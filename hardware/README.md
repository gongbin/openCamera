# 硬件

## 现在有什么

| 路径 | 内容 |
|---|---|
| [interfaces.md](interfaces.md) | Core 对外的三个电气接口：OAC Link、电池触点、Shell 连接器 |
| [power-tree.md](power-tree.md) | 电源树、各电源轨预算、掉电保持计算 |
| [p0-companion/](p0-companion/) | **P0 伴随板**：原理图（代码形式）、KiCad 网表、BOM、PCB 设计约束 |

## 为什么先做伴随板，而不是 Core 主板

Core 主板现在画不了，原因有三个：

1. **核心板还没选定。** EVT 用 RV1126B 核心板 + 自研载板，载板原理图取决于具体核心板的引脚定义。
2. **P0 的结论会改变主板。** 传感器是 12MP 4:3 还是 IMX415、电池触点怎么排、超级电容多大，都要等 P0 实测。
3. **电池仓尺寸要等拆解实测。**

伴随板把系统里**与 SoC 无关**的部分先做出来：充电与电源路径、电量计、常开电源域、掉电保持、常开传感器、主 IMU 和 OAC Link。它接在 RV1126B 开发板和 nRF54L15 开发板之间，用于验证整机功耗、IMU 同步、标准电池、掉电保持和常开域功耗。这部分电路验证后会原样搬进 Core 主板。

## 没有的东西

- **没有图形化原理图（`.kicad_sch`）和 PCB 布局（`.kicad_pcb`）。** 原理图以 Python 代码的形式存在，可生成 KiCad 网表导入 Pcbnew。布局布线需要在 KiCad 里人工完成，约束见 [p0-companion/pcb-constraints.md](p0-companion/pcb-constraints.md)。
- **器件引脚编号未对照数据手册。** 清单见 `p0-companion/out/pin-review.csv`，全部核对完之前不要打样。
- 以 `OAC:` 开头的封装需要自己建。

## 下一步

1. 选定 RV1126B 核心板 / 开发板型号，拿到引脚定义和参考原理图。
2. 逐项核对 `pin-review.csv`，建缺失的封装。
3. 在 KiCad 里导入网表，按约束完成伴随板布局，打样。
4. P0 结果出来后开始 Core 主板原理图。
