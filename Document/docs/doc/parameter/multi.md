# Multi 多组学分析参数

`dnbc4tools multi run` 通过一份分段式 CSV 配置文件，实现单细胞 RNA、ATAC 与 V(D)J 等多组学文库的统一调度、质控与联合分析。

> **提示**
> 如需进行基于 Sample Barcode 混合的多样本单细胞 RNA 分析，请参阅独立的 [C6 多样本分析参数说明](c6.md)。

## 运行命令 <a id="多组学整合流程-run"></a>

```bash
dnbc4tools multi run \
  --name demo \
  --csv multi.config.csv \
  --outdir ./results \
  --threads 20
```

| 参数 | 是否必需 | 说明 |
| :--- | :--- | :--- |
| `--name` | 是 | 任务名称；结果写入 `<outdir>/<name>/` |
| `--csv` | 是 | 分段式 CSV 配置文件 |
| `--outdir` | 否 | 分析输出根目录，默认当前目录 |
| `--threads` | 否 | 总 CPU 线程数，默认全部可用核心 |

### 完整命令行帮助

```shell
$ dnbc4tools multi run --help
dnbc4tools 3.2

Process an integrated multi-omics sample.
Coordinate RNA, ATAC, and V(D)J workflows within a single run.
Support C6 probe-barcoded RNA sample demultiplexing via [samples].
Generate a unified multi-omics report.

Usage: dnbc4tools multi run [OPTIONS]

options:
  --help           show this help message and exit

Basic Settings:
  --name <STR>     Unique identifier for the sample.
  --csv <FILE>     CSV file containing pipeline configuration settings. Add [samples] for C6 RNA sample
                   demultiplexing; RNA chemistry is fixed to scRNAC6 in this mode.
  --outdir <DIR>   Output directory path for analysis results.
  --threads <INT>  Number of CPU threads to use [default: all available cores].
```

`rna multi` 和 `atac multi` 只生成逐样本脚本；这里的 `multi run` 会实际执行分析。

## CSV 配置规则 <a id="csv-配置规范"></a>

模态分段使用 `参数名,值`；`[libraries]` 使用带表头的行表。

| 分段 | 用途 |
| :--- | :--- |
| `[rna]` | RNA 参考、试剂和细胞识别等设置 |
| `[atac]` | ATAC 参考、峰检测和过滤设置 |
| `[vdj-t]` / `[vdj-b]` | TCR / BCR 参考及组装设置 |
| `[libraries]` | FASTQ 目录与模态对应关系，必填 |

布尔值推荐 `true/false`。值含逗号时加双引号，例如 `darkreaction,"R1,R1R2"`。`[rna] expectcells` 和 `[atac] jaccard_cutoff` 可填 `auto`。输入目录建议使用绝对路径。

RNA FASTQ 根目录须含 `cDNA/`、`oligo/`；ATAC 和 VDJ 目录直接放对应文库的配对 FASTQ。文件名的 R1/R2 规则见[快速开始](../quickstart.md#file-naming-conventions)。

> **提示：测序文件一致性与批次处理**
> Multi 允许在同一次运行中配置独立的 RNA、ATAC、TCR 和 BCR 文库。对同一模态输入项，合并的 FASTQ 应来自对应文库，并保持读段结构及暗反应设置兼容；不要将无关文库混入同一模态输入目录。不同模态分别配置。
> 如果同一文库批次的不同测序批次存在暗反应模式或者测序长度不一致的情况，则需要使用 FASTQ 裁剪工具 [`fqsubC4`](tools.md#fastq-切割-fqsubc4) 对 reads 进行裁剪，具体裁剪位置请参考[文库结构识别](../library_structure.md)。

## 普通多组学配置 <a id="配置示例"></a>

以下为 5′ RNA + TCR 的最小示例，保存为 `multi.config.csv` 后使用上方命令运行。

```csv
[rna]
genomeDir,/database/scRNA/Human
end5,true
no_bam,true

[vdj-t]
ref,human

[libraries]
fastqs,feature_types
/rawdata/rna,rna
/rawdata/tcr,vdj-t
```

使用 BCR 时将 `[vdj-t]` / `vdj-t` 改为 `[vdj-b]` / `vdj-b`。添加 ATAC 时增加 `[atac]` 及对应的 libraries 行。只运行 RNA 时移除 VDJ 分段及该输入行。

VDJ 默认复用 RNA 的细胞信息；可用 `beadstrans` 指定另一份细胞表。普通 RNA + VDJ 联合分析需设置 `end5,true`。

<a id="c6-samples"></a>

> **提示：C6 多样本参数配置**
>
> C6 多样本单细胞 RNA 分析的配置规则、`[samples]` 样本表格式及 Sample Barcode 映射参数已独立成章，详情请参阅 [C6 多样本分析参数说明](c6.md)。

## 模块参数映射 <a id="模块参数映射"></a>

| 分段 | 常用设置 | 完整参数说明 |
| :--- | :--- | :--- |
| `[rna]` | `genomeDir`, `chemistry`, `darkreaction`, `expectcells`, `forcecells`, `minumi`, `consistent_cells`, `calling_method`, `no_introns`, `end5`, `no_bam`, `star_parameters`, `sample_read_pairs` | [RNA](scRNA.md) |
| `[atac]` | `genomeDir`, `darkreaction`, `forcecells`, `frags_cutoff`, `tss_cutoff`, `jaccard_cutoff`, `merge_cutoff`, `need_bam`, `sample_read_pairs` | [ATAC](scATAC.md) |
| `[vdj-t]` / `[vdj-b]` | `ref`, `beadstrans`, `darkreaction`, `customize`, `keep_all_cells`, `r2_only`, `enrichment_primers`, `sample_read_pairs` | [VDJ](scVDJ.md) |

普通 RNA 显式 chemistry 与暗反应须成对设置。`customize` 可按对应文库规则填写多条，其余单值参数保留一份定义。

