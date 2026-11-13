# 从 3.1 升级到 3.2

本文档总结了 DNBelab C Series™ HT 单细胞分析软件（dnbc4tools）从 3.1 升级至 3.2 的主要新功能、算法优化与输出文件变更。顶部版本切换菜单可随时查阅 3.1 归档文档。

---

## 核心新特性：C6 多样本 RNA 分析

3.2 开发版本新增 **C6 多样本 RNA 分析**，支持在单个物理文库中混合测序并按 Sample Barcode 拆分样本：

- **配置与运行**：在 `multi run` 配置文件中使用 `[samples]` 区块声明样本名称与对应的 Sample Barcode 序列，软件会自动识别并启用 C6 多样本分析流程，无需手动指定化学体系参数。
- **全局与各样本矩阵**：
    - 针对总文库（输出根目录）以及每个拆分后的样本（`per_sample_outs/<sample>/` 目录下），均分别生成完整的基因表达矩阵信息，同时提供 MEX 文本目录、标准 H5 格式与 H5AD 格式；
    - 为各样本生成交互式 HTML 质控与聚类分析报告（`per_sample_outs/<sample>/<sample>_scRNA_report.html`）。
- **按样本拆分输出比对 BAM 文件**：
    - 默认会为每个样本输出比对 BAM 文件（`per_sample_outs/<sample>/<sample>_alignments.bam` 及索引文件），方便针对特定样本进行 IGV 可视化或突变分析；
    - 当 `[rna] no_bam` 为 `false`（默认）时，未能明确分配给任何样本 Sample Barcode 的 reads 归集输出为 `unassigned_alignments.bam`。设置 `no_bam,true` 时，不生成任何 BAM 及其索引，包括逐样本、未分配和 Oligo BAM。
- **双 UMI 独立校正**：针对 C6 双 UMI 文库结构，分别对两段 UMI 进行独立纠错与去重，用于后续分子计数。

---

## 算法更新与指标说明

### 1. 单细胞 RNA (scRNA)
- **细胞内跨基因同 UMI 冲突过滤优化**：
    - 3.1 版本已支持该机制，但存在边界判定缺陷；3.2 修复了相关缺陷并优化了冲突裁决逻辑：当同一细胞内同一个 UMI 比对到多个不同基因时，择优保留 read 数最高的主基因；若多个基因 read 数相同无法唯一判定，则剔除该歧义分子，不计入基因表达量。
- **Cell Calling 自动预测增加上下限保护**：
    - 3.1 的自动细胞预测没有设置数量上下限；3.2 增加了自动预测细胞数目的上下限保护，用于约束自动估计的细胞数；实际细胞识别结果仍需结合样本质控指标评估。
- **Oligo R2 过滤优化减少数据丢弃**：
    - 更新 Oligo Read 2 中条形码与结构序列的质控、纠错和过滤规则。

### 2. 双物种区分算法升级 (Mixed-Species Classification)
- **双向背景预测带拟合模型**：
    - 更新双物种分类模型，以独立的方向性连续背景预测带模型（Bidirectional background prediction bands）取代旧版的固定硬阈值（如 1,000 UMI / 90% 纯度规则及简单分位数过滤）；
    - 引入两阶段稳健 Huber 回归分别独立评估宿主与次级物种间的背景泄露分布与方差，用于评估细胞的物种归属；
    - 在 ATAC 模块中引入微珠感知（bead-aware）背景建模，联合考虑合并 bead 数（N1, N2...）与染色质开放深度，用于区分跨物种多联体（Multiplet）与高测序深度单细胞。

### 3. 单细胞 ATAC (scATAC)
- **Peak 与矩阵计数口径采用 cutsite**：
    - **什么是 cutsite？** 在 ATAC-seq 实验中，Tn5 转座酶结合开放染色质并在 DNA 双链上切割插入测序接头，切割时会在双链两端产生 9 bp 的交错错位。**cutsite 模式即统计经 9 bp 偏移修正后的 Tn5 实际插入切割位点端点**。cutsite 统计切割位点端点，fragment 统计测序片段，两者计数口径不同。
    - **指标说明**：Peak 召回与表达矩阵计数默认采用 cutsite 统计；而 FRIP（Fraction of Reads in Peaks）、TSS 富集比例以及 Cell Calling 仍严格基于去重后的唯一 fragment 统计。

### 4. 单细胞 V(D)J (scVDJ)
- 更新链配对算法与全长重叠群（Full-length Contigs）拼接逻辑。
- 更新多线程抽样的确定性处理；跨运行比较时，应保持输入、参数及软件环境一致。

---

## 3.1 用户需要适配的变更

<a id="输出目录与格式变更"></a>

下表仅比较 3.1 已有流程的输出与行为变更。C6 是 3.2 新增能力，没有对应的 3.1 输出结构：逐样本结果位于 `outs/rna/per_sample_outs/<sample>/`，全局矩阵位于 `outs/rna/`。C6 新增的明细表为 `outs/rna/singlecell.csv.gz`，读取时需支持 gzip，并通过 `is_cell_barcode` 筛选有效细胞。

### 输出目录与格式变更

| 变更项 | 3.1 旧版 | 3.2 新版 | 适配说明 |
| :--- | :--- | :--- | :--- |
| **RNA 矩阵目录** | `raw_matrix/`<br>`filter_matrix/` | `raw_feature_bc_matrix/`<br>`filtered_feature_bc_matrix/` | 目录结构与标准格式保持一致；同级新增压缩 `.h5` 矩阵，可使用单文件读取。 |
| **ATAC 矩阵目录** | `raw_peak_matrix/`<br>`filter_peak_matrix/` | `raw_peak_bc_matrix/`<br>`filtered_peak_bc_matrix/` | 目录命名规范化；同级新增压缩 `.h5` 矩阵。 |
| **ATAC 文本矩阵** | `matrix.mtx.gz` 用 `\t` 分隔 | `matrix.mtx.gz` 用**单空格**分隔 | 自定义解析脚本改用 `line.split()`（匹配任意空白字符）或标准 MatrixMarket 库。 |
| **批量分析脚本** | 写入分析输出目录 | **仅在当前终端工作目录**生成 `.sh` | 在当前目录执行生成的脚本；`--outdir` 仅指定结果交付目录；同名脚本不覆盖。 |
