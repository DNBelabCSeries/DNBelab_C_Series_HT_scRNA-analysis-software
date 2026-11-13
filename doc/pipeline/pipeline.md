# 分析流程

从输入准备、参考库构建到结果交付，按实验类型选择流程。

| 模块 | 主要步骤 | 流程文档 |
| :--- | :--- | :--- |
| RNA | cDNA/oligo 质控 → 比对与计数 → 细胞识别 → 聚类与报告 | [RNA 流程](scRNA.md) |
| ATAC | 片段处理 → 微珠合并 → 峰检测与矩阵 → 细胞质控与聚类 | [ATAC 流程](scATAC.md) |
| V(D)J | 质控 → 组装 → 注释与过滤 → 克隆型与报告 | [VDJ 流程](scVDJ.md) |
| 多组学 (Multi) | CSV 配置 → 模态调度 → 结果归档 → 组合报告 | [Multi 流程](multi.md) |
| C6 多样本 | 共享文库 → Sample Barcode 解复用 → 逐样本独立细胞识别与交付 | [C6 流程](c6.md) |

## 流程选择建议

- **独立单组学**：独立测序的文库直接进入对应单组学流程（`scRNA`、`scATAC` 或 `scVDJ`）。VDJ 可选使用 RNA `singlecell.csv` 进行微珠映射和细胞过滤；省略 `--beadstrans` 时自动启用 `keep_all_cells`。
- **普通多组学 (Multi)**：同一批样本同时测了 RNA、ATAC 或 VDJ，使用单个 CSV 配置文件统一调度各模块并生成组合报告。
- **C6 多样本 RNA**：使用 Sample Barcode 混合建库的测序数据，通过含 `[samples]` 的配置文件自动完成拆分、逐样本独立定量与报告交付。
