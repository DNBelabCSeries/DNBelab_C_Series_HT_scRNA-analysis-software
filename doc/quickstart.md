# 快速开始指南

本指南提供 DNBelab C Series™ 单细胞分析套件（dnbc4tools）的端到端快速上手流程，涵盖环境准备、参考库构建、单组学分析、多组学统筹调度、C6 多样本单细胞 RNA 分析以及批量分析脚本生成。

---

## 选择运行方式 <a id="choose-workflow"></a>

根据您的实验设计与建库类型，选择对应的命令入口：

| 分析类型 | 命令入口 | 适用场景与说明 |
| :--- | :--- | :--- |
| [**单细胞 RNA 分析**](#single-cell-rna-analysis) | `dnbc4tools rna run` | 单样本标准转录组定量、EmptyDrops 细胞识别与聚类 |
| [**单细胞 ATAC 分析**](#single-cell-atac-analysis) | `dnbc4tools atac run` | 单样本染色质开放区分析、Peak Calling 与质控 |
| [**单细胞 V(D)J 分析**](#single-cell-vdj-analysis) | `dnbc4tools vdj run` | TCR / BCR 全长序列从头组装、注释与克隆型识别 |
| [**多组学联合分析**](#integrated-multi-omics-analysis) | `dnbc4tools multi run --csv multi.config.csv` | RNA + ATAC + VDJ 多组学统筹调度与跨组学交互报告 |
| [**C6 多样本 RNA 分析**](#c6-multi-sample-analysis) | `dnbc4tools multi run --csv sample.config.csv` | 基于 Sample Barcode 混合建库解复用与各样本结果输出 |
| [**批量分析脚本生成**](#batch-script-generation) | `dnbc4tools <rna/atac> multi` | 批量生成独立样本分析脚本，后续由调度系统排队执行 |

---

## 使用前准备 <a id="prerequisites"></a>

<div class="doc-callout doc-callout-info" markdown="block">
<strong>运行前请确认：</strong>
<ul style="margin-bottom: 0;">
  <li><strong>环境与路径</strong>：已完成软件安装（详见 <a href="./installation.md">安装指南</a>）；示例中的 <code>$dnbc4tools</code>、<code>/test/data/...</code> 与 <code>/database/...</code> 请替换为实际路径。</li>
  <li><strong>输出目录</strong>：流程默认在当前目录下生成以 <code>--name</code> 命名的任务目录（结果保存在 <code>./&lt;name&gt;/outs/</code>）；亦可通过 <code>--outdir</code> 显式指定自定义输出根目录。</li>
</ul>
</div>

### `--fastqs` 目录自动识别命名规则 <a id="file-naming-conventions"></a>

当使用 `--fastqs <dir>` 目录输入方式时，流程会自动扫描目录下所有匹配文件并按命名模式自动配对双端测序数据：

| 测序端 | 识别模式（Pattern） | 匹配示例 |
| :--- | :--- | :--- |
| **Read 1 (R1)** | 包含 `_R1_`、`_R1`、`_1` 或 `_read1` | `sample_R1.fastq.gz`、`sample_1.fq.gz`、`sample_R1_001.fastq.gz` |
| **Read 2 (R2)** | 包含 `_R2_`、`_R2`、`_2` 或 `_read2` | `sample_R2.fastq.gz`、`sample_2.fq.gz`、`sample_R2_001.fastq.gz` |

* **支持扩展名**：`.fastq.gz`、`.fq.gz`、`.fastq`、`.fq`
* **逐项指定文件不受命名限制**：若通过独立参数（如 `--fastq1/--fastq2`，或 RNA 的 `--cDNAfastq1/2`、`--oligofastq1/2`）逐项显式指定，文件名不受上述规则限制，但双端文件列表顺序须严格一一对应。

---

## 单细胞 RNA 分析 <a id="single-cell-rna-analysis"></a>

适用于常规单样本 3′ 或 5′ 单细胞转录组基因表达定量与聚类分析。

### 第一步：构建参考数据库 {#rna-prepare-reference}

已有兼容参考库时可跳过构建，直接在分析命令中填写完整参考目录。以下物种示例按需选择，并在各自独立的工作目录执行。`mkref --genomeDir /database/scRNA` 指定参考输出根目录，软件会追加物种子目录，生成 `/database/scRNA/Homo_sapiens`、`/database/scRNA/Mus_musculus` 或 `/database/scRNA/hg38_and_mm10`。后续 `run --genomeDir` 应填写该物种目录，而不是输出根目录或原始 FASTA/GTF 文件。混合物种示例中的 `hg38/`、`mm10/` 两份过滤后 GTF 需事先分别准备。

以常用物种的人、小鼠及双物种混合为例：

**人（Human, GRCh38）**
```bash
# 1. 下载 GENCODE 注释文件与基因组 FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/GRCh38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/gencode.v32.primary_assembly.annotation.gtf.gz

# 2. 解压文件
gzip -d GRCh38.primary_assembly.genome.fa.gz
gzip -d gencode.v32.primary_assembly.annotation.gtf.gz

# 3. 过滤 GTF 并构建 STAR 参考库
$dnbc4tools tools mkgtf --ingtf gencode.v32.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools rna mkref --genomeDir /database/scRNA --ingtf genes.filtered.gtf --fasta GRCh38.primary_assembly.genome.fa --threads 10 --species Homo_sapiens
```

**小鼠（Mouse, GRCm38）**
```bash
# 1. 下载注释与基因组 FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/GRCm38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/gencode.vM23.primary_assembly.annotation.gtf.gz

# 2. 解压文件
gzip -d GRCm38.primary_assembly.genome.fa.gz
gzip -d gencode.vM23.primary_assembly.annotation.gtf.gz

# 3. 过滤 GTF 并构建 STAR 参考库
$dnbc4tools tools mkgtf --ingtf gencode.vM23.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools rna mkref --genomeDir /database/scRNA --ingtf genes.filtered.gtf --fasta GRCm38.primary_assembly.genome.fa --threads 10 --species Mus_musculus
```

**人-鼠双物种参考库**
```bash
# 准备好两物种 FASTA 与 GTF 后联合构建
$dnbc4tools rna mkref --genomeDir /database/scRNA \
    --fasta GRCh38.primary_assembly.genome.fa,GRCm38.primary_assembly.genome.fa \
    --ingtf hg38/genes.filtered.gtf,mm10/genes.filtered.gtf \
    --species hg38,mm10 \
    --threads 10
```

### 第二步：准备 RNA 测序数据 {#rna-prepare-inputs}

推荐将测序文件规整放置于包含 `cDNA/` 与 `oligo/` 子目录的路径下，流程将自动识别并配对双端数据：

```text
/test/data/rna_fastqs/          # --fastqs 所指定的根目录
├── cDNA/                       # 存放转录组 cDNA 测序数据
│   ├── sample_cDNA_R1.fastq.gz
│   └── sample_cDNA_R2.fastq.gz
└── oligo/                      # 存放微珠/条形码 Oligo 测序数据
    ├── sample_oligo_R1.fastq.gz
    └── sample_oligo_R2.fastq.gz
```

`--fastqs` 指向同时包含 `cDNA/` 与 `oligo/` 的根目录；本标准示例需要这两类文库的 R1/R2 数据。目录中只放同一样本对应的文库；同一文库的多个测序文件可归入相应子目录，读段结构与暗反应设置须兼容，不要混入其他样本。文件配对规则见[目录自动识别命名规则](#file-naming-conventions)。

### 第三步：执行 RNA 分析 {#rna-run}

**方式一：目录输入方式（推荐）**

```bash
$dnbc4tools rna run \
    --fastqs /test/data/rna_fastqs \
    --genomeDir /database/scRNA/Homo_sapiens \
    --name test_rna \
    --threads 30
```

**方式二：独立显式指定 FASTQ 文件**

当测序文件未按 `cDNA/` 与 `oligo/` 归类归档，或跨多个存储路径时，可使用独立参数逐项指定输入文件（多个文件支持逗号 `,` 分隔）：

```bash
$dnbc4tools rna run \
    --cDNAfastq1 /test/data/rna_fastqs/cDNA/sample_cDNA_R1.fastq.gz \
    --cDNAfastq2 /test/data/rna_fastqs/cDNA/sample_cDNA_R2.fastq.gz \
    --oligofastq1 /test/data/rna_fastqs/oligo/sample_oligo_R1.fastq.gz \
    --oligofastq2 /test/data/rna_fastqs/oligo/sample_oligo_R2.fastq.gz \
    --genomeDir /database/scRNA/Homo_sapiens \
    --name test_rna \
    --threads 30
```

两种输入方式任选一种，不要同时填写 `--fastqs` 和显式 FASTQ 参数。`--name test_rna` 用于任务及报告命名，结果将保存在 `./test_rna/outs/`（亦可使用 `--outdir` 指定其他根目录），`--threads` 设置 CPU 线程数；显式指定多个 R1/R2 文件时，列表顺序须一一对应。

5′ RNA 在所选运行命令中添加 `--end5`，3′ RNA 示例不加该开关。RNA 默认输出 BAM；节省存储时可添加 `--no_bam`，跳过 BAM 及其索引。细胞识别、试剂和暗反应等更多设置见 [RNA 参数说明](parameter/scRNA.md)。

### 第四步：查看 RNA 结果 {#rna-check-outputs}

分析完成后，结果归档于 `./test_rna/outs/`：

* **交互式报告**：直接用浏览器打开 `test_rna_scRNA_report.html` 查看细胞数、测序质控、基因表达与聚类图；
* **定量表达矩阵**：包含 MEX 目录、`.h5` 以及 AnnData `.h5ad`（保存于 `filtered_feature_bc_matrix/` 与 `analysis/QC_Cluster.h5ad`）；
* **质控与单细胞表**：`singlecell.csv`（微珠/液滴明细，筛选有效细胞使用 `is_cell_barcode == 1`）与 `metrics_summary.xls`。

完整输出目录树、文件字段说明及下游加载代码请参阅 [RNA 输出详解](outs/scRNA.md) 与 [在 R / Python 中读取结果](io.md#scrna-analysis)。

---

## 单细胞 ATAC 分析 <a id="single-cell-atac-analysis"></a>

适用于单细胞染色质开放区分析、峰检测（Peak Calling）与质控评估。

### 第一步：构建 ATAC 参考库 {#atac-prepare-reference}

已有兼容参考库时可跳过构建，直接在分析命令中填写完整参考目录。以下物种示例按需选择，并在各自独立的工作目录执行。`mkref --genomeDir /database/scATAC` 指定参考输出根目录，软件会追加物种子目录，生成 `/database/scATAC/Homo_sapiens`、`/database/scATAC/Mus_musculus` 或 `/database/scATAC/hg38_and_mm10`。后续 `run --genomeDir` 应填写该物种目录，而不是输出根目录或原始 FASTA/GTF 文件。混合物种示例中的 `hg38/`、`mm10/` 两份过滤后 GTF 需事先分别准备。

**人（Human, GRCh38）**
```bash
# 1. 下载 GENCODE 注释文件与基因组 FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/GRCh38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/gencode.v32.primary_assembly.annotation.gtf.gz

# 2. 解压文件
gzip -d GRCh38.primary_assembly.genome.fa.gz
gzip -d gencode.v32.primary_assembly.annotation.gtf.gz

# 3. 过滤 GTF 并构建 Chromap 参考库
$dnbc4tools tools mkgtf --ingtf gencode.v32.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools atac mkref --genomeDir /database/scATAC --fasta GRCh38.primary_assembly.genome.fa --ingtf genes.filtered.gtf --species Homo_sapiens --prefix chr
```

**小鼠（Mouse, GRCm38）**
```bash
# 1. 下载注释与基因组 FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/GRCm38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/gencode.vM23.primary_assembly.annotation.gtf.gz

# 2. 解压文件
gzip -d GRCm38.primary_assembly.genome.fa.gz
gzip -d gencode.vM23.primary_assembly.annotation.gtf.gz

# 3. 过滤 GTF 并构建 Chromap 参考库
$dnbc4tools tools mkgtf --ingtf gencode.vM23.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools atac mkref --genomeDir /database/scATAC --fasta GRCm38.primary_assembly.genome.fa --ingtf genes.filtered.gtf --species Mus_musculus --prefix chr
```

**人-鼠双物种参考库**
```bash
# 准备好两物种 FASTA 与过滤后的 GTF 后联合构建（双物种不支持 --prefix 参数）
$dnbc4tools atac mkref --genomeDir /database/scATAC \
    --fasta GRCh38.primary_assembly.genome.fa,GRCm38.primary_assembly.genome.fa \
    --ingtf hg38/genes.filtered.gtf,mm10/genes.filtered.gtf \
    --species hg38,mm10
```

### 第二步：准备 ATAC 测序数据 {#atac-prepare-inputs}

测序数据支持放置于指定目录或显式指定成对 FASTQ：

```text
/test/data/atac_fastqs/          # --fastqs 所指定的根目录
├── sample_R1.fastq.gz
└── sample_R2.fastq.gz
```

`--fastqs` 直接填写该 ATAC 文库的配对 FASTQ 所在目录，无需 `cDNA/` 或 `oligo/` 子目录。不同样本分开运行；同一文库的多个测序文件须保持配对命名、读段结构和暗反应设置兼容，见[目录自动识别命名规则](#file-naming-conventions)。

### 第三步：执行 ATAC 分析 {#atac-run}

**方式一：目录输入方式（推荐）**

```bash
$dnbc4tools atac run \
    --fastqs /test/data/atac_fastqs \
    --genomeDir /database/scATAC/Homo_sapiens \
    --name test_atac \
    --threads 10
```

**方式二：独立显式指定 FASTQ 文件**

```bash
$dnbc4tools atac run \
    --fastq1 /test/data/atac_fastqs/sample_R1.fastq.gz \
    --fastq2 /test/data/atac_fastqs/sample_R2.fastq.gz \
    --genomeDir /database/scATAC/Homo_sapiens \
    --name test_atac \
    --threads 10
```

两种输入方式任选一种，不要同时填写 `--fastqs` 和显式 FASTQ 参数。`--name test_atac` 用于任务及报告命名，结果将保存在 `./test_atac/outs/`（亦可使用 `--outdir` 指定其他根目录），`--threads` 设置 CPU 线程数；显式指定多个 R1/R2 文件时，列表顺序须一一对应。

参考库须由 `atac mkref` 构建，不能使用 RNA 的 STAR 参考目录替代。需要 BAM 时添加 `--need_bam`；细胞识别和峰检测的更多设置见 [ATAC 参数说明](parameter/scATAC.md)。

### 第四步：查看 ATAC 结果 {#atac-check-outputs}

分析完成后，结果归档于 `./test_atac/outs/`：

* **交互式报告**：直接用浏览器打开 `test_atac_scATAC_report.html` 查看细胞召回数、TSS 富集曲线及 FRIP 质控指标；
* **Peak 计数矩阵**：包含 `filtered_peak_bc_matrix/`（MEX 格式）与 `filtered_peak_bc_matrix.h5`（经 9-bp 偏移 cutsite 计数）；
* **片段文件**：`fragments.tsv.gz` 与 `filtered.fragments.tsv.gz`（均附带 `.tbi` 索引，直通下游 ArchR / Signac / SnapATAC2）。

完整输出目录树、文件字段说明及下游加载代码请参阅 [ATAC 输出详解](outs/scATAC.md) 与 [在 R / Python 中读取结果](io.md#scatac-analysis)。

---

## 单细胞 V(D)J 分析 <a id="single-cell-vdj-analysis"></a>

适用于 TCR / BCR 免疫受体全长序列从头组装、注释与克隆型识别。

<div class="doc-callout doc-callout-warn" markdown="block">
<strong>VDJ 运行模式：</strong> 支持两种模式：提供 `--beadstrans` 时，使用 RNA 细胞表进行微珠映射及基于 RNA 的细胞过滤；省略时，可在没有 RNA 细胞表的情况下运行 VDJ。省略该参数会自动启用 `keep_all_cells`，不按 RNA 细胞识别结果过滤组装条形码，因此不能将这些条形码视为 RNA 已确认的细胞集合。
</div>

以下步骤演示**RNA 关联模式**。若已有对应细胞表，可直接复用，无需为了此示例重新运行 RNA。

### 第一步：准备 VDJ 数据与参考库 {#vdj-prepare-inputs}

TCR 和 BCR 文库分别放在独立目录中，以下目录与后面的命令对应：

```text
/test/data/
├── tcr_fastqs/
│   ├── sample_TCR_R1.fastq.gz
│   └── sample_TCR_R2.fastq.gz
└── bcr_fastqs/
    ├── sample_BCR_R1.fastq.gz
    └── sample_BCR_R2.fastq.gz
```

| 参数或输入 | 说明 |
| :--- | :--- |
| `--fastqs` | 填对应 TCR 或 BCR 文库的配对 FASTQ 目录，不混放两类文库。也可改用 `--fastq1` 与 `--fastq2` 显式指定，双端列表顺序须对应。 |
| `--ref` | 人填写 `human`，小鼠填写 `mouse`；这两个值为软件参考库标识，不是路径。自建参考填写包含 `reference.json` 的 VDJ 参考目录，不能直接填写 FASTA 或 RNA / ATAC 参考目录。 |
| `--chain` | TCR 使用 `TR`，BCR 使用 `IG`；须与输入文库对应。 |
| `--beadstrans` | RNA 关联模式使用同一实验对应的 RNA `outs/singlecell.csv`，不是表达矩阵、`barcodes.tsv.gz` 或其他样本的细胞表。无 RNA 模式省略此参数。 |

`/test/data/...` 是待替换的示例路径。目录命名与配对规则见[输入命名规则](#file-naming-conventions)，自建参考要求见 [VDJ 参数说明](parameter/scVDJ.md)。

### 第二步：准备 RNA 细胞表（仅 RNA 关联模式） {#vdj-prepare-rna}

已有对应 RNA `singlecell.csv` 时直接复用，跳过以下命令。否则先按 [RNA 输入目录结构](#rna-prepare-inputs)准备 `/test/data/rna_5p_fastqs`，再运行对应的 5′ RNA 数据；选择[无 RNA 模式](#vdj-without-rna)时直接跳过本步。

```bash
$dnbc4tools rna run \
    --fastqs /test/data/rna_5p_fastqs \
    --genomeDir /database/scRNA/Homo_sapiens \
    --name test_rna_5p \
    --threads 30 \
    --end5
```

### 第三步：执行 VDJ 分析 {#vdj-run}

RNA 关联模式使用上一步生成的 `./test_rna_5p/outs/singlecell.csv`，或将 `--beadstrans` 替换为已有的对应细胞表路径。目录输入与显式指定文件任选一种，不要混用。

**方式一：目录输入方式（推荐）**

*人 TCR 分析（Human TCR）*
```bash
$dnbc4tools vdj run \
    --fastqs /test/data/tcr_fastqs \
    --beadstrans ./test_rna_5p/outs/singlecell.csv \
    --ref human \
    --name test_human_tcr \
    --threads 20 \
    --chain TR
```

*人 BCR 分析（Human BCR）*
```bash
$dnbc4tools vdj run \
    --fastqs /test/data/bcr_fastqs \
    --beadstrans ./test_rna_5p/outs/singlecell.csv \
    --ref human \
    --name test_human_bcr \
    --threads 20 \
    --chain IG
```

**方式二：独立显式指定 FASTQ 文件**

当测序文件不在同一目录或有特殊路径时，可通过 `--fastq1` 与 `--fastq2` 逐项显式输入：

*人 TCR 分析（独立文件输入）*
```bash
$dnbc4tools vdj run \
    --fastq1 /test/data/tcr_fastqs/sample_TCR_R1.fastq.gz \
    --fastq2 /test/data/tcr_fastqs/sample_TCR_R2.fastq.gz \
    --beadstrans ./test_rna_5p/outs/singlecell.csv \
    --ref human \
    --name test_human_tcr \
    --threads 20 \
    --chain TR
```

*人 BCR 分析（独立文件输入）*
```bash
$dnbc4tools vdj run \
    --fastq1 /test/data/bcr_fastqs/sample_BCR_R1.fastq.gz \
    --fastq2 /test/data/bcr_fastqs/sample_BCR_R2.fastq.gz \
    --beadstrans ./test_rna_5p/outs/singlecell.csv \
    --ref human \
    --name test_human_bcr \
    --threads 20 \
    --chain IG
```

<details markdown="block">
<summary>点击展开：小鼠（Mouse）TCR 与 BCR 分析示例</summary>

以下示例假设已有 `./test_mouse_rna_5p/outs/singlecell.csv`。请替换为实际路径，并确保输入 FASTQ、参考库与 RNA 细胞表均对应小鼠实验。


**小鼠 TCR 分析**
```bash
$dnbc4tools vdj run \
    --fastqs /test/data/mouse_tcr_fastqs \
    --beadstrans ./test_mouse_rna_5p/outs/singlecell.csv \
    --ref mouse \
    --name test_mouse_tcr \
    --threads 20 \
    --chain TR
```

**小鼠 BCR 分析**
```bash
$dnbc4tools vdj run \
    --fastqs /test/data/mouse_bcr_fastqs \
    --beadstrans ./test_mouse_rna_5p/outs/singlecell.csv \
    --ref mouse \
    --name test_mouse_bcr \
    --threads 20 \
    --chain IG
```

</details>

#### 无 RNA 细胞表的 VDJ 分析 {#vdj-without-rna}

省略 `--beadstrans` 即可使用此模式，无需先运行 RNA；仍需准备 VDJ 测序文件与对应参考库。

```bash
$dnbc4tools vdj run \
    --fastqs /test/data/tcr_fastqs \
    --ref human \
    --name test_vdj_without_rna \
    --threads 20 \
    --chain TR
```

软件会自动启用 `keep_all_cells`。统计细胞数或与 RNA 结果比较前，应结合 VDJ 注释标记进行筛选与核验。

### 第四步：查看 VDJ 结果 {#vdj-check-outputs}

分析完成后，结果归档于 `./<name>/outs/`（如 `./test_human_tcr/outs/`）：

* **交互式报告**：浏览器打开 `*_report.html` 查看组装率、生产性（Productive）重叠群比例与免疫克隆型丰度分布；
* **组装与注释**：核心注释文件为 `filtered_contig_annotations.csv`，组装序列为 `filtered_contig.fasta`；
* **免疫生态兼容**：提供标准 `clonotypes.csv` 与 `airr_annotations.tsv`（可直接导入 `scRepertoire` 或 `immunarch`）。

完整文件清单与注释字段解读请参阅 [VDJ 输出详解](outs/scVDJ.md) 与 [在 R / Python 中读取结果](io.md#scvdj-analysis)。

---

## 多组学联合分析 <a id="integrated-multi-omics-analysis"></a>

通过一份配置文件调度 RNA、ATAC、TCR 和 BCR 文库分析，并生成组合报告。下面以**同一生物学样本的 5′ RNA + ATAC + TCR + BCR** 为例；按实际实验保留需要的组学，无需准备全部四类文库。多个独立样本应分别配置、运行；基于 Sample Barcode 混合的 C6 RNA 数据请使用下方的 [C6 多样本分析](#c6-multi-sample-analysis)。

!!! note "联合分析范围"
    RNA 与 V(D)J 可关联细胞信息；ATAC 当前独立分析后汇总到组合报告。该命令不执行 RNA + ATAC 联合降维或聚类。

### 第一步：准备测序数据与参考库 {#multi-prepare-inputs}

将同一样本的各类文库分别放在独立目录中，示例如下：

```text
/test/data/
├── rna/
│   ├── cDNA/
│   │   ├── sample_cDNA_R1.fastq.gz
│   │   └── sample_cDNA_R2.fastq.gz
│   └── oligo/
│       ├── sample_oligo_R1.fastq.gz
│       └── sample_oligo_R2.fastq.gz
├── atac/
│   ├── sample_ATAC_R1.fastq.gz
│   └── sample_ATAC_R2.fastq.gz
├── vdj-t/
│   ├── sample_TCR_R1.fastq.gz
│   └── sample_TCR_R2.fastq.gz
└── vdj-b/
    ├── sample_BCR_R1.fastq.gz
    └── sample_BCR_R2.fastq.gz
```

- **RNA**：`fastqs` 填 `/test/data/rna`，即包含 `cDNA/` 与 `oligo/` 的根目录，不要填到 `cDNA/` 或单个 FASTQ 文件。
- **ATAC、TCR、BCR**：分别填写存放对应文库配对 FASTQ 的目录。TCR 和 BCR 分开存放；文件命名与配对规则见[目录自动识别命名规则](#file-naming-conventions)。
- **每种组学仅支持一个 FASTQ 根目录**，且在 `[libraries]` 中只能出现一次。同一文库有多个测序文件时，将匹配的 R1/R2 文件归入对应目录，并保持读段结构及暗反应设置兼容；不要混入其他样本或无关文库的数据。
- **RNA / ATAC 参考库**：分别使用已由 `rna mkref`、`atac mkref` 构建好的参考目录，不能直接填写 FASTA、GTF 或其所在的原始文件目录。构建方法见上文 [RNA](#single-cell-rna-analysis) 和 [ATAC](#single-cell-atac-analysis)。
- **VDJ 参考库**：人、小鼠可分别填写 `human`、`mouse`；自建参考填写包含 `reference.json` 的 VDJ 参考目录，参见 [VDJ 参数说明](parameter/scVDJ.md)。

以上 `/test/data/...` 和下方 `/database/...` 均为示例路径，运行前须替换为本机实际存在的数据和参考目录。

### 第二步：编写多组学配置文件 {#multi-prepare-config}

将以下内容保存为纯文本文件 `multi.config.csv`。配置采用 `[分段]` 加逗号分隔内容：`[libraries]` 保留表头，其余组学分段按 `参数名,值` 填写。

```csv
[libraries]
fastqs,feature_types
/test/data/rna,rna
/test/data/atac,atac
/test/data/vdj-t,vdj-t
/test/data/vdj-b,vdj-b

[rna]
genomeDir,/database/scRNA/Homo_sapiens
end5,true

[atac]
genomeDir,/database/scATAC/Homo_sapiens

[vdj-t]
ref,human

[vdj-b]
ref,human
```

| 配置项 | 含义与填写方式 |
| :--- | :--- |
| `[libraries] fastqs` | 对应文库的 FASTQ 根目录，目录结构见上方示例。 |
| `[libraries] feature_types` | `rna`、`atac`、`vdj-t`（TCR）或 `vdj-b`（BCR）；须与对应组学分段一致。 |
| `[rna] genomeDir` / `[atac] genomeDir` | 各自已经构建完成的参考库目录；RNA 与 ATAC 参考目录分别填写。 |
| `[rna] end5,true` | 表示本例使用 5′ RNA 数据。3′ RNA 不应照抄此设置，可删除该行。 |
| `[vdj-t] ref` / `[vdj-b] ref` | VDJ 参考物种标识或自建参考库目录；本例 `human` 是物种标识，不是文件路径。 |

**按实际文库删减配置**：例如仅做 RNA + TCR 时，删除 `[libraries]` 中 `atac`、`vdj-b` 两行，以及整个 `[atac]`、`[vdj-b]` 分段。仅声明实际提供的文库，不要保留空路径。启用 5′ RNA 且其细胞表正常生成时，VDJ 默认使用本次 RNA 细胞表，无需提前单独运行 RNA 或手动填写 `beadstrans`。

**路径解析规则**：配置文件内的相对路径，以 `multi.config.csv` 所在目录为基准；建议初次运行使用绝对路径。例如 CSV 位于 `/project/config/multi.config.csv`，其中的 `../fastqs/rna` 会解析为 `/project/fastqs/rna`。命令行中的 `--csv`、`--outdir` 相对路径则以执行命令时的当前目录为基准。

其他组学参数、布尔值与含逗号的值如何填写，参见 [Multi 参数说明](parameter/multi.md)。

### 第三步：执行多组学分析 {#multi-run}

在保存 `multi.config.csv` 的目录下运行：

```bash
$dnbc4tools multi run \
    --name test_multi \
    --csv ./multi.config.csv \
    --threads 20
```

这里 `--name test_multi` 为任务名，默认在当前目录生成 `./test_multi/outs/`（亦可添加 `--outdir` 指定其他根目录）；`--threads 20` 设置使用的 CPU 线程数。

### 第四步：查看运行结果 {#multi-check-outputs}

分析完成后，结果统一归档于 `./test_multi/outs/`：

* **组合交互式报告**：直接用浏览器打开 `test_multi_multi_report.html`，集中查看 RNA、ATAC、TCR 与 BCR 的跨组学联合质控；
* **独立模态目录**：各组学结果完全解耦归档于独立子目录（`rna/`、`atac/`、`vdj-t/`、`vdj-b/`），结构与单组学输出完全一致，可独立使用；
* **执行清单审计**：`logs/run_manifest.json` 记录了各模态的执行耗时与状态。

完整子目录结构与文件说明请参阅 [多组学输出详解](outs/multi.md)。

---

## C6 多样本单细胞 RNA 分析 <a id="c6-multi-sample-analysis"></a>

适用于实验端使用 Sample Barcode 标记并混合建库的 C6 RNA 数据：多个生物学样本共用一套 cDNA 与 Oligo 测序数据，软件根据配置中的条形码归属拆分样本，再分别进行细胞识别、计数和下游分析。若各样本本来就是独立文库、独立 FASTQ，请使用[单样本 RNA 分析](#single-cell-rna-analysis)或[批量分析脚本生成](#batch-script-generation)。

### 第一步：准备共享测序数据、参考库与样本对应表 {#c6-prepare-inputs}

将**同一套 C6 混合文库**的 cDNA 与 Oligo 双端数据分别放入以下目录：

```text
/test/data/c6_pooled_data/
├── cDNA/
│   ├── pooled_cDNA_R1.fastq.gz
│   └── pooled_cDNA_R2.fastq.gz
└── oligo/
    ├── pooled_oligo_R1.fastq.gz
    └── pooled_oligo_R2.fastq.gz
```

- **共享 FASTQ 根目录**：`[libraries] fastqs` 填 `/test/data/c6_pooled_data`，不要填到 `cDNA/`、`oligo/` 或单个 FASTQ 文件。所有样本共用这一行输入，不需要按样本建立 FASTQ 目录或重复填写 `rna` 行。
- **多文件输入**：同一混合文库有多个测序文件时，将配对文件归入对应的 `cDNA/`、`oligo/` 目录。读段结构和暗反应设置须兼容，文件命名见[目录自动识别命名规则](#file-naming-conventions)。不同混合文库应分别配置、运行。
- **参考库**：准备已由 `rna mkref` 构建完成的参考目录。`genomeDir` 填参考库目录，不是 FASTA、GTF 文件；构建方法见上文 [RNA 参考库构建](#single-cell-rna-analysis)。
- **样本对应表**：从实验记录确认每个生物学样本使用的 Sample Barcode。下方 `Sample_01 → BC01`、`Sample_02 → BC02;BC03` 仅为示例，必须改为实际归属，不能根据样本顺序推定条形码。

`/test/data/c6_pooled_data` 和 `/database/scRNA/Homo_sapiens` 均为示例路径，运行前须替换为本机实际存在的数据和参考目录。

### 第二步：编写 C6 配置文件 {#c6-prepare-config}

将以下内容保存为纯文本文件 `sample.config.csv`，保留三个分段及两个表头：

```csv
[rna]
genomeDir,/database/scRNA/Homo_sapiens
chemistry,scRNAC6
darkreaction,auto
no_bam,false

[libraries]
fastqs,feature_types
/test/data/c6_pooled_data,rna

[samples]
sample_id,probe_barcode_ids
Sample_01,BC01
Sample_02,BC02;BC03
```

| 配置项 | 含义与填写方式 |
| :--- | :--- |
| `[rna] genomeDir` | RNA 参考库目录。 |
| `[rna] chemistry,scRNAC6` | C6 试剂读段结构；有 `[samples]` 时固定使用 `scRNAC6`，省略也会归一化为此值。 |
| `[rna] darkreaction,auto` | 自动检测 cDNA 与 Oligo 暗反应；不用于选择试剂版本。 |
| `[rna] no_bam,false` | 保留默认 BAM 输出。节省存储时改为 `true`，将跳过逐样本、未分配及 Oligo BAM 和相应索引。 |
| `[libraries] fastqs` / `feature_types` | 共享 FASTQ 根目录与文库类型；本例只填一行，类型为 `rna`。 |
| `[samples] sample_id` | 生物学样本名，用于各样本输出目录和报告命名，不要求与 FASTQ 文件名一致。 |
| `[samples] probe_barcode_ids` | 该样本实际使用的 Sample Barcode ID；同一样本的多个 ID 用英文分号 `;` 分隔。 |

**样本表填写规则**：每个生物学样本一行；例如本例将 `BC02`、`BC03` 的数据合并归入 `Sample_02`，不会生成两个独立样本。样本名须唯一（不区分大小写），以字母或数字开头，其余仅用字母、数字、`.`、`_`、`-`；不能使用保留名 `unassigned` 或 `non_multiplexed`。同一条形码不能重复填写，也不能分配给多个样本。可用内置 ID 或自定义 DNA 序列，详细规则见 [C6 样本表说明](parameter/c6.md#samples-specification)。

**路径解析规则**：配置内的相对路径按 `sample.config.csv` 所在目录解析；命令行中的 `--csv`、`--outdir` 相对路径按执行命令时的当前目录解析。初次运行建议在配置中使用绝对路径。

**可选细胞识别设置**：需要按样本设置预期细胞数等参数时，可在 `[samples]` 表头增加 `expectcells`、`forcecells`、`minumi`，填写对应正整数；留空继承全局设置，不要将全批次预期细胞数复制给每个样本。`high_occupancy_filter` 是实验级开关，默认开启，只能写在 `[rna]` 中。完整示例见 [C6 参数说明](parameter/c6.md#sample-overrides)。

### 第三步：执行 C6 分析 {#c6-run}

在保存 `sample.config.csv` 的目录下运行：

```bash
$dnbc4tools multi run \
    --name test_c6 \
    --csv ./sample.config.csv \
    --threads 40
```

`--name test_c6` 是整次混合文库任务的名称，与 `[samples]` 中的 `Sample_01`、`Sample_02` 不同。上述命令将结果写入当前目录下的 `./test_c6/outs/`（亦可添加 `--outdir` 指定其他输出根目录），使用 40 个 CPU 线程。

### 第四步：查看全局与各样本结果 {#c6-check-outputs}

分析完成后，结果归档于 `./test_c6/outs/`：

* **批次汇总报告**：浏览器打开 `test_c6_multi_report.html` 查看混合文库整体质控、Sample Barcode 拆分分配率及各样本细胞数对比；
* **逐样本独立交付**：每个样本在 `rna/per_sample_outs/<sample>/` 拥有专属结果，包含独立交互式报告（`<sample>_scRNA_report.html`）、定量矩阵（MEX / `.h5` / `.h5ad`）及比对 BAM（若启用）；
* **物理文库总矩阵**：`rna/filtered_feature_bc_matrix/`（及同名 `.h5` / `.h5ad`）保留物理文库合并原始计数。

完整多样本层级目录树与下游分析注意事项请参阅 [C6 输出详解](outs/c6.md) 与 [在 R / Python 中读取结果](io.md#c6-analysis)。

---

## 批量分析脚本生成 <a id="batch-script-generation"></a>

适用于需要批量处理大量独立单样本的场景。通过提供样本清单 TSV 文件，自动为每个样本生成独立的 Shell 执行脚本，后续可在终端或计算集群调度系统（如 Slurm、SGE）中排队运行。

### 第一步：准备样本清单文件

**RNA 样本清单 (`rna_samples.tsv`)**

制表符 `\t` 分隔 3 列：`样本名`、`cDNA_R1;cDNA_R2`、`oligo_R1;oligo_R2`（同端多个 FASTQ 文件用逗号 `,` 分隔）：

```text
Sample1	sample1_cDNA_R1.fq.gz;sample1_cDNA_R2.fq.gz	sample1_oligo_R1.fq.gz;sample1_oligo_R2.fq.gz
Sample2	sample2_cDNA_R1.fq.gz;sample2_cDNA_R2.fq.gz	sample2_oligo_R1.fq.gz;sample2_oligo_R2.fq.gz
```

**ATAC 样本清单 (`atac_samples.tsv`)**

制表符 `\t` 分隔 2 列：`样本名`、`FASTQ_R1;FASTQ_R2`（同端多个 FASTQ 文件用逗号 `,` 分隔）：

```text
Sample1	sample1_R1.fq.gz;sample1_R2.fq.gz
Sample2	sample2_R1.fq.gz;sample2_R2.fq.gz
```

### 第二步：生成分析脚本

```bash
# 批量生成 RNA 样本执行脚本
$dnbc4tools rna multi \
    --list ./rna_samples.tsv \
    --genomeDir /database/scRNA/Homo_sapiens \
    --threads 20

# 批量生成 ATAC 样本执行脚本
$dnbc4tools atac multi \
    --list ./atac_samples.tsv \
    --genomeDir /database/scATAC/Homo_sapiens \
    --threads 20
```

> **执行机制说明：**
> `multi` 命令仅在当前工作目录下为清单中的每个样本生成独立的 `.sh` 脚本（如 `run_Sample1.sh`），不自动启动计算。生成完毕后，可按需执行脚本（如 `sh run_Sample1.sh`）或批量提交至集群作业队列。

---

快速入门完成后，您可以根据分析需求查阅更深入的模块文档：

* 查阅各模块完整运行机制：[分析流程总览](./pipeline/pipeline.md)
* 探索高级参数与资源调优：[参数配置总览](./parameter/parameter.md)
* 查看各模块详细交付物结构：[输出结果总览](./outs/outs.md)
