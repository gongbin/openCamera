# SPDX-License-Identifier: CERN-OHL-W-2.0
"""P0 伴随板用到的器件定义。

重要：所有 IC 的引脚编号都是凭资料印象录入的，**尚未逐一对照数据手册**
（verified=False）。在画 PCB 之前必须逐个核对，核对后把 verified 改为 True。
封装名以 "OAC:" 开头的表示 KiCad 标准库里没有，需要自己建。
"""
from oacnet import (PartDef, PWR_IN, PWR_OUT, IN, OUT, BIDIR, PASSIVE, OD, NOCONN)

P = PASSIVE


def _two(name, prefix, fp, **kw):
    return PartDef(name, prefix, [(1, "1", P), (2, "2", P)], footprint=fp, **kw)


# ---- 无源与分立 ----
R0402 = _two("电阻", "R", "Resistor_SMD:R_0402_1005Metric")
R0805 = _two("电阻", "R", "Resistor_SMD:R_0805_2012Metric")
C0402 = _two("电容", "C", "Capacitor_SMD:C_0402_1005Metric")
C0603 = _two("电容", "C", "Capacitor_SMD:C_0603_1608Metric")
C0805 = _two("电容", "C", "Capacitor_SMD:C_0805_2012Metric")
L_PWR = _two("功率电感", "L", "OAC:L_4x4mm", desc="2.2 µH，Isat ≥ 4 A，DCR ≤ 40 mΩ")
SUPERCAP = _two("超级电容", "C", "OAC:Supercap_21x14mm", mpn="DMF3Z5R5H474M3DTA0", mfr="Murata",
                desc="0.47 F / 5.5 V，低 ESR（< 0.1 Ω）", note="型号与尺寸待核实")
LED = PartDef("LED", "D", [(1, "K", P), (2, "A", P)], footprint="LED_SMD:LED_0603_1608Metric")
SCHOTTKY = PartDef("肖特基二极管", "D", [(1, "K", P), (2, "A", P)], footprint="Diode_SMD:D_SMA",
                   desc="≥ 3 A / 30 V，低 Vf")
DIODE_SM = PartDef("开关二极管", "D", [(1, "K", P), (2, "A", P)], footprint="Diode_SMD:D_SOD-323")
TVS = PartDef("TVS", "D", [(1, "K", P), (2, "A", P)], footprint="Diode_SMD:D_SOD-323",
              desc="5 V 单向 TVS")
ESD = _two("ESD 二极管", "D", "Diode_SMD:D_0402_1005Metric", desc="低电容双向 ESD")
NMOS = PartDef("N-MOSFET", "Q", [(1, "G", IN), (2, "S", P), (3, "D", P)],
               footprint="Package_TO_SOT_SMD:SOT-23", desc="逻辑电平，Vgs(th) < 1.5 V（如 BSS138 类）")
NPN = PartDef("NPN", "Q", [(1, "B", IN), (2, "E", P), (3, "C", P)],
              footprint="Package_TO_SOT_SMD:SOT-23")
TP = PartDef("测试点", "TP", [(1, "1", P)], footprint="TestPoint:TestPoint_Pad_D1.0mm")
JUMPER = _two("跳线", "JP", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
SOLDER_JP = _two("焊接跳线", "JP", "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm")
BUTTON = _two("轻触开关", "SW", "OAC:SW_Tact_SMD")
MOTOR = PartDef("ERM 振动马达焊盘", "M", [(1, "+", P), (2, "-", P)], footprint="OAC:Pads_2x1.5mm")

# ---- IC ----
BQ25895 = PartDef(
    "BQ25895", "U", mpn="BQ25895RTWR", mfr="TI",
    footprint="Package_DFN_QFN:WQFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
    desc="1S 充电 + 电源路径，I2C",
    pins=[(1, "VBUS", PWR_IN), (2, "D+", BIDIR), (3, "D-", BIDIR), (4, "STAT", OD),
          (5, "SCL", IN), (6, "SDA", BIDIR), (7, "INT", OD), (8, "OTG", IN),
          (9, "CE_N", IN), (10, "ILIM", P), (11, "TS", P), (12, "QON_N", P),
          (13, "BAT", P), (14, "BAT", P), (15, "SYS", PWR_OUT), (16, "SYS", P),
          (17, "PGND", PWR_IN), (18, "PGND", PWR_IN), (19, "SW", P), (20, "SW", P),
          (21, "BTST", P), (22, "REGN", PWR_OUT), (23, "PMID", P), (24, "DSEL", OUT),
          (25, "EP", PWR_IN)])

MAX17048 = PartDef(
    "MAX17048", "U", mpn="MAX17048G+T10", mfr="Analog Devices",
    footprint="OAC:TDFN-8-1EP_2x2mm_P0.5mm", desc="电压型电量计，免检流电阻，免学习",
    pins=[(1, "CTG", P), (2, "CELL", P), (3, "VDD", PWR_IN), (4, "GND", PWR_IN),
          (5, "ALRT_N", OD), (6, "QSTRT", IN), (7, "SCL", IN), (8, "SDA", BIDIR),
          (9, "EP", PWR_IN)])

TPS7A02 = PartDef(
    "TPS7A02 3.0V", "U", mpn="TPS7A0230DBVR", mfr="TI",
    footprint="Package_TO_SOT_SMD:SOT-23-5", desc="超低静态电流 LDO，3.0 V / 200 mA",
    pins=[(1, "IN", PWR_IN), (2, "GND", PWR_IN), (3, "EN", IN), (4, "NC", NOCONN),
          (5, "OUT", PWR_OUT)])

TLV3011 = PartDef(
    "TLV3011", "U", mpn="TLV3011AIDBVR", mfr="TI",
    footprint="Package_TO_SOT_SMD:SOT-23-6", desc="带 1.242 V 基准的微功耗比较器，开漏输出",
    pins=[(1, "OUT", OD), (2, "V-", PWR_IN), (3, "IN+", IN), (4, "IN-", IN),
          (5, "REF", OUT), (6, "V+", PWR_IN)])

ICM42688 = PartDef(
    "ICM-42688-P", "U", mpn="ICM-42688-P", mfr="TDK InvenSense",
    footprint="OAC:LGA-14_2.5x3mm_P0.5mm", desc="6 轴 IMU，SPI，FSYNC",
    note="RESV 引脚的处理方式（接地 / 悬空）待对照数据手册",
    pins=[(1, "AP_SDO", OUT), (2, "RESV_NC", NOCONN), (3, "RESV_NC", NOCONN),
          (4, "INT1", OUT), (5, "VDDIO", PWR_IN), (6, "GND", PWR_IN),
          (7, "RESV_GND", P), (8, "VDD", PWR_IN), (9, "INT2_FSYNC", IN),
          (10, "RESV_NC", NOCONN), (11, "RESV_NC", NOCONN), (12, "AP_CS", IN),
          (13, "AP_SCLK", IN), (14, "AP_SDI", IN)])

LIS2DW12 = PartDef(
    "LIS2DW12", "U", mpn="LIS2DW12TR", mfr="ST",
    footprint="OAC:LGA-12_2x2mm_P0.5mm", desc="低功耗 3 轴加速度计，I2C",
    pins=[(1, "SCL", IN), (2, "CS", IN), (3, "SA0", IN), (4, "SDA", BIDIR),
          (5, "NC", NOCONN), (6, "GND", PWR_IN), (7, "RES", P), (8, "GND", PWR_IN),
          (9, "VDD", PWR_IN), (10, "VDD_IO", PWR_IN), (11, "INT2", OUT), (12, "INT1", OUT)])

T5838 = PartDef(
    "T5838", "MK", mpn="MMICT5838-00-012", mfr="TDK InvenSense",
    footprint="OAC:MIC_T5838", desc="带声学活动检测的 PDM 麦克风",
    note="引脚编号是占位值，必须对照数据手册重填；料号待核实",
    pins=[(1, "DATA", OUT), (2, "SELECT", IN), (3, "CLK", IN), (4, "VDD", PWR_IN),
          (5, "GND", PWR_IN), (6, "WAKE", OUT), (7, "THSEL", IN)])

# ---- 连接器 ----
USBC_PWR = PartDef(
    "USB-C 座（仅供电）", "J", mpn="USB4125-GF-A", mfr="GCT",
    footprint="OAC:USB_C_Power_6P", note="料号待核实",
    pins=[("A9", "VBUS", P), ("B9", "VBUS", P), ("A12", "GND", P), ("B12", "GND", P),
          ("A5", "CC1", P), ("B5", "CC2", P), ("S1", "SHIELD", P)])

BAT_CONTACT = PartDef(
    "电池触点（4 位）", "J", footprint="OAC:Battery_Contact_4P",
    note="触点顺序和间距等标准电池拆解实测后再定",
    pins=[(1, "BAT+", P), (2, "TS", P), (3, "ID", P), (4, "BAT-", P)])

OAC_LINK = PartDef(
    "OAC Link 10 针触点", "J", footprint="OAC:OAC_Link_10P",
    note="焊盘图形待结构设计确定",
    pins=[(1, "VEXT_5V", P), (2, "GND", P), (3, "USB_DP", P), (4, "USB_DM", P),
          (5, "UART_TX", P), (6, "UART_RX", P), (7, "TRIG_IN", P), (8, "SYNC_OUT", P),
          (9, "DOCK_ID", P), (10, "GND", P)])


def header(name, signals):
    """按信号名定义一个 2xN 排针；引脚编号按列表顺序从 1 开始。"""
    n = len(signals)
    assert n % 2 == 0
    fp = "Connector_PinHeader_2.54mm:PinHeader_2x%02d_P2.54mm_Vertical" % (n // 2)
    return PartDef(name, "J", [(i + 1, s, P) for i, s in enumerate(signals)],
                   footprint=fp, verified=True)


TERMINAL2 = PartDef("2 位接线端子", "J", [(1, "1", P), (2, "2", P)],
                    footprint="TerminalBlock:TerminalBlock_bornier-2_P5.08mm", verified=True)
JST2 = PartDef("JST-PH 2 位", "J", [(1, "1", P), (2, "2", P)],
               footprint="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", verified=True)
