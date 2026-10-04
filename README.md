# OAC-1 开源感知相机

一个带同步运动数据和端侧 AI 的开源影像核心。装进不同的外壳和底座，就是手持运动相机、车载记录仪、无人机相机或佩戴相机；对外提供统一协议，人、脚本和 AI Agent 都能使用。

**当前阶段：可行性验证。** 还没有可以打样的整机 PCB。

## 目录

| 目录 | 内容 | 状态 |
|---|---|---|
| `hardware/` | 接口定义、电源树、P0 伴随板原理图与 BOM | 进行中，见 [hardware/README.md](hardware/README.md) |
| `tools/oacnet/` | 原理图即代码的小工具（纯 Python 标准库） | 可用 |
| `mechanical/` `firmware/` `proto/` `profiles/` `skills/` `app/` | 结构、固件、协议、场景档、技能、App | 未开始 |

## 许可

按资产类型分别许可，详见 [LICENSE.md](LICENSE.md)。
