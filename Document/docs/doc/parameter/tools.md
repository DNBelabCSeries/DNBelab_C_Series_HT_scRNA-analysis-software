# 工具命令参数

DNBelab C Series HT 工具命令参数说明

当前 `dnbc4tools tools` 的公开子命令为 `mkgtf`。下文的 `bam2fastq`、`chromsplit`、`fqsubC4` 为独立辅助工具，位于软件 `misc` 目录，不是 `dnbc4tools tools` 的子命令。

## GTF 文件操作 (mkgtf) <a id="gtf-文件操作-mkgtf"></a>

> **核心功能**
>
> GTF 文件操作工具，支持基因类型统计、按规则过滤和文件格式校验与修复。为单细胞转录组分析提供标准化的基因注释数据。

### 用法 <a id="usage-mkgtf"></a>

```bash
dnbc4tools tools mkgtf --ingtf genes.gtf --output genes.filtered.gtf
```

### 完整命令行帮助

```shell
$ dnbc4tools tools mkgtf --help
dnbc4tools 3.2

Filter and process GTF annotation files.

Usage: dnbc4tools tools mkgtf [OPTIONS]

options:
  --help           show this help message and exit

Basic Settings:
  --action <STR>   Operation type: 'mkgtf' (filter by gene types), 'stats' (count statistics), 'check' (validate
                   format) [default: mkgtf] (e.g., `stats`).
  --ingtf <FILE>   Path to input GTF annotation file (required) (e.g., `genes.gtf`).
  --output <FILE>  Path to output file (required unless --action stats). If omitted for "stats", statistics are
                   printed to stdout.

Analysis Settings:
  --include <STR>  Comma-separated list of gene types to include. Supports wildcards (e.g., 'IG_*' will match
                   'IG_V_gene', 'IG_C_gene'). [default: protein_coding,lncRNA,lincRNA,antisense,IG_*,TR_*].
  --type <STR>     Attribute name for gene type classification (e.g., gene_biotype, gene_type).
  --feature <STR>  Feature type to process from GTF. Use 'transcript' if no 'gene' entries exist [default: gene].

Usage Examples:
  Statistics:   dnbc4tools tools mkgtf --action stats --ingtf genes.gtf
  Filtering:    dnbc4tools tools mkgtf --ingtf genes.gtf --output filtered.gtf --include 'protein_coding,lncRNA'
  Validation:   dnbc4tools tools mkgtf --action check --ingtf genes.gtf --output corrected.gtf
```

### 参数速查表

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--ingtf` | 文件路径 | **必需** | 输入的标准 GTF 注释文件路径（不支持 GFF/GFF3 格式） |
| `--output` | 文件路径 | 条件必需 | 处理结果输出文件路径（`--action mkgtf` 和 `check` 模式必需；`stats` 模式可省略并输出至标准输出） |
| `--action` | 选项 | `mkgtf` | 操作模式：`mkgtf`（按基因类型过滤）、`stats`（类型分布统计）、`check`（格式自检与修复） |
| `--include` | 字符串 | 预设类型集 | 仅在 `mkgtf` 模式下生效。要保留的基因生物学类型列表（逗号分隔，支持通配符 `*`） |
| `--type` | 字符串 | `auto` | GTF 属性中用于标识基因类型的键名（如 `gene_biotype`、`gene_type`） |
| `--feature` | 字符串 | `gene` | 从 GTF 中提取的目标层级（通常为 `gene`；若无 gene 行可设为 `transcript`） |

---

### 操作模式深度解析

#### 1. 过滤模式 (`--action mkgtf`)

从包含多种非编码或假基因注释的完整 GTF 中提取感兴趣的高信度基因集合，有效减少跨基因的多重比对，提高比对唯一性：

```bash
dnbc4tools tools mkgtf \
  --action mkgtf \
  --ingtf Homo_sapiens.GRCh38.108.gtf \
  --output Homo_sapiens.filtered.gtf \
  --include "protein_coding,lncRNA,IG_*,TR_*"
```

- **通配符支持**：如 `IG_*` 匹配 `IG_V_gene`、`IG_C_gene`、`IG_J_gene` 等所有免疫球蛋白基因类型。
- **默认保留集**：`protein_coding,lncRNA,lincRNA,antisense,IG_*,TR_*`。

#### 2. 统计模式 (`--action stats`)

统计 GTF 中各类基因生物学类型的数量分布，帮助评估注释源文件的组成与分类标签名称：

```bash
dnbc4tools tools mkgtf --action stats --ingtf genes.gtf
```

#### 3. 校验与修复模式 (`--action check`)

检查 GTF 文件规范性，自动修复缺失的父级特征（如缺少 `gene` 行但有 `transcript` 行时自动推导补齐）：

```bash
dnbc4tools tools mkgtf --action check --ingtf raw_genes.gtf --output corrected.gtf
```

---

## BAM 转 FASTQ (bam2fastq) <a id="bam-转-fastq-bam2fastq"></a>

> **转换工具（位于软件 `misc` 目录）**
>
> 专用于将单细胞 C4 cDNA 及 C4/C6 Oligo 比对 BAM 文件无损反向转换提取为 FASTQ 文件。支持坐标排序与序列名排序输入、单端/双端自动检测、C4/C6 Oligo 结构识别、多线程并行压缩与指定区间提取。

### 用法 <a id="usage-bam2fastq"></a>

```shell
$ bam2fastq -h
BAM to FASTQ Converter for cDNA and oligo data

Usage: bam2fastq [OPTIONS] <BAM> <OUTPUT>

Arguments:
  <BAM>     Path to the input BAM file
  <OUTPUT>  Directory where FASTQ files will be written

Options:
      --library-type <LIBRARY_TYPE>  BAM library format; auto checks c4_oligo program metadata and oligo tags [default: auto] [possible values: auto, cDNA, oligo]
      --oligo-layout <OLIGO_LAYOUT>  Oligo layout (default: auto): c4 barcode only or c6 barcode plus R1 UMI [default: auto] [possible values: auto, c4, c6]
  -t, --threads <THREADS>            Number of CPU threads for parallel processing (default: all available cores) [default: 8]
  -r, --locus <REGION>               Process a zero-based, half-open genomic region (format: chr1:1000-2000)
      --bx-list <BX_LIST>            BX list; requires a BX-sorted BAM and .bam.bxi index
  -n, --reads-per-fastq <READS>      Maximum number of reads per FASTQ file. All reads go to a single file if not specified.
      --max-memory <MEMORY>          Working-memory target in MB for caches, queues and output buffers; not a hard RSS limit.
      --traceback                    Show detailed error traceback
      --relaxed[=<RELAXED>]          Relaxed mode: skip unpaired reads instead of erroring [default: true] [possible values: true, false]
      --auto-detect[=<AUTO_DETECT>]  Automatically detect paired-end status from BAM flags [default: true] [possible values: true, false]
      --no-compress                  Disable gzip compression for output FASTQ files
  -h, --help                         Print help
  -V, --version                      Print version
```

### 参数速查表

| 参数 / 选项 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `<BAM>` | 文件路径 | **必需 (位置参数)** | 输入的 BAM 文件路径（支持坐标排序或名称排序的 cDNA BAM，及带 `c4_oligo` 标签的 Oligo BAM） |
| `<OUTPUT>` | 目录路径 | **必需 (位置参数)** | FASTQ 文件输出目录路径 |
| `--library-type` | 选项 (`auto`, `cDNA`, `oligo`) | `auto` | BAM 文库类型格式；`auto` 会自动检查 `c4_oligo` 程序元数据及 Oligo 标签 |
| `--oligo-layout` | 选项 (`auto`, `c4`, `c6`) | `auto` | Oligo 文库结构布局：`c4` 仅条形码，`c6` 为条形码加 R1 UMI；`auto` 自动检测 |
| `-t, --threads` | 整数 | 全部可用核心 (默认 8) | 用于并行处理的 CPU 线程数 |
| `-r, --locus` | 字符串 | 无 | 处理指定的基因组区域（0-based 半开区间，格式为 `chr1:1000-2000`；需 BAM `.bai` 索引） |
| `--bx-list` | 文件路径 | 无 | 按条形码白名单列表过滤；要求 BAM 经 BX 排序且具有 `.bam.bxi` 索引 |
| `-n, --reads-per-fastq` | 整数 | 无 (全部单文件) | 单个输出 FASTQ 文件的最大读段数；未指定时全部输出到单个文件，超过则自动分卷 |
| `--max-memory` | 整数 (MB) | 系统可用内存一半 | 用于缓存、队列与输出缓冲区的目标工作内存 (MB)；非硬性系统 RSS 上限 |
| `--traceback` | 标志开关 | 关闭 | 出错时显示详细的错误追踪堆栈上下文 |
| `--relaxed` | 布尔值 (`true`, `false`) | `true` | 宽松模式：跳过未配对读段而非直接报错退出 |
| `--auto-detect` | 布尔值 (`true`, `false`) | `true` | 是否根据 BAM flags 自动检测双端测序（paired-end）状态 |
| `--no-compress` | 标志开关 | 关闭 | 禁用 gzip 压缩（直接输出未压缩的 `.fastq` 文件以获得最高写出吞吐） |
| `-h, --help` | 标志开关 | - | 显示帮助信息并退出 |
| `-V, --version` | 标志开关 | - | 显示版本号并退出 |

### 常用示例

```shell
# 基础转换（自动推断双端/单端与文库类型，使用全部可用核心）
bam2fastq sample.bam ./output/

# 指定线程数并输出至目标目录
bam2fastq -t 20 sample.bam ./output/

# 提取指定染色体区域（需要 .bai 索引）
bam2fastq -t 8 -r chr1:1000000-2000000 sample.bam ./output_chr1/

# 禁用压缩以获得最高写出速度
bam2fastq -t 8 --no-compress sample.bam ./output/

# 按每五千万条 reads 分卷输出
bam2fastq -t 20 -n 50000000 sample.bam ./output/

# Oligo 文库转换（自动识别 C4 与 C6 双 UMI 布局）
bam2fastq -t 20 oligo.records.bam ./output_oligo/
```

---

## 染色体分割 (chromsplit) <a id="染色体分割-chromsplit"></a>

> **核心功能**
>
> 基因组长染色体序列切分工具。结合 GTF 注释在非编码或基因间区（N-stretch / intergenic）寻找安全断点，主要用于处理超过 Chromap 或下游软件上限（如 $2^{29}-1$ bp）的超长染色体。

### 用法

```shell
$ chromsplit --help
Split large genome sequences into smaller fragments at N-stretches or intergenic regions

Usage: chromsplit [OPTIONS] --fasta <FA> --prefix <PREFIX>

Options:
  --fasta <FA>               Input genome sequence file in FASTA format
  --gtf <GTF>                Optional GTF/GFF annotation file for the genome
  --prefix <PREFIX>          Prefix for output files (.fa and .cutsite.tsv will be appended)
  --min_length <MIN_LENGTH>  Minimum length of output scaffold fragments [default: 300000000]
  --max_length <MAX_LENGTH>  Maximum length of output scaffold fragments [default: 500000000]
  --cut_site <CUT_SITE>      Optional cut site file containing predefined split positions
  --help                     Print help
  --version                  Print version
```

### 参数速查表

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--fasta` | 文件路径 | **必需** | 输入的大基因组 FASTA 序列文件 |
| `--prefix` | 字符串 | **必需** | 输出文件前缀（自动生成 `<prefix>.fa` 与 `<prefix>.cutsite.tsv`） |
| `--gtf` | 文件路径 | 无 | 可选的基因注释文件（确保分割点避开外显子并同步输出位移后的新注释） |
| `--min_length` | 整数 (bp) | `300000000` | 切分后输出 scaffold 片段的最小长度限制 |
| `--max_length` | 整数 (bp) | `500000000` | 切分后输出 scaffold 片段的最大长度限制 |
| `--cut_site` | 文件路径 | 无 | 包含预先指定切点坐标的文本文件 |

### 常用示例

```shell
# 结合 GTF 注释进行安全切分，保护基因结构完整性
chromsplit --fasta large_genome.fasta --gtf genes.gtf --prefix genome_split

# 指定自定义切分长度区间 (200Mb - 400Mb)
chromsplit --fasta large_genome.fasta --prefix custom_split --min_length 200000000 --max_length 400000000
```

---

## FASTQ 切割 (fqsubC4) <a id="fastq-切割-fqsubc4"></a>

> **核心功能**
>
> 高性能 FASTQ 序列区间提取与重构工具。支持按碱基坐标截取 Barcode、UMI 或 Insert 序列，用于多批次加测格式统一与非标文库重构。

### 用法

```shell
$ fqsubC4 --help
Extracts regions from FASTQ sequences

Usage: fqsubC4 [OPTIONS] --input <FILE> --output <FILE> --regions <REGIONS>

Options:
  --input <FILE>       Path to input FASTQ file (supports both uncompressed and gzipped formats)
  --output <FILE>      Path to output FASTQ file (automatically compressed if ending in .gz)
  --regions <REGIONS>  Comma-separated regions in format start:end (e.g., 7:16,23:32,38:47)
  --threads <THREADS>  Number of threads to use for parallel processing [default: 8]
  --help               Print help
  --version            Print version
```

### 参数速查表

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--input` | 文件路径 | **必需** | 输入的 FASTQ 文件路径（支持 `.fq`、`.fastq`、`.fq.gz`、`.fastq.gz`） |
| `--output` | 文件路径 | **必需** | 输出截取后的 FASTQ 文件路径（若以 `.gz` 结尾则自动进行并行 gzip 压缩） |
| `--regions` | 字符串 | **必需** | 提取的碱基区间定义，格式为 `start:end`，多段用逗号分隔（1-based 坐标） |
| `--threads` | 整数 | `8` | 用于并行读取、提取和压缩写出的 CPU 线程数 |

### 常用示例

```shell
# 从包含暗反应或前导碱基的序列中截取两个条形码片段并输出为压缩文件
fqsubC4 \
  --input sample_raw_R1.fq.gz \
  --output extracted_R1.fq.gz \
  --regions "7:16,23:32" \
  --threads 8
```
