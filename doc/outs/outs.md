# 输出与报告

> **输出范围**：目录树描述常规完成运行的结果；可选文件取决于启用模块与阶段完成状态。下文质量参考区间是判读建议，不是软件内置的通过/失败规则，应以本次配置阈值和报告状态为准。

按模块查找输出目录、文件字段与网页报告指标。独立流程的分析结果位于 `<outdir>/<name>/outs/`；多组学 (Multi) 与 C6 多样本流程在输出目录下按模态与样本分层归档。

| 模块 | 主要交付内容 | 详细文档 |
| :--- | :--- | :--- |
| **scRNA** | 基因表达矩阵 (MEX / H5 / H5AD)、细胞表、聚类分析与 HTML 质控报告 | [scRNA 输出详解](scRNA.md) |
| **scATAC** | 染色质开放 Peak 矩阵、Tabix 片段文件、细胞质控与 HTML 质控报告 | [scATAC 输出详解](scATAC.md) |
| **scVDJ** | TCR / BCR 重叠群序列、全长功能注释、克隆型统计与 HTML 质控报告 | [scVDJ 输出详解](scVDJ.md) |
| **多组学 (Multi)** | 跨组学联合汇总报告、解耦归档各模态结果目录（RNA / ATAC / VDJ） | [多组学输出详解](multi.md) |
| **C6 多样本** | 全局合并表达矩阵、`singlecell.csv.gz`、各样本矩阵、BAM（`[rna] no_bam` 为 `false` 时生成）与独立报告 | [C6 多样本输出详解](c6.md) |

---

## 通用输出规范与交付架构

dnbc4tools 在所有组学流程中遵循统一的数据交付规范与目录组织标准：

### 1. 标准输出目录层级
- **独立单组学流程**：统一写入 `<outdir>/<name>/outs/`，根目录下包含最终交付的表达矩阵、质控汇总表、BAM（若启用）与 HTML 交互式报告。
- **多组学流程 (Multi)**：在 `outs/` 根目录交付跨组学联合报告 `<name>_multi_report.html`，并将各组学解耦归档于独立的子目录中（如 `rna/`、`atac/`、`vdj-t/`、`vdj-b/`），各子目录完全兼容单组学规范。
- **C6 多样本流程**：组合报告为 `outs/<name>_multi_report.html`；全局矩阵与 `singlecell.csv.gz` 位于 `outs/rna/`，各样本输出位于 `outs/rna/per_sample_outs/<sample>/`。

### 2. 特征与表达矩阵格式规范

所有单细胞定量矩阵均同步提供主流格式，可按下游工具选择相应格式：

- **MEX 矩阵**：RNA 包含 `matrix.mtx.gz`、`barcodes.tsv.gz`、`features.tsv.gz`；ATAC 使用 `peaks.bed.gz`，不能假设存在 RNA 的 `features.tsv.gz`。ATAC 应分别读取矩阵、条形码和峰坐标，示例见[结果读取指南](../io.md)。
- **H5 压缩格式**（`*.h5`）：单文件封装稀疏矩阵与元数据，R 语言可通过 `Seurat::Read10X_h5()`、Python 可通过 `scanpy.read_10x_h5()` 极速加载。
- **H5AD 格式**（`*.h5ad`）：RNA/C6 的计数矩阵与 RNA 下游分析对象是不同文件。计数导出不含聚类，保存的下游分析应读取 `analysis/QC_Cluster.h5ad`；ATAC 不在 `outs/` 交付计数 H5AD。

### 3. 细胞识别与元数据过滤统一法则 {#3}
- RNA/ATAC/C6 生成的 `singlecell.csv` 或 `singlecell.csv.gz` 记录了测序下机全量候选微珠/液滴的质控明细（包含游离背景与零分子行）。
- **细胞筛选**：RNA/ATAC/C6 的 singlecell 表使用 `is_cell_barcode`（`1` 或 `True`）；VDJ Contig 表使用 `is_cell`，且同一细胞可有多行，应过滤后按条形码去重统计细胞数。

### 4. 质控指标汇总表格式
- `metrics_summary.xls` 虽采用 `.xls` 后缀以便在桌面表格软件中直接双击预览，**但底层实质为标准的制表符分隔纯文本（TSV）**。
- **代码加载规范**：在 R 中请使用 `read.delim("metrics_summary.xls", check.names = FALSE)`（切勿使用 `readxl::read_excel`）；在 Python 中请使用 `pd.read_csv("metrics_summary.xls", sep="\t")`。

### 5. 比对 BAM 与索引自适应规则
- **交付开关**：scRNA 默认输出比对 BAM（支持 `--no_bam` 跳过）；scATAC 默认不输出 BAM 以节约 I/O 与存储（支持 `--need_bam` 显式开启）。
- **BAM 索引**：原生写出工具在参考序列最大长度超过 `2^29`（536,870,912）bp 时选择 CSI，否则选择 BAI。仅含表头的零结果 RNA BAM 可不带索引；Oligo BAM 不要求有坐标索引。
- **C6 BAM 输出**：`[rna] no_bam` 默认为 `false`；设置 `no_bam,true` 会跳过逐样本、未分配和 Oligo BAM 及其索引。
- **BAM 标签**：RNA/C6 的 cDNA 记录可包含 `UB` 等 UMI 标签，ATAC 不使用 RNA UMI 标签。可用 `CB` 筛选带合并细胞标识的记录；未匹配、未比对和 Oligo 记录的标签集合不同。

---

## 各组学核心特性与避坑速查

不同组学在数据结构与生物学机制上存在特有考量，下表汇总了各模态最关键的注意事项，点击可直达对应文档的详细说明：

| 模态 / 流程 | 核心注意事项与避坑要点 | 详见章节 |
| :--- | :--- | :--- |
| **scRNA** | • 表达矩阵采用 UMI 去重与跨基因同 UMI 冲突裁决，交付纯净表达谱。<br>• 多微珠共包裹液滴自动合并，细胞 ID 格式为 `CELL<ID>_N<count>`。 | [scRNA 特征矩阵与比对文件](scRNA.md#特征矩阵文件) |
| **scATAC** | • **重点**：Peak 矩阵统计经 9-bp 偏移修正的 **cutsite 计数**，质控指标（FRIP/TSS）基于 **unique fragment**，严禁将矩阵列和当做 fragment 测序深度。<br>• 3.2 矩阵 `matrix.mtx.gz` 采用单空格分隔。 | [scATAC 片段与峰文件](scATAC.md#atac片段和峰文件) |
| **scVDJ** | • 下游分析核心入口为 `filtered_contig_annotations.csv`（过滤非生产性与背景噪音）。<br>• AIRR 标准文件（`airr_annotations.tsv`）直通 `scRepertoire`/`immunarch`。<br>• `--beadstrans` 用于关联 RNA 细胞标识；Contig 表仍可一细胞多行。 | [scVDJ 组装与注释文件](scVDJ.md#vdj组装和注释文件) |
| **C6 多样本** | • 根目录合并矩阵仅保留原始计数，**不提供跨样本联合降维和聚类**，需在下游按需进行去批次校正。<br>• 各样本结果位于 `per_sample_outs/<sample>/`。<br>• 跨样本分析保留完整 Barcode 后缀防止命名碰撞。 | [C6 核心交付文件详解](c6.md#核心交付文件详解) |
| **多组学 (Multi)** | • 各组学目录独立解耦（`rna/`、`atac/`、`vdj-t/`、`vdj-b/`），支持单组学独立复用与跨模态分析。<br>• `logs/run_manifest.json` 记录各模态运行与断点复用状态。 | [多组学详细文件说明](multi.md#详细文件说明) |

---

## 常用操作指引

- 想要了解在 R 和 Python 中的具体代码加载示例？请参阅 [在 R / Python 中读取结果](../io.md)。
- 想要了解 3.1 升至 3.2 版本的输出文件变迁？请参阅 [升级前后的文件变化](../migration.md)。
- 运行过程中遇到输出文件缺失或报错？请参阅 [运行与排错](../troubleshooting.md)。
