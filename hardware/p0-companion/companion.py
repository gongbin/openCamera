#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-W-2.0
"""OAC P0 伴随板（oac-p0-companion）原理图。

用途见同目录 README.md。运行：
    python3 companion.py
会做规则检查，并在 out/ 下生成 KiCad 网表、BOM、引脚核对清单和可读网表。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools", "oacnet"))

from oacnet import Circuit, NC  # noqa: E402
import parts as P  # noqa: E402

ckt = Circuit("oac-p0-companion")
GND = "GND"


def R(value, a, b, pdef=P.R0402, dnp=False):
    return ckt.add(pdef, {1: a, 2: b}, value, dnp)


def C(value, a, b=GND, pdef=P.C0402):
    return ckt.add(pdef, {1: a, 2: b}, value)


def TP(net):
    ckt.allow_single(net)
    return ckt.add(P.TP, {1: net}, net)


def ESD(net):
    return ckt.add(P.ESD, {1: net, 2: GND}, "ESD")


# 由连接器或板外提供的电源，以及经无源器件得到的电源轨
ckt.power(GND, "VBUS_USB", "LINK_VEXT_5V", "VBUS_IN", "VBAT", "VBAT_CONN",
          "VSYS", "AON_3V0", "VIO_SOC")

# ───────────────────────── 1. 电源输入 ─────────────────────────
# USB-C 只取电；数据仍走开发板自己的 USB 口。
ckt.add(P.USBC_PWR, {"VBUS": "VBUS_USB", "GND": GND, "CC1": "USB_CC1",
                     "CC2": "USB_CC2", "SHIELD": GND})
R("5.1k", "USB_CC1", GND)
R("5.1k", "USB_CC2", GND)
ckt.add(P.TVS, {"K": "VBUS_USB", "A": GND}, "5V TVS")
ckt.add(P.TVS, {"K": "LINK_VEXT_5V", "A": GND}, "5V TVS")
# 两路 5 V 用肖特基二极管合路。P0 够用；EVT 换成理想二极管以减小压降。
ckt.add(P.SCHOTTKY, {"A": "VBUS_USB", "K": "VBUS_IN"}, "3A 肖特基")
ckt.add(P.SCHOTTKY, {"A": "LINK_VEXT_5V", "K": "VBUS_IN"}, "3A 肖特基")

# ───────────────────────── 2. 充电与电源路径 ─────────────────────────
ckt.add(P.BQ25895, {
    "VBUS": "VBUS_IN", "PMID": "CHG_PMID", "SW": "CHG_SW", "BTST": "CHG_BTST",
    "REGN": "CHG_REGN", "SYS": "VSYS", "BAT": "VBAT", "PGND": GND, "EP": GND,
    "D+": "CHG_DPDM", "D-": "CHG_DPDM",      # 短接：识别为专用充电口
    "SCL": "I2C_SCL", "SDA": "I2C_SDA", "INT": "CHG_INT_N", "STAT": "CHG_STAT",
    "OTG": GND,                               # 不使用升压输出
    "CE_N": "CHG_CE_N", "ILIM": "CHG_ILIM", "TS": "CHG_TS",
    "QON_N": "CHG_QON_N", "DSEL": NC})
C("1u 25V", "VBUS_IN", pdef=P.C0603)
C("10u 25V", "CHG_PMID", pdef=P.C0805)
C("47n", "CHG_BTST", "CHG_SW")
C("4.7u", "CHG_REGN", pdef=P.C0603)
ckt.add(P.L_PWR, {1: "CHG_SW", 2: "VSYS"}, "2.2uH")
C("10u", "VSYS", pdef=P.C0805)
C("10u", "VSYS", pdef=P.C0805)
C("10u", "VBAT", pdef=P.C0805)
R("200R 1%", "CHG_ILIM", GND)                 # 输入限流约 2 A（系数待对照数据手册）
R("10k", "CHG_CE_N", GND)                     # 默认允许充电
R("10k", "CHG_INT_N", "AON_3V0")
R("2.2k", "VSYS", "CHG_STAT_LED")
ckt.add(P.LED, {"A": "CHG_STAT_LED", "K": "CHG_STAT"}, "充电状态")
ckt.add(P.BUTTON, {1: "CHG_QON_N", 2: GND}, "QON（出船运模式 / 复位）")
# 电池温度：10 k NTC 在电池包内。阻值取自数据手册的典型网络，待核对。
R("5.23k 1%", "CHG_REGN", "CHG_TS")
R("30.1k 1%", "CHG_TS", GND)
R("0R", "CHG_TS", "BAT_TS")
ckt.add(P.SOLDER_JP, {1: "BAT_TS", 2: "BAT_TS_FIX"}, "无 NTC 电池时短接")
R("10k 1%", "BAT_TS_FIX", GND)

# ───────────────────────── 3. 电池触点与电量计 ─────────────────────────
ckt.add(P.BAT_CONTACT, {"BAT+": "VBAT_CONN", "BAT-": GND, "TS": "BAT_TS",
                        "ID": "BAT_ID_RAW"})
R("20m 1%", "VBAT_CONN", "VBAT", pdef=P.R0805)        # 电池电流检流，配测试点
R("1k", "BAT_ID_RAW", "BAT_ID")
R("100k 1%", "BAT_ID", "AON_3V0")                     # 与电池 ID 电阻分压，MCU 用 ADC 读
ESD("BAT_ID_RAW")
ckt.add(P.MAX17048, {"CELL": "VBAT", "VDD": "VBAT", "CTG": GND, "QSTRT": GND,
                     "GND": GND, "EP": GND, "ALRT_N": "GAUGE_ALRT_N",
                     "SCL": "I2C_SCL", "SDA": "I2C_SDA"})
C("100n", "VBAT")
R("10k", "GAUGE_ALRT_N", "AON_3V0")
R("4.7k", "I2C_SCL", "AON_3V0")
R("4.7k", "I2C_SDA", "AON_3V0")

# ───────────────────────── 4. 常开电源轨 ─────────────────────────
ckt.add(P.TPS7A02, {"IN": "VSYS", "EN": "VSYS", "GND": GND, "NC": NC,
                    "OUT": "AON_3V0_LDO"})
C("1u", "VSYS")
C("1u", "AON_3V0_LDO")
ckt.add(P.JUMPER, {1: "AON_3V0_LDO", 2: "AON_3V0"}, "常开域电流测量（串 PPK2）")
C("1u", "AON_3V0")

# ───────────────────────── 5. 掉电保持与掉电检测 ─────────────────────────
ckt.add(P.JUMPER, {1: "VSYS", 2: "VSYS_SC"}, "接入超级电容")
R("2.2R", "VSYS_SC", "VSYS_HOLD", pdef=P.R0805)       # 限制充电浪涌
ckt.add(P.SCHOTTKY, {"A": "VSYS_HOLD", "K": "VSYS_SC"}, "3A 肖特基")  # 放电旁路
ckt.add(P.SUPERCAP, {1: "VSYS_HOLD", 2: GND}, "0.47F 5.5V")
# 比较器监视电池电压：VBAT < 约 3.25 V 时 PFAIL_N 拉低。
ckt.add(P.TLV3011, {"V+": "AON_3V0", "V-": GND, "IN+": "PF_DIV", "IN-": "PF_REF",
                    "REF": "PF_REF", "OUT": "PFAIL_N"})
R("1M 1%", "VBAT", "PF_DIV")
R("619k 1%", "PF_DIV", GND)
R("10M", "PFAIL_N", "PF_DIV")                         # 迟滞
C("100n", "AON_3V0")
R("100k", "PFAIL_N", "AON_3V0")
# 电池仓门开关：关门 = 闭合到地；开门 = 上拉为高。
ckt.add(P.JST2, {1: "BAT_DOOR_N", 2: GND}, "仓门微动开关")
R("1M", "BAT_DOOR_N", "AON_3V0")
# 送往 SoC 的两根信号做电平转换（SoC 侧电平为 VIO_SOC，SoC 断电时不倒灌）
for aon, soc in (("PFAIL_N", "PFAIL_N_SOC"), ("BAT_DOOR_N", "BAT_DOOR_N_SOC")):
    ckt.add(P.NMOS, {"G": "VIO_SOC", "S": soc, "D": aon}, "BSS138")
    R("10k", soc, "VIO_SOC")

# ───────────────────────── 6. 系统供电输出 ─────────────────────────
R("20m 1%", "VSYS", "VSYS_OUT", pdef=P.R0805)         # 整机电流检流，配测试点
ckt.add(P.TERMINAL2, {1: "VSYS_OUT", 2: GND}, "VSYS 输出到开发板")

# ───────────────────────── 7. 常开域传感器 ─────────────────────────
ckt.add(P.LIS2DW12, {"VDD": "AON_3V0", "VDD_IO": "AON_3V0", "GND": GND, "RES": GND,
                     "CS": "AON_3V0", "SA0": GND, "NC": NC,
                     "SCL": "I2C_SCL", "SDA": "I2C_SDA",
                     "INT1": "ACC_INT1", "INT2": "ACC_INT2"})
C("100n", "AON_3V0")
C("100n", "AON_3V0")
ckt.add(P.T5838, {"VDD": "AON_3V0", "GND": GND, "SELECT": GND, "CLK": "MIC_CLK",
                  "DATA": "MIC_DATA", "WAKE": "MIC_WAKE", "THSEL": "MIC_THSEL"})
C("100n", "AON_3V0")
# 振动马达
ckt.add(P.NMOS, {"G": "HAPTIC_G", "S": GND, "D": "MOTOR_N"}, "BSS138")
R("100R", "HAPTIC_EN", "HAPTIC_G")
R("100k", "HAPTIC_G", GND)
ckt.add(P.MOTOR, {"+": "VSYS", "-": "MOTOR_N"})
ckt.add(P.DIODE_SM, {"K": "VSYS", "A": "MOTOR_N"}, "续流")

# ───────────────────────── 8. 主 IMU（主电源域，由 SoC 侧供电）─────────────────────────
ckt.add(P.ICM42688, {"VDD": "VIO_SOC", "VDDIO": "VIO_SOC", "GND": GND,
                     "RESV_GND": GND, "RESV_NC": NC,
                     "AP_CS": "IMU_CS", "AP_SCLK": "IMU_SCLK",
                     "AP_SDI": "IMU_MOSI", "AP_SDO": "IMU_MISO",
                     "INT1": "IMU_INT1", "INT2_FSYNC": "IMU_FSYNC"})
C("100n", "VIO_SOC")
C("2.2u", "VIO_SOC")
C("10n", "VIO_SOC")
R("100R", "XVS_IN", "IMU_FSYNC")              # 传感器帧同步 → IMU FSYNC
R("100k", "IMU_FSYNC", GND)

# ───────────────────────── 9. OAC Link ─────────────────────────
ckt.add(P.OAC_LINK, {"VEXT_5V": "LINK_VEXT_5V", "GND": GND,
                     "USB_DP": "LINK_USB_DP", "USB_DM": "LINK_USB_DM",
                     "UART_TX": "LINK_UART_TX", "UART_RX": "LINK_UART_RX",
                     "TRIG_IN": "LINK_TRIG_IN", "SYNC_OUT": "LINK_SYNC_OUT",
                     "DOCK_ID": "LINK_DOCK_ID"})
R("1k", "LINK_TRIG_IN", "LINK_TRIG_IN_SOC")
R("100k", "LINK_TRIG_IN_SOC", GND)
R("100R", "LINK_SYNC_OUT_SOC", "LINK_SYNC_OUT")
R("100R", "LINK_DOCK_ID", "DOCK_ID")
R("2.2k", "DOCK_ID", "AON_3V0")               # 1-Wire 上拉
for n in ("LINK_USB_DP", "LINK_USB_DM", "LINK_UART_TX", "LINK_UART_RX",
          "LINK_TRIG_IN", "LINK_SYNC_OUT", "LINK_DOCK_ID"):
    ESD(n)

# ───────────────────────── 10. 录制指示灯联动演示 ─────────────────────────
# 传感器模拟供电一上电，LED 就亮；不经过任何固件。
ckt.add(P.NPN, {"B": "REC_B", "E": GND, "C": "REC_K"}, "MMBT3904")
R("10k", "SENSOR_AVDD", "REC_B")
R("100k", "REC_B", GND)
R("1k", "VSYS", "REC_A")
ckt.add(P.LED, {"A": "REC_A", "K": "REC_K"}, "录制指示（红）")

# ───────────────────────── 11. 板间连接 ─────────────────────────
J_MCU = P.header("MCU 排针（接 nRF54L15 开发板）", [
    "AON_3V0", "GND", "I2C_SCL", "I2C_SDA", "CHG_INT_N", "CHG_CE_N",
    "CHG_QON_N", "GAUGE_ALRT_N", "ACC_INT1", "ACC_INT2", "MIC_CLK", "MIC_DATA",
    "MIC_WAKE", "MIC_THSEL", "HAPTIC_EN", "DOCK_ID", "BAT_ID", "BAT_DOOR_N",
    "PFAIL_N", "GND"])
ckt.add(J_MCU, {s: s for s in set(n for _, n, _ in J_MCU.pins)})

J_SOC = P.header("SoC 排针（接 RV1126B 开发板）", [
    "VIO_SOC", "GND", "IMU_SCLK", "IMU_MOSI", "IMU_MISO", "IMU_CS",
    "IMU_INT1", "XVS_IN", "LINK_USB_DP", "LINK_USB_DM", "LINK_UART_TX",
    "LINK_UART_RX", "LINK_TRIG_IN_SOC", "LINK_SYNC_OUT_SOC", "PFAIL_N_SOC",
    "BAT_DOOR_N_SOC", "SENSOR_AVDD", "GND", "GND", "GND"])
ckt.add(J_SOC, {s: s for s in set(n for _, n, _ in J_SOC.pins)})

# ───────────────────────── 12. 测试点 ─────────────────────────
for n in ("VBUS_IN", "VBAT_CONN", "VBAT", "VSYS", "VSYS_OUT", "VSYS_HOLD",
          "AON_3V0", "PFAIL_N", "IMU_FSYNC", GND, GND):
    ckt.add(P.TP, {1: n}, n)


def main():
    errors, warnings = ckt.check()
    for w in warnings:
        print("警告: " + w)
    for e in errors:
        print("错误: " + e)
    out = os.path.join(HERE, "out")
    ckt.export_kicad(os.path.join(out, "companion.net"))
    ckt.export_bom(os.path.join(out, "bom.csv"))
    ckt.export_pin_review(os.path.join(out, "pin-review.csv"))
    ckt.export_markdown(os.path.join(out, "netlist.md"))
    print("器件 %d 个，网络 %d 个，错误 %d，警告 %d"
          % (len(ckt.parts), len(ckt.nets()), len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
