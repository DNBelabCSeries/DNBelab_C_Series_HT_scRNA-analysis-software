# Chinese–English Glossary

This glossary defines the terms used in the 3.2 documentation to distinguish experimental objects, analysis steps, and report contents. Commands, options, field names, and report UI labels retain their original software spelling.

## Experimental Objects and Identifiers {#objects-and-identifiers}

| 中文 | English | Meaning and Usage |
| :--- | :--- | :--- |
| 微珠 | bead | A barcoded bead used in the experiment. Chinese prose consistently uses 微珠. A droplet may contain multiple beads; bead counts are not cell counts. |
| 液滴 | droplet | A microfluidic reaction droplet. It may contain background, one cell, or multiple cells, and is not equivalent to a cell. |
| 细胞 | cell | A biological entity. In analysis outputs, a called cell refers to a barcode or merged-bead group that passes the relevant calling rules; consult each metric for its counting unit. |
| 样本条形码 | sample barcode | A label distinguishing biological samples in C6. Chinese prose may introduce it as 样本条形码（sample barcode）. The UI label `Sample Barcode` is preserved. |
| 微珠条形码 | bead barcode | A barcode identifying a bead. After bead merging, multiple beads may share a cell identifier. |
| 细胞条形码 | cell barcode | A cell-associated identifier in a matrix, BAM, or metadata table. Preserve the complete identifier and sample suffix; the presence of an identifier alone does not establish a valid cell call. |
| 重叠群 | contig | A sequence assembly product. Use “full-length” for sequences or contigs, not for clonotype identification. |
| 克隆型 | clonotype | A category of immune receptor sequences defined by the analysis rules. Clonotype identification and full-length sequence assembly are distinct steps. |

## Analysis Steps and Reports {#analysis-and-reporting}

| 中文 | English | Meaning and Usage |
| :--- | :--- | :--- |
| 细胞识别 | cell calling | Selecting cells for downstream analysis using barcode counts, background models, or specified rules. Chinese prose consistently uses 细胞识别; methods and thresholds are defined in each module. |
| 样本解复用 | sample demultiplexing | Assigning pooled data to samples using sample barcodes. Use the spelling `demultiplexing`; unassigned reads are tracked separately. |
| 微珠合并 | bead merging | Associating beads inferred to originate from the same cell or droplet with a common identifier. See each workflow for the method used. |
| 联合分析 | joint analysis | Comparing or analyzing related samples or modalities. Specify whether this means workflow orchestration, cell association, or downstream data integration. |
| 流程统一调度 | unified workflow orchestration | Configuring and executing multiple modules from a single entry point. This does not imply joint dimensionality reduction or clustering across modalities. |
| 数据整合 | data integration | Downstream joint modeling of samples or modalities. The need for batch correction depends on the experimental design. |
| 组合报告 | combined report | A report presenting metrics and plots from multiple modules. Generating it does not itself perform joint dimensionality reduction, clustering, or batch correction across modalities. |
| 批次汇总报告 | batch summary report | A C6 report summarizing shared library metrics and cross-sample comparisons, distinct from per-sample reports. |

## Related Documentation {#related-documentation}

- [Workflow Overview](pipeline/pipeline.md)
- [C6 Outputs](outs/c6.md)
- [Multi-Omics Workflow](pipeline/multi.md)
- [Downstream Analysis Guide](io.md)
