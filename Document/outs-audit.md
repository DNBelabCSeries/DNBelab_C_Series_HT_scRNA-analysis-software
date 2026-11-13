# 3.2 输出文档核对记录

核对日期：2026-11-07。范围为 `doc/outs/` 六组中英文文档（12 页）。

主要依据相邻 `dnbc4tools_py` 工作区（HEAD `2adbe21`）的输出命名、发布与报告读取实现；涉及原生 CSV/BAM 字段时，补充核对 `dnbc4rust`（HEAD `39e5193`）的写出实现。未修改这两个源码项目。

## 已修正的差异

| 项目 | 文档修正 | 主要依据（相对于对应源码项目） |
| :--- | :--- | :--- |
| RNA/C6 计数 H5AD | 区分 `filtered_feature_bc_matrix.h5ad` 原始计数和 `analysis/QC_Cluster.h5ad` 下游对象；删除保证存在 PCA/UMAP、剪接层等描述 | Python `pipelines/rna/analysis.py`、`infrastructure/filesystem/rna_h5ad.py`、`pipelines/multi/analysis.py` |
| RNA 聚类字段 | 使用 `obs['leiden']`、`uns['rank_genes_groups']`；区分 CSV 首列行索引、`leiden` 与展示标签 `Cluster` | Python `algorithms/rna/clustering_outputs.py` |
| Marker 导出 | 补充正向差异、校正 P < 0.05、每簇最多 50 个基因；`marker_table.csv` 的 `_pval` 为校正值 | Python `algorithms/rna/clustering_outputs.py` |
| RNA 指标分母 | 区分转录组置信比对 reads、原始输入 reads 与识别细胞内分子支持 reads；删除统一分母说法 | Python `config/template/report_glossary.json`、`infrastructure/reporting/readers/rna.py` |
| RNA BAM | `RE` 为 SAM `A` 类型；基因 ID 不限定 Ensembl；不将 UMI 标签存在解释为 BAM 已按分子去重 | Rust `c4_bam/src/bam_tags.rs`、`c4_annotation/src/read_annotation.rs` |
| ATAC 峰注释 | 补充可选的 `peak_annotation.tsv`、十个字段、坐标与关联基因的一对多关系、发布条件 | Python `application/atac_peak_annotation.py`、`algorithms/atac/peak_annotation.py` |
| ATAC 可选输出 | 补充根目录的双物种分类和白名单诊断文件；明确 ATAC 聚类对象未作为 `outs/analysis/` 发布 | Python `pipelines/atac/report_outputs.py`、`application/multi/reporting/organization.py` |
| ATAC 统计口径 | TSS 窗口为 ±1,000 bp；FRIP/TSS 汇总以核内唯一片段为分母；Targeting 散点图使用全部唯一片段；细胞内片段比例使用含重复支持的 `totalFrags` | Python `infrastructure/reporting/readers/atac_plot_inputs.py`、`readers/atac.py`、`config/template/report_glossary.json` |
| VDJ 发布条件 | FASTA 索引可选；无重叠群时允许空 FASTA 和精简表头；明确 TR/IG 报告名 | Python `pipelines/vdj/report_workflow.py`、`pipelines/vdj/clonotype.py`、`infrastructure/filesystem/report_bundles.py` |
| VDJ 字段与关联 | CSV 布尔值与 AIRR T/F 区分；补充 `exact_subclonotype_id`；过滤依据为 `productive && is_cell && high_confidence`；RNA 关联不能假设 Contig 表一细胞一行 | Rust `vdj_assembly/src/annotation_writer.rs`、`clonotype_builder.rs`、`barcode_transformation.rs` |
| C6/Multi 层级与失败样本 | C6 全局矩阵位于 `outs/rna/`，样本位于其 `per_sample_outs/`；补充失败/空样本可能缺少分析或报告；Multi RNA BAM 标注 `no_bam` 条件 | Python `application/multi/reporting/organization.py`、`rna_publication.py`、`sample_rna_publication.py` |
| 通用格式与索引 | ATAC MEX 使用 `peaks.bed.gz`，不直接套用 RNA features 文件读取规则；区分 VDJ `is_cell`；BAI/CSI 阈值使用 `2^29` bp；补充零结果索引例外 | Python `infrastructure/filesystem/report_bundles.py`、Rust `c4_bam/src/output.rs` |
| 双物种标签 | 增补 `Unassigned`，说明 `Multiplet` 是混合候选而非已证实生物学双胞 | Python `domain/multi_genome.py`、`infrastructure/reporting/*_multi_genome.py` |

## 验证范围

- 运行 `tests/atac/test_peak_annotation.py` 与 `tests/vdj/test_report_contract.py`：26 项中 24 项通过，2 项因缺少 pandas 跳过。
- 核对文档中的规范文件名及峰注释字段与源码声明一致。
- 使用现有双版本构建脚本重建站点，并运行 `Document/check_site.py` 检查链接、资源、锚点、版本清单及 3.1 冻结源哈希。

本次为源码契约核对与定向单元验证；未运行真实 FASTQ 的端到端流程，也未验证不同系统的外部工具二进制组合。文档中的质控参考区间不作为源码验证通过的阈值或性能结论。
