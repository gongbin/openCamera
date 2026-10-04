# 许可

本仓库按资产类型分别许可。各许可证全文在 [`LICENSES/`](LICENSES/) 目录下。

| 资产 | 路径 | 许可证 |
|---|---|---|
| 硬件设计：原理图、网表、PCB、BOM、接口定义、硬件文档 | `hardware/` | [CERN-OHL-W-2.0](LICENSES/CERN-OHL-W-2.0.txt) |
| 结构设计：CAD、图纸、打印参数 | `mechanical/` | [CERN-OHL-W-2.0](LICENSES/CERN-OHL-W-2.0.txt) |
| 自研固件、工具、App、网页 | `firmware/`（内核部分除外）、`tools/`、`app/`、`web/` | [Apache-2.0](LICENSES/Apache-2.0.txt) |
| 协议定义、场景档、技能 | `proto/`、`profiles/`、`skills/` | [Apache-2.0](LICENSES/Apache-2.0.txt) |
| 内核补丁与驱动 | `firmware/soc/` 下的内核相关部分 | GPL-2.0-only（随 Linux 内核） |
| 其他文档、标定数据、测试素材 | `docs/`、`calibration/`、`test/` 中的素材 | [CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0.txt) |

说明：

- 文件头部带有 `SPDX-License-Identifier` 的，以文件头为准。
- 厂商的闭源组件（ISP 库、NPU 运行时、Wi‑Fi 固件、调校工具）不在本仓库分发，也不受上述许可证约束。
- 模型权重不在本仓库分发；每个模型的许可证在 `models/` 中单独记录。

Copyright © 2026 OAC-1 项目贡献者。
