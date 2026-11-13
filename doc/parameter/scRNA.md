# scRNA 分析参数

DNBelab C Series HT scRNA 参数配置说明

## 概述 <a id="概述"></a>

本文档说明 `dnbc4tools rna` 各子命令的参数含义、默认行为和常见使用方式，覆盖单样本分析 (`run`)、参考库构建 (`mkref`) 与多样本任务生成 (`multi`)。

> **提示**
> 参数说明以当前命令行帮助信息为基础，示例可直接作为模板调整后使用。

## 主分析流程 (run) <a id="v32-options"></a> <a id="主分析流程-run"></a>

### 用法 <a id="usage"></a>

```bash
dnbc4tools rna run \
  --name sample1 \
  --fastqs /data/rna \
  --genomeDir /reference/rna \
  --threads 20
```

### 完整命令行帮助

```shell
$ dnbc4tools rna run --help
dnbc4tools 3.2

Process a single-cell RNA-seq sample.

Usage: dnbc4tools rna run [OPTIONS]

options:
  --help                     show this help message and exit

Input Files:
  Choose one input method: either `--fastqs` (directory input) or all four individual FASTQ files.

  --fastqs <DIR>             Directory containing cDNA and oligo FASTQ subfolders (e.g.,
                             `cDNA/sample_cdna_R1.fastq.gz`, `oligo/sample_oligo_R1.fastq.gz`). Paired-end files are
                             detected from the directory structure.
  --cDNAfastq1 <FILE>        cDNA Read1 FASTQ list. Supports wildcard and comma-separated inputs (e.g.,
                             `sample1_R1.fastq.gz,sample2_R1.fastq.gz`).
  --cDNAfastq2 <FILE>        cDNA Read2 FASTQ list. Order must match `--cDNAfastq1` (e.g.,
                             `sample1_R2.fastq.gz,sample2_R2.fastq.gz`).
  --oligofastq1 <FILE>       Oligo Read1 FASTQ list for barcode merging. Supports wildcard and comma-separated inputs.
  --oligofastq2 <FILE>       Oligo Read2 FASTQ list. Order must match `--oligofastq1` (e.g.,
                             `sample1_oligo_R2.fastq.gz`).

Basic Settings:
  --name <STR>               Unique identifier for the sample. Used for naming output files and reports (e.g.,
                             `sample1`).
  --genomeDir <DIR>          Reference genome directory path containing STAR index files (e.g., `./genome_index`).
  --outdir <DIR>             Output directory path for results and reports [default: current directory] (e.g.,
                             `./output`).
  --threads <INT>            Number of CPU threads for parallel processing [default: all available cores] (e.g.,
                             `16`).

Filtering Settings:
  --calling_method <STR>     Cell detection method [default: emptydrops]. Supported values: `barcoderanks`,
                             `emptydrops`.
  --expectcells <INT>        Expected number of cells to guide detection (e.g., `3000`).
  --forcecells <INT>         Force pipeline to use exactly this number of cells, overriding expected cell detection
                             (e.g., `5000`).
  --minumi <INT>             Minimum UMI count per cell to retain [default: 1000].
  --consistent_cells <FILE>  Headered CSV or CSV.gz for merge/cell-calling constraints. Supported schemas: `cell`;
                             `cell,barcode`; `cell,is_cell_barcode`; `cell,barcode,is_cell_barcode`. Other columns are
                             ignored.

Library Settings:
  --chemistry <STR>          Library chemistry version. Auto-detected when omitted [default: auto]. Options:
                             `scRNAv1HT`, `scRNAv2HT`, `scRNAv3HT`, `scRNA5Pv1`.
  --darkreaction <STR>       Dark cycle setting for cDNA and oligo libraries. Auto-detected when omitted [default:
                             auto]. Provide two comma-separated values in the form `<cDNA>,<oligo>`.
                             cDNA=`R1`/`unset`; oligo=`R1R2`/`R1`/`unset`.
  --customize <STR>          Custom read structure string. Format: `<type>,<read>:<start>-<end>` joined by `;`. cDNA
                             (e.g., `"cb,R1:7-16;cb,R1:23-32;umi,R1:38-47;R1,R2:1-100"`). Oligo (e.g.,
                             `"cb,R1:7-16;cb,R1:23-32;R1,R2:1-10;R1,R2:17-26;R1,R2:33-42"`). For RNA, provide
                             `--customize` twice when both cDNA and oligo are customized: first cDNA, then oligo.

Analysis Settings:
  --no_introns               Exclude intronic reads from the expression matrix to increase specificity.
  --end5                     Enable 5'-end scRNA-seq analysis for 5' gene-expression profiling.
  --no_bam                   Skip BAM file generation to save time and disk space.
  --sample_read_pairs <INT>  Subsample this number of cDNA read pairs for analysis (e.g., `1000000`).
  --star_parameters <STR>    Extra STAR filtering, alignment, seeding or scoring arguments. Wrap them in quotes (e.g.,
                             `"--outFilterMismatchNmax 10 --outFilterMultimapNmax 1"`). Unknown or ineffective options
                             are rejected.
```

### 参数速查表

#### 必需与基本设置

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--name` | 字符串 | **必需** | 样本唯一标识符，用作所有输出文件的前缀和报告标题（如 `sample_001`） |
| `--genomeDir` | 目录路径 | **必需** | 参考基因组目录路径，必须包含由 `rna mkref` 构建的 STAR 索引和注释文件，兼容 v2 版本以及 Cell Ranger RNA 数据库 |
| `--outdir` | 目录路径 | `./` | 分析结果和报告的输出根目录 |
| `--threads` | 整数 | 全部可用核心 | 分析过程中使用的 CPU 线程数 |

#### 输入文件参数

输入方式二选一：使用 `--fastqs` 指定统一目录，或显式分别指定 cDNA 与 Oligo 的四个 FASTQ 参数。

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--fastqs` | 目录路径 | 无 | FASTQ 根目录（内部必须包含 `cDNA/` 与 `oligo/` 子目录，自动检测配对） |
| `--cDNAfastq1` | 文件路径 | 无 | cDNA Read 1 文件（支持逗号分隔多个文件或通配符 `*`） |
| `--cDNAfastq2` | 文件路径 | 无 | cDNA Read 2 文件（与 `--cDNAfastq1` 顺序必须严格一致） |
| `--oligofastq1` | 文件路径 | 无 | Oligo Read 1 文件（支持逗号分隔多个文件或通配符 `*`） |
| `--oligofastq2` | 文件路径 | 无 | Oligo Read 2 文件（与 `--oligofastq1` 顺序必须严格一致） |

> **提示：测序文件一致性与批次处理**
> 同一分析中的所有测序文件必须来自同一文库批次，测序模式与暗反应设置须保持一致；不同文库的数据不能混合输入。
> 如果同一文库批次的不同测序批次存在暗反应模式或者测序长度不一致的情况，则需要使用 FASTQ 裁剪工具 [`fqsubC4`](tools.md#fastq-切割-fqsubc4) 对 reads 进行裁剪，具体裁剪位置请参考[文库结构识别](../library_structure.md#scrna)。

#### 细胞识别与质控参数

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--calling_method` | `emptydrops` \| `barcoderanks` | `emptydrops` | 细胞识别算法（`emptydrops` 基于表达谱统计检验；`barcoderanks` 基于 UMI 拐点） |
| `--expectcells` | 整数 \| `auto` | `auto` | 预期细胞回收数量，为算法提供初步估计阈值 |
| `--forcecells` | 整数 | 无 | 强制输出确切的细胞数量，优先级最高（覆盖自动识别结果）。截取时按每个候选细胞条形码的总有效 UMI 计数降序截取前 N 个细胞 |
| `--minumi` | 整数 | `1000` | EmptyDrops 算法中检验候选细胞的最低 UMI 阈值（仅在 `--calling_method emptydrops` 时生效）。低于该阈值的液滴不参与第二轮非环境游离 RNA 似然比检验与细胞召回，直接视为背景空液滴。若样本测序深度较低或微小细胞有效 UMI 较少，可调低该值（如 `500`）以召回更多低丰度细胞 |
| `--consistent_cells` | CSV 文件路径 | 无 | 外部细胞条形码白名单或合并约束表（支持 `.csv` / `.csv.gz`） |

#### 文库化学与测序结构参数

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--chemistry` | 选项 | `auto` | 试剂盒化学版本：`scRNAv1HT`、`scRNAv2HT`、`scRNAv3HT`、`scRNA5Pv1` |
| `--darkreaction` | 选项 / 字符串 | `auto` | 暗循环配置，格式为 `<cDNA设置>,<oligo设置>`（如 `R1,R1R2`、`unset,unset`） |
| `--customize` | 格式字符串 | 无 | 自定义条形码与读段结构，需按顺序指定两次（先 cDNA，后 oligo） |

#### 分析设置与调优参数

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--no_introns` | 标志开关 | 关闭 | 排除内含子 reads，仅基于外显子区域量化基因表达 |
| `--end5` | 标志开关 | 关闭 | 启用 5' 端单细胞转录组数据分析模式（针对 5' 捕获试剂盒） |
| `--no_bam` | 标志开关 | 关闭 | 跳过比对 BAM 文件的生成以节省磁盘空间和分析耗时 |
| `--sample_read_pairs` | 整数 | 无 | 从 cDNA FASTQ 中抽取的读段对数量（用于快速降采样评估） |
| `--star_parameters` | 字符串 | 无 | 传递给 STAR 比对器的额外参数（须双引号包裹） |

---

### 关键参数深度解析

#### 1. FASTQ 目录结构与输入规范

当使用便捷参数 `--fastqs` 时，软件根据子目录组织自动匹配配对 FASTQ 文件：

```text
fastq_directory/
├── cDNA/
│   ├── sample_cDNA_L01_R1.fastq.gz
│   └── sample_cDNA_L01_R2.fastq.gz
└── oligo/
    ├── sample_oligo_L01_R1.fastq.gz
    └── sample_oligo_L01_R2.fastq.gz
```

- **命名识别规则**：自动检测依赖文件名中的 R1/R2 标识，支持 `_R1_`、`_R1`、`_1`、`_read1` 与对应的 `_R2_`、`_R2`、`_2`、`_read2`；扩展名支持 `.fastq.gz`、`.fq.gz`、`.fastq`、`.fq`。
- **独立输入模式**：如果不使用 `--fastqs`，则必须完整指定 `--cDNAfastq1`、`--cDNAfastq2`、`--oligofastq1`、`--oligofastq2` 四个参数。多 lane 文件用逗号连接，且 R1 与 R2 的文件顺序必须严格对应。

#### 2. 细胞识别算法与诊断策略

软件提供两种互补的细胞识别算法：

| 算法 | 原理 | 优势与适用场景 |
| :--- | :--- | :--- |
| **`emptydrops`**（默认推荐） | 基于非空液滴与背景空泡 RNA 表达谱的狄利克雷-多项分布统计检验 | 精确识别低 RNA 含量的细胞，严格控制假阳性，适用于绝大多数标准组织样本 |
| **`barcoderanks`** | 纯经验阈值法，通过总 UMI 排序曲线的“拐点 (Inflection)”与“膝点 (Knee)”进行截断 | 计算轻量，适合细胞与背景表达差异极大、或初步快速质控探索场景 |

**UMI Rank 曲线形态与调参决策：**

- **陡峭下降**：细胞群与背景噪声界限清晰，使用默认参数通常能获得极佳判定结果。
- **平缓下降 / 无明显拐点**：细胞活性低或游离 RNA（ambient RNA）污染偏重。建议采用保守细胞数，可显式设置 `--expectcells` 或通过 `--minumi 1500` 提高门槛。
- **`--minumi` 候选门槛机制**：仅在 `emptydrops` 算法中生效（默认 1000），用于定义进入非环境游离 RNA 统计检验的候选液滴最低 UMI 门槛。算法将 UMI 大于等于该阈值（且高于背景液滴最大 UMI）的液滴作为候选池，通过多项分布 Monte-Carlo 模拟检验其表达谱是否显著偏离背景空滴；低于该阈值的液滴则直接视为环境背景，不进行非环境显著性检验与召回计算。若样本由于测序深度偏低导致微小细胞未被召回，可调低该参数（如 `--minumi 500`）。
- **细胞数严重偏离预期**：
  - *过低*：常因 `--minumi` 设置过严或文库上样不足，可降低 `--minumi 500` 后复查。
  - *过高*：常因背景空滴多，可改用 `--forcecells <N>` 直接固定目标有效细胞数（系统将按候选条形码的总有效 UMI 计数降序排列，直接截取前 N 个细胞）。

#### 3. 外部细胞白名单约束 (`--consistent_cells`)

用于在细胞条形码合并与最终细胞识别阶段引入外部先验信息（例如跨组学对齐或历史金标准表）。文件为带表头的 CSV（支持 `.csv` 或 `.csv.gz`）：

| 支持的表头结构 | 功能说明 |
| :--- | :--- |
| `cell` | 仅限制最终识别出的有效细胞列表 |
| `cell,barcode` | 强制指定 bead 与 cell 的归属合并映射关系；**在此模式下，Oligo 数据的分析结果将被绕过，直接应用该映射** |
| `cell,is_cell_barcode` | 指定候选条形码并标注其是否作为细胞识别基准 |
| `cell,barcode,is_cell_barcode` | 同时提供细胞与微珠对应关系，并通过 `is_cell_barcode`（1/0 或 true/false）直接指定每个条形码的细胞识别状态（例如直接传入质控输出的 `singlecell.csv`） |

#### 4. 文库化学与暗反应配置 (`--chemistry` & `--darkreaction`)

- **试剂版本 (`--chemistry`)**：支持 `scRNAv1HT`、`scRNAv2HT`、`scRNAv3HT`、`scRNA5Pv1`。默认 `auto` 即可自动解析结构。
- **暗反应 (`--darkreaction`)**：针对 MGI 测序平台的暗循环设计。
  - 自动模式：`--darkreaction auto`
  - 手工模式格式为 `<cDNA设置>,<oligo设置>`：
    - cDNA 可选：`R1` 或 `unset`
    - Oligo 可选：`R1R2`、`R1` 或 `unset`
    - 常见设置：`--darkreaction R1,R1R2`（双端暗循环）、`--darkreaction unset,unset`（无暗反应）
  - **重要原则**：显式指定 chemistry 时，必须同时显式设置 `--darkreaction`。

#### 5. 自定义文库结构 (`--customize`) <a id="customize"></a>

针对特殊、改进型或第三方非标建库方案，使用 `--customize` 精确定义 Barcode、UMI 与有效序列的起止区间（1-based 闭区间坐标，不可超出测序读长）。

> **文库结构参考**：完整的文库接头序列、区段物理坐标与暗反应图解请参阅 [文库结构识别](../library_structure.md)。

##### 语法规则与传参要求

- **语法结构**：`"<type>,<read>:<start>-<end>"`，多个片段用分号 `;` 连接。
  - `cb`：细胞条形码 (Cell Barcode)
  - `umi`：分子唯一标识符 (UMI)
  - `R1` / `R2`：有效读段序列（用于配对校验或转录本比对）
- **配置规则**：RNA 流程包含 cDNA 与 Oligo 两个文库，因此需要**按顺序连续传入两次 `--customize`**（第一次针对 cDNA，第二次针对 oligo）。

##### 场景配置对比：如何正确去除固定序列

###### 示例 A：无暗反应模式（从头完整测序，去除固定序列）
在标准测序模式或未开启暗反应的测序中，测序结果包含固定接头（Linker）。若将固定接头作为 Barcode 会造成识别失败。**配置时通过指定区间直接跳过固定序列，即可实现安全去除**：

- **cDNA 提取策略**：
  - 跳过 1–6 bp（Linker 1），截取 `cb,R1:7-16`（CB1 10bp）
  - 跳过 17–22 bp（Linker 2），截取 `cb,R1:23-32`（CB2 10bp）
  - 跳过 33–37 bp（Linker 3），截取 `umi,R1:38-47`（UMI 10bp）
  - Read 2 对应 1–100 bp 转录本插入序列：`R1,R2:1-100`
  - 提取参数：`--customize "cb,R1:7-16;cb,R1:23-32;umi,R1:38-47;R1,R2:1-100"`
- **Oligo 提取策略**：
  - Read 1 跳过固定接头：`cb,R1:7-16;cb,R1:23-32`
  - Read 2 提取第一段 UMI (1–10 bp)，跳过固定接头后提取 Tag 1 (17–26 bp) 与 Tag 2 (33–42 bp)：`R1,R2:1-10;R1,R2:17-26;R1,R2:33-42`
  - 提取参数：`--customize "cb,R1:7-16;cb,R1:23-32;R1,R2:1-10;R1,R2:17-26;R1,R2:33-42"`

运行示例：
```bash
dnbc4tools rna run \
  --name non_dark_demo --genomeDir /reference/rna \
  --cDNAfastq1 cdna_R1.fq.gz --cDNAfastq2 cdna_R2.fq.gz \
  --oligofastq1 oligo_R1.fq.gz --oligofastq2 oligo_R2.fq.gz \
  --customize "cb,R1:7-16;cb,R1:23-32;umi,R1:38-47;R1,R2:1-100" \
  --customize "cb,R1:7-16;cb,R1:23-32;R1,R2:1-10;R1,R2:17-26;R1,R2:33-42" \
  --threads 20
```

###### 示例 B：暗反应模式（测序仪已跳过固定序列）
测序仪已通过暗反应在硬件层面跳过了固定接头，测序产物中全长均为有效信息，直接从第 1 位开始提取：

- **cDNA 提取**：`--customize "cb,R1:1-10;cb,R1:11-20;umi,R1:21-30;R1,R2:1-100"`
- **Oligo 提取**：`--customize "cb,R1:1-10;cb,R1:11-20;R1,R2:1-30"`

运行示例：
```bash
dnbc4tools rna run \
  --name dark_demo --genomeDir /reference/rna \
  --cDNAfastq1 cdna_R1.fq.gz --cDNAfastq2 cdna_R2.fq.gz \
  --oligofastq1 oligo_R1.fq.gz --oligofastq2 oligo_R2.fq.gz \
  --customize "cb,R1:1-10;cb,R1:11-20;umi,R1:21-30;R1,R2:1-100" \
  --customize "cb,R1:1-10;cb,R1:11-20;R1,R2:1-30" \
  --threads 20
```

#### 6. STAR 比对参数透传 (`--star_parameters`)

通过 `--star_parameters` 可以向内置 STAR 比对引擎直接追加经过校验的比对、过滤或 seeding 参数：

```bash
--star_parameters "--outFilterMismatchNmax 10 --outFilterMultimapNmax 1"
```

> **注意：** 仅接受 STAR 比对相关参数；由流程内部管理的参数（如输入输出目录、线程数、基因组索引）以及未知参数会被预检阶段自动拒绝。若对磁盘或耗时敏感且无需下游可视化，推荐直接添加 `--no_bam` 跳过 BAM 生成。

---

## 参考数据库构建 (mkref) <a id="参考数据库构建-mkref"></a>

`dnbc4tools rna mkref` 基于参考基因组 FASTA 和 GTF 注释文件，构建用于比对与表达量化的高效 STAR 索引库。

### 用法

```bash
dnbc4tools rna mkref \
  --fasta genome.fa --ingtf genes.gtf \
  --species human --genomeDir /reference/rna --threads 20
```

### 完整命令行帮助

```shell
$ dnbc4tools rna mkref --help
dnbc4tools 3.2

Build an RNA reference database.

Usage: dnbc4tools rna mkref [OPTIONS]

options:
  --help              show this help message and exit

Input Files:
  Input genome FASTA files and gene-annotation GTF files. For mixed-species analysis, separate multiple files with
  commas.

  --fasta <FILE>      Reference-genome FASTA file path(s). Separate multiple files with commas (e.g.,
                      `genome1.fa,genome2.fa`).
  --ingtf <FILE>      Gene-annotation GTF file path(s). Separate multiple files with commas (e.g.,
                      `anno1.gtf,anno2.gtf`).

Basic Settings:
  --genomeDir <DIR>   Output directory path for generated reference files [default: current directory] (e.g.,
                      `./ref`).
  --species <STR>     Species identifier(s) [default: undefined]. For mixed-species references, provide
                      comma-separated names in the same order as --fasta and --ingtf (e.g., `human,mouse`).
  --threads <INT>     Number of CPU threads for parallel processing [default: all available cores] (e.g., `16`).

Advanced Settings:
  --chrM <STR>        Mitochondrial chromosome name [default: auto-detect common names]. For mixed-species references,
                      provide comma-separated names in --species order (e.g., `MT,chrM`).
  --limitram <INT>    RAM limit for STAR index generation, in GiB (e.g., `64`). Omit to use STAR's default. Index
                      sparsity can affect mapping memory use and speed.
  --extra-args <STR>  Additional validated STAR genomeGenerate parameters (e.g., `"--sjdbOverhang 100
                      --genomeSAsparseD 2"`). Preflight rejects alignment-only, unknown and mkref-managed parameters.
  --noindex           Skip the STAR index-generation step.
```

### 参数速查表

#### 必需与输入文件参数

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--fasta` | 文件路径 | **必需** | 参考基因组 FASTA 文件路径（双物种时用逗号分隔，如 `human.fa,mouse.fa`） |
| `--ingtf` | 文件路径 | **必需** | 基因结构注释 GTF 文件路径（双物种时用逗号分隔，如 `human.gtf,mouse.gtf`） |
| `--genomeDir` | 目录路径 | `./` | 生成的参考数据库输出目录 |
| `--species` | 字符串 | `undefined` | 物种标识符，双物种时用逗号分隔（如 `human,mouse`） |
| `--threads` | 整数 | 全部可用核心 | STAR 索引构建与处理的 CPU 线程数 |

#### 高级设置参数

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--chrM` | 字符串 | 自动识别 | 线粒体染色体名称（双物种按 species 顺序用逗号分隔，如 `MT,chrM`） |
| `--limitram` | 整数 (GiB) | STAR 默认 | STAR 基因组索引生成过程的最大 RAM 限制（单位 GiB），可限制比对时使用的内存数量，内存占用越低耗时越高 |
| `--extra-args` | 字符串 | 无 | 传递给 STAR `genomeGenerate` 的额外校验参数（如 `"--sjdbOverhang 100"`） |
| `--noindex` | 标志开关 | 关闭 | 仅生成配置文件和注释预处理结果，跳过耗时的 STAR 索引构建 |

---

### 关键配置与数据库解析

#### 1. GTF 注释规范与双物种配置

- **GTF 文件要求**：
  - 必须为标准 GTF 格式（不支持 GFF/GFF3 格式）。
  - 必须包含 `gene` 或 `transcript` 以及 `exon` 类型注释行。
  - 属性字段必须包含 `gene_id` 或 `gene_name`，以及 `transcript_id` 或 `transcript_name`。
  - 染色体名称必须与 FASTA 基因组完全一致。
- **双物种参考库构建**：
  - `--fasta`、`--ingtf` 与 `--species` 支持逗号分隔传入两个物种的文件与名称。
  - 三者的物种顺序必须严格保持一一对应：
    ```bash
    dnbc4tools rna mkref \
      --fasta human.fa,mouse.fa \
      --ingtf human.gtf,mouse.gtf \
      --species human,mouse
    ```
  - 构建过程会自动为每个基因加上物种前缀（如 `human_GAPDH`、`mouse_Actb`），便于下游细胞混合鉴定。

#### 2. 参考数据库目录结构与元信息

构建成功后，在 `--genomeDir` 目录下会生成统一的规范结构（物种输出目录自动命名为 `<species>`，双物种时命名为 `species1_and_species2`）：

- **数据库兼容性**：除了由当前版本 `rna mkref` 构建的参考目录外，`dnbc4tools rna run` 亦全面兼容历史 v2 版本参考数据库以及标准的 Cell Ranger RNA 参考数据库目录（可直接将包含 STAR 索引与注释的目录传入 `--genomeDir`）。

```text
genomeDir/
└── <species>/
    ├── fasta/
    │   └── genome.fa          # 处理整合后的基因组序列
    ├── genes/
    │   └── genes.gtf          # 标准化提取后的基因注释文件
    ├── star/
    │   ├── SA                 # STAR 索引文件
    │   ├── SAindex            # STAR 索引核心文件
    │   ├── chrLength.txt      # 染色体长度信息
    │   ├── chrName.txt        # 染色体名称列表
    │   ├── mtgene.list        # 线粒体基因列表（用于 QC 统计）
    │   └── genomeParameters.txt
    └── ref.json               # 数据库核心元信息与版本配置
```

**单物种 `ref.json` 示例：**

```json
{
  "chrmt": "chrM",
  "genome": "/database/scRNA/Homo_sapiens/fasta/genome.fa",
  "genomeDir": "/database/scRNA/Homo_sapiens/star",
  "gtf": "/database/scRNA/Homo_sapiens/genes/genes.gtf",
  "input_fasta_files": [
    "genome.fa"
  ],
  "input_gtf_files": [
    "genes.gtf"
  ],
  "mtgenes": "/database/scRNA/Homo_sapiens/star/mtgene.list",
  "species": "Homo_sapiens",
  "version": "3.2"
}
```

**双物种 `ref.json` 示例：**

```json
{
  "chrmt": "human_chrM,mouse_chrM",
  "genome": "/database/scRNA/human_and_mouse/fasta/genome.fa",
  "genomeDir": "/database/scRNA/human_and_mouse/star",
  "gtf": "/database/scRNA/human_and_mouse/genes/genes.gtf",
  "input_fasta_files": [
    "human.fa",
    "mouse.fa"
  ],
  "input_gtf_files": [
    "human.gtf",
    "mouse.gtf"
  ],
  "mtgenes": "/database/scRNA/human_and_mouse/star/mtgene.list",
  "species": "human_and_mouse",
  "version": "3.2"
}
```

---

## 多样本操作 (multi) <a id="多样本操作-multi"></a>

`dnbc4tools rna multi` 依据制表符分隔的样本列表文件，为每个样本自动生成独立的执行 Shell 脚本。该命令仅生成分析脚本，不会自动启动分析。

### 用法

```bash
dnbc4tools rna multi --list samples.tsv --genomeDir /reference/rna --threads 20
```

### 完整命令行帮助

```shell
$ dnbc4tools rna multi --help
dnbc4tools 3.2

Process multiple RNA-seq samples.

Usage: dnbc4tools rna multi [OPTIONS]

options:
  --help             show this help message and exit

Input Files:
  --list <FILE>      Tab-separated sample list: sample name <TAB> cDNA R1;R2 <TAB> oligo R1;R2. Multiple FASTQ files
                     within one end are comma-separated. Generates one shell script per sample in the current working
                     directory; run the generated scripts to start analysis.

Basic Settings:
  --genomeDir <DIR>  Reference genome directory path containing required reference files.
  --outdir <DIR>     Analysis output directory written into each generated script [default: current directory] (e.g.,
                     `./output`). Scripts are written to the current working directory.
  --threads <INT>    Number of CPU threads written into each generated analysis script. If omitted, each analysis
                     detects available cores when it runs.

Analysis Settings:
  --end5             Enable 5'-end single-cell transcriptome analysis.
  --no_bam           Skip BAM file generation for every sample in the generated scripts.
```

### 参数速查表

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--list` | 文件路径 | **必需** | 制表符分隔的多样本清单文件 |
| `--genomeDir` | 目录路径 | **必需** | 参考基因组数据库目录路径 |
| `--outdir` | 目录路径 | `./` | 写入各样本脚本中的输出根目录（脚本本身生成在当前工作目录） |
| `--threads` | 整数 | 自动识别 | 写入各样本脚本中的 CPU 线程数 |
| `--end5` | 标志开关 | 关闭 | 在生成的脚本中启用 5' 端单细胞转录组分析 |
| `--no_bam` | 标志开关 | 关闭 | 在生成的脚本中为所有样本跳过 BAM 文件生成 |

---

### 清单文件规范与执行机制

#### 1. `--list` 列表文件格式

列表文件必须使用制表符 (`\t`) 分隔，包含三列内容：
1. **样本标识** (`sample_name`)
2. **cDNA 数据路径**（配对 R1 与 R2 之间用分号 `;` 分隔，同端多文件用逗号 `,` 连接）
3. **Oligo 数据路径**（配对 R1 与 R2 之间用分号 `;` 分隔，同端多文件用逗号 `,` 连接）

```tsv
SampleA	/data/A_cDNA_R1.fq.gz;/data/A_cDNA_R2.fq.gz	/data/A_oligo_R1.fq.gz;/data/A_oligo_R2.fq.gz
SampleB	/data/B_cDNA_L1_R1.fq.gz,/data/B_cDNA_L2_R1.fq.gz;/data/B_cDNA_L1_R2.fq.gz,/data/B_cDNA_L2_R2.fq.gz	/data/B_oligo_R1.fq.gz;/data/B_oligo_R2.fq.gz
```

#### 2. 执行机制与脚本管理

- 运行 `dnbc4tools rna multi` 后，将在当前目录下为清单中的每个样本生成独立的执行脚本（如 `SampleA.sh`、`SampleB.sh`）。
- 脚本内已自动拼装 `dnbc4tools rna run` 的完整命令参数。
- 用户可直接通过 `bash SampleA.sh` 运行，或提交至集群调度系统（如 Slurm、SGE）实现并行批量分析。
