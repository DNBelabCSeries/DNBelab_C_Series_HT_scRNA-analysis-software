# Quick Start Guide

This guide provides end-to-end operational walkthroughs for the DNBelab C Series™ single-cell analysis suite (dnbc4tools), covering system prerequisites, reference genome indexing, single-modality pipelines, integrated multi-omics orchestration, C6 multiplexed single-cell RNA analysis, and batch analysis script generation.

---

## Choose a Workflow <a id="choose-workflow"></a>

Select the appropriate command entry point according to your experimental design and library preparation:

| Workflow | Command Entry Point | Scope & Description |
| :--- | :--- | :--- |
| [**Single-Cell RNA Analysis**](#single-cell-rna-analysis) | `dnbc4tools rna run` | Single-sample gene expression quantification, EmptyDrops cell calling, and clustering |
| [**Single-Cell ATAC Analysis**](#single-cell-atac-analysis) | `dnbc4tools atac run` | Single-sample chromatin accessibility analysis, peak calling, and QC |
| [**Single-Cell V(D)J Analysis**](#single-cell-vdj-analysis) | `dnbc4tools vdj run` | De novo assembly of full-length TCR / BCR sequences, annotation, and clonotype identification |
| [**Integrated Multi-Omics**](#integrated-multi-omics-analysis) | `dnbc4tools multi run --csv multi.config.csv` | Unified orchestration and cross-modality reporting for RNA + ATAC + VDJ |
| [**C6 Multiplexed RNA**](#c6-multi-sample-analysis) | `dnbc4tools multi run --csv sample.config.csv` | Sample Barcode pooled RNA-seq demultiplexing and per-sample dedicated delivery |
| [**Batch Script Generation**](#batch-script-generation) | `dnbc4tools <rna/atac> multi` | Batch-generate standalone analysis scripts for queued HPC scheduling |

---

## Prerequisites <a id="prerequisites"></a>

<div class="doc-callout doc-callout-info" markdown="block">
<strong>Before you begin:</strong>
<ul style="margin-bottom: 0;">
  <li><strong>Environment & Paths</strong>: Ensure software installation is verified (see <a href="./installation.html">Installation Guide</a>). Replace placeholder paths like <code>$dnbc4tools</code>, <code>/test/data/...</code>, and <code>/database/...</code> with actual paths on your system.</li>
  <li><strong>Output Directory</strong>: By default, a task directory named after <code>--name</code> is created under the current working directory (results saved in <code>./&lt;name&gt;/outs/</code>). You can also explicitly specify a custom output root via <code>--outdir</code>.</li>
</ul>
</div>

### `--fastqs` Directory Auto-Detection Rules <a id="file-naming-conventions"></a>

When using directory-based input via `--fastqs <dir>`, the pipeline automatically scans the folder and pairs paired-end reads matching the following patterns:

| Read End | Match Pattern | Example Filenames |
| :--- | :--- | :--- |
| **Read 1 (R1)** | Contains `_R1_`, `_R1`, `_1`, or `_read1` | `sample_R1.fastq.gz`, `sample_1.fq.gz`, `sample_R1_001.fastq.gz` |
| **Read 2 (R2)** | Contains `_R2_`, `_R2`, `_2`, or `_read2` | `sample_R2.fastq.gz`, `sample_2.fq.gz`, `sample_R2_001.fastq.gz` |

* **Supported Extensions**: `.fastq.gz`, `.fq.gz`, `.fastq`, `.fq`
* **Explicit File Arguments Bypass Naming Restrictions**: If files are provided via explicit flags (e.g., `--fastq1/--fastq2` or RNA `--cDNAfastq1/2`, `--oligofastq1/2`), file names do not need to follow these patterns, but the list ordering between paired reads must match strictly.

---

## Single-Cell RNA Analysis <a id="single-cell-rna-analysis"></a>

Designed for standard single-sample 3′ or 5′ single-cell transcriptomic profiling and clustering.

### Step 1: Build Reference Genome {#rna-prepare-reference}

If a compatible reference is already available, skip rebuilding and use its complete directory in the run command. Choose the appropriate species example below and run it in a separate working directory. `mkref --genomeDir /database/scRNA` specifies the reference output root; the software adds a species subdirectory, producing `/database/scRNA/Homo_sapiens`, `/database/scRNA/Mus_musculus`, or `/database/scRNA/hg38_and_mm10`. Pass that species directory to `run --genomeDir`, not the output root or an original FASTA/GTF file. For the mixed-species example, prepare the two filtered GTF files at the indicated `hg38/` and `mm10/` paths first.

Using Human, Mouse, and Human-Mouse dual-species as common references:

**Human (GRCh38)**
```bash
# 1. Download GENCODE annotation and genomic FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/GRCh38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/gencode.v32.primary_assembly.annotation.gtf.gz

# 2. Decompress files
gzip -d GRCh38.primary_assembly.genome.fa.gz
gzip -d gencode.v32.primary_assembly.annotation.gtf.gz

# 3. Filter GTF and generate STAR genome index
$dnbc4tools tools mkgtf --ingtf gencode.v32.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools rna mkref --genomeDir /database/scRNA --ingtf genes.filtered.gtf --fasta GRCh38.primary_assembly.genome.fa --threads 10 --species Homo_sapiens
```

**Mouse (Mus musculus, GRCm38)**
```bash
# 1. Download annotation and FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/GRCm38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/gencode.vM23.primary_assembly.annotation.gtf.gz

# 2. Decompress files
gzip -d GRCm38.primary_assembly.genome.fa.gz
gzip -d gencode.vM23.primary_assembly.annotation.gtf.gz

# 3. Filter GTF and generate STAR genome index
$dnbc4tools tools mkgtf --ingtf gencode.vM23.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools rna mkref --genomeDir /database/scRNA --ingtf genes.filtered.gtf --fasta GRCm38.primary_assembly.genome.fa --threads 10 --species Mus_musculus
```

**Human-Mouse Mixed-Species Reference**
```bash
# Combine FASTA and GTF after preparing both species
$dnbc4tools rna mkref --genomeDir /database/scRNA \
    --fasta GRCh38.primary_assembly.genome.fa,GRCm38.primary_assembly.genome.fa \
    --ingtf hg38/genes.filtered.gtf,mm10/genes.filtered.gtf \
    --species hg38,mm10 \
    --threads 10
```

### Step 2: Prepare RNA Sequencing Data {#rna-prepare-inputs}

Organize your sequencing files under structured subdirectories containing `cDNA/` and `oligo/`. The pipeline will automatically identify and pair FASTQ files:

```text
/test/data/rna_fastqs/          # Root directory passed to --fastqs
├── cDNA/                       # Transcriptomic cDNA sequencing reads
│   ├── sample_cDNA_R1.fastq.gz
│   └── sample_cDNA_R2.fastq.gz
└── oligo/                      # Bead/barcode Oligo sequencing reads
    ├── sample_oligo_R1.fastq.gz
    └── sample_oligo_R2.fastq.gz
```

`--fastqs` points to the root containing both `cDNA/` and `oligo/`; all four paired input streams are required for this standard example. Keep data from one sample/library in the directory. Multiple files from the same library may be placed in the corresponding subdirectories, with compatible read structures and dark-cycle settings. Do not mix unrelated samples. See the [filename pairing rules](#file-naming-conventions).

### Step 3: Run RNA Analysis {#rna-run}

**Method 1: Directory Input (Recommended)**

```bash
$dnbc4tools rna run \
    --fastqs /test/data/rna_fastqs \
    --genomeDir /database/scRNA/Homo_sapiens \
    --name test_rna \
    --threads 30
```

**Method 2: Explicit Individual FASTQ Inputs**

When sequencing files are not grouped into `cDNA/` and `oligo/` subdirectories, or are distributed across separate storage paths, specify each input file explicitly using dedicated arguments (comma-separated lists supported):

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

Choose one input method; do not combine `--fastqs` with explicit FASTQ arguments. `--name test_rna` names the run and report, results are stored in `./test_rna/outs/` (use `--outdir` to customize the root), and `--threads` sets the CPU thread count. Explicit R1/R2 lists must match in order.

For 5′ RNA, add `--end5` to the chosen run command; leave it off for the 3′ example. BAM output is enabled by default. Add the flag `--no_bam` to omit BAM files and their indexes when saving storage. Further cell-calling and library options are described in [RNA parameters](parameter/scRNA.md).

### Step 4: Inspect RNA Outputs {#rna-check-outputs}

Upon completion, results are stored in `./test_rna/outs/`:

* **Interactive Report**: Open `test_rna_scRNA_report.html` in a web browser to review cell counts, sequencing QC, gene expression, and clustering charts;
* **Quantification Matrices**: Standard MEX directory, `.h5`, and AnnData `.h5ad` formats (located in `filtered_feature_bc_matrix/` and `analysis/QC_Cluster.h5ad`);
* **QC & Single-Cell Metadata**: `singlecell.csv` (bead/droplet metrics; filter cells via `is_cell_barcode == 1`) and `metrics_summary.xls`.

For the complete directory structure, metric explanations, and programmatic loading examples, see [scRNA Output Details](outs/scRNA.md) and [Reading Results in R / Python](io.md#scrna-analysis).

---

## Single-Cell ATAC Analysis <a id="single-cell-atac-analysis"></a>

Designed for single-cell chromatin accessibility analysis, peak calling, and quality control.

### Step 1: Build ATAC Reference {#atac-prepare-reference}

If a compatible reference is already available, skip rebuilding and use its complete directory in the run command. Choose the appropriate species example below and run it in a separate working directory. `mkref --genomeDir /database/scATAC` specifies the reference output root; the software adds a species subdirectory, producing `/database/scATAC/Homo_sapiens`, `/database/scATAC/Mus_musculus`, or `/database/scATAC/hg38_and_mm10`. Pass that species directory to `run --genomeDir`, not the output root or an original FASTA/GTF file. For the mixed-species example, prepare the two filtered GTF files at the indicated `hg38/` and `mm10/` paths first.

**Human (GRCh38)**
```bash
# 1. Download GENCODE annotation and genomic FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/GRCh38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_32/gencode.v32.primary_assembly.annotation.gtf.gz

# 2. Decompress files
gzip -d GRCh38.primary_assembly.genome.fa.gz
gzip -d gencode.v32.primary_assembly.annotation.gtf.gz

# 3. Filter GTF and build Chromap reference index
$dnbc4tools tools mkgtf --ingtf gencode.v32.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools atac mkref --genomeDir /database/scATAC --fasta GRCh38.primary_assembly.genome.fa --ingtf genes.filtered.gtf --species Homo_sapiens --prefix chr
```

**Mouse (Mus musculus, GRCm38)**
```bash
# 1. Download annotation and FASTA
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/GRCm38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M23/gencode.vM23.primary_assembly.annotation.gtf.gz

# 2. Decompress files
gzip -d GRCm38.primary_assembly.genome.fa.gz
gzip -d gencode.vM23.primary_assembly.annotation.gtf.gz

# 3. Filter GTF and build Chromap reference index
$dnbc4tools tools mkgtf --ingtf gencode.vM23.primary_assembly.annotation.gtf --output genes.filtered.gtf
$dnbc4tools atac mkref --genomeDir /database/scATAC --fasta GRCm38.primary_assembly.genome.fa --ingtf genes.filtered.gtf --species Mus_musculus --prefix chr
```

**Human-Mouse Mixed-Species Reference**
```bash
# Combine FASTA and filtered GTF after preparing both species (--prefix is not supported for mixed-species)
$dnbc4tools atac mkref --genomeDir /database/scATAC \
    --fasta GRCh38.primary_assembly.genome.fa,GRCm38.primary_assembly.genome.fa \
    --ingtf hg38/genes.filtered.gtf,mm10/genes.filtered.gtf \
    --species hg38,mm10
```

### Step 2: Prepare ATAC Sequencing Data {#atac-prepare-inputs}

Place sequencing files in a designated folder or provide paired-end files explicitly:

```text
/test/data/atac_fastqs/          # Root directory passed to --fastqs
├── sample_R1.fastq.gz
└── sample_R2.fastq.gz
```

`--fastqs` points directly to the directory containing this ATAC library's paired FASTQs; no `cDNA/` or `oligo/` layout is needed. Keep unrelated samples separate. Multiple files from one library must have matching paired-file names and compatible read structures and dark-cycle settings; see the [filename pairing rules](#file-naming-conventions).

### Step 3: Run ATAC Analysis {#atac-run}

**Method 1: Directory Input (Recommended)**

```bash
$dnbc4tools atac run \
    --fastqs /test/data/atac_fastqs \
    --genomeDir /database/scATAC/Homo_sapiens \
    --name test_atac \
    --threads 10
```

**Method 2: Explicit Individual FASTQ Inputs**

```bash
$dnbc4tools atac run \
    --fastq1 /test/data/atac_fastqs/sample_R1.fastq.gz \
    --fastq2 /test/data/atac_fastqs/sample_R2.fastq.gz \
    --genomeDir /database/scATAC/Homo_sapiens \
    --name test_atac \
    --threads 10
```

Choose one input method; do not combine `--fastqs` with explicit FASTQ arguments. `--name test_atac` names the run and report, results are stored in `./test_atac/outs/` (use `--outdir` to customize the root), and `--threads` sets the CPU thread count. Explicit R1/R2 lists must match in order.

The reference must be an ATAC reference built with `atac mkref`; an RNA STAR reference is not interchangeable. BAM output requires `--need_bam`. See [ATAC parameters](parameter/scATAC.md) for cell-calling and peak-calling settings.

### Step 4: Inspect ATAC Outputs {#atac-check-outputs}

Upon completion, results are stored in `./test_atac/outs/`:

* **Interactive Report**: Open `test_atac_scATAC_report.html` in a web browser to review cell calling counts, TSS enrichment curves, and FRIP QC metrics;
* **Peak Count Matrices**: MEX directory (`filtered_peak_bc_matrix/`) and `.h5` file based on 9-bp shifted cutsite quantification;
* **Fragment Files**: `fragments.tsv.gz` and `filtered.fragments.tsv.gz` (both indexed with `.tbi`, ready for ArchR / Signac / SnapATAC2).

For the complete directory layout, field descriptions, and downstream analysis workflows, see [scATAC Output Details](outs/scATAC.md) and [Reading Results in R / Python](io.md#scatac-analysis).

---

## Single-Cell V(D)J Analysis <a id="single-cell-vdj-analysis"></a>

Designed for de novo assembly of full-length TCR / BCR immune receptor sequences, annotation, and clonotype identification.

<div class="doc-callout doc-callout-warn" markdown="block">
<strong>VDJ modes:</strong> Two modes are supported: provide `--beadstrans` to use an RNA cell table for bead mapping and RNA-based cell filtering; or omit it to run VDJ without an RNA cell table. When omitted, `keep_all_cells` is enabled automatically, so assembled barcodes are not filtered by RNA cell calls and must not be treated as an RNA-confirmed cell set.
</div>

The following steps demonstrate **RNA-associated VDJ analysis**. An existing cell table can be reused, so RNA does not need to be rerun solely for this example.

### Step 1: Prepare VDJ Data and Reference {#vdj-prepare-inputs}

Keep TCR and BCR libraries in separate directories, matching the commands below:

```text
/test/data/
├── tcr_fastqs/
│   ├── sample_TCR_R1.fastq.gz
│   └── sample_TCR_R2.fastq.gz
└── bcr_fastqs/
    ├── sample_BCR_R1.fastq.gz
    └── sample_BCR_R2.fastq.gz
```

| Parameter or input | Description |
| :--- | :--- |
| `--fastqs` | Directory of paired FASTQs for the TCR or BCR library; keep the two library types separate. Alternatively, use `--fastq1` and `--fastq2` with matching paired-file order. |
| `--ref` | Use `human` or `mouse` for these species. These are software reference identifiers, not paths. For a custom reference, supply a VDJ reference directory containing `reference.json`, not a FASTA file or RNA / ATAC reference directory. |
| `--chain` | Use `TR` for TCR or `IG` for BCR, matching the input library. |
| `--beadstrans` | For RNA-associated analysis, use the corresponding RNA `outs/singlecell.csv` from the same experiment, not an expression matrix, `barcodes.tsv.gz`, or another sample's cell table. Omit this option for analysis without RNA. |

Replace the `/test/data/...` placeholders with actual paths. See the [input naming rules](#file-naming-conventions) and [VDJ parameters](parameter/scVDJ.md) for custom reference requirements.

### Step 2: Prepare an RNA Cell Table (RNA-Associated Mode Only) {#vdj-prepare-rna}

If the corresponding RNA `singlecell.csv` already exists, reuse it and skip this command. Otherwise, prepare the RNA FASTQs using the [RNA input layout](#rna-prepare-inputs) at `/test/data/rna_5p_fastqs`, then run the corresponding 5′ RNA data. For the mode [without an RNA table](#vdj-without-rna), skip this step entirely.

```bash
$dnbc4tools rna run \
    --fastqs /test/data/rna_5p_fastqs \
    --genomeDir /database/scRNA/Homo_sapiens \
    --name test_rna_5p \
    --threads 30 \
    --end5
```

### Step 3: Run VDJ Analysis {#vdj-run}

For RNA-associated mode, the command above produces `./test_rna_5p/outs/singlecell.csv`. Use this path with `--beadstrans`, or replace it with your existing corresponding cell table. Choose directory input or explicit files; do not combine them.

**Method 1: Directory Input (Recommended)**

*Human TCR Analysis*
```bash
$dnbc4tools vdj run \
    --fastqs /test/data/tcr_fastqs \
    --beadstrans ./test_rna_5p/outs/singlecell.csv \
    --ref human \
    --name test_human_tcr \
    --threads 20 \
    --chain TR
```

*Human BCR Analysis*
```bash
$dnbc4tools vdj run \
    --fastqs /test/data/bcr_fastqs \
    --beadstrans ./test_rna_5p/outs/singlecell.csv \
    --ref human \
    --name test_human_bcr \
    --threads 20 \
    --chain IG
```

**Method 2: Explicit Individual FASTQ Inputs**

When files are located in separate storage paths, provide them via `--fastq1` and `--fastq2`:

*Human TCR Analysis (Explicit Files)*
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

*Human BCR Analysis (Explicit Files)*
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
<summary>Click to expand: Mouse TCR and BCR Analysis Examples</summary>

These examples assume the corresponding mouse RNA cell table already exists at `./test_mouse_rna_5p/outs/singlecell.csv`. Replace it with your actual path; use mouse FASTQs, reference, and RNA cell table consistently.


**Mouse TCR Analysis**

```bash
$dnbc4tools vdj run \
    --fastqs /test/data/mouse_tcr_fastqs \
    --beadstrans ./test_mouse_rna_5p/outs/singlecell.csv \
    --ref mouse \
    --name test_mouse_tcr \
    --threads 20 \
    --chain TR
```

**Mouse BCR Analysis**

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

#### VDJ Without an RNA Cell Table {#vdj-without-rna}

Omit `--beadstrans`; a preceding RNA run is not required for this mode. Other input and reference requirements remain the same.

```bash
$dnbc4tools vdj run \
    --fastqs /test/data/tcr_fastqs \
    --ref human \
    --name test_vdj_without_rna \
    --threads 20 \
    --chain TR
```

The software automatically enables `keep_all_cells`. Review the VDJ annotation flags before counting cells or comparing them with RNA results.

### Step 4: Inspect VDJ Outputs {#vdj-check-outputs}

Upon completion, results are stored in `./<name>/outs/` (e.g., `./test_human_tcr/outs/`):

* **Interactive Report**: Open `*_report.html` in a web browser to review assembly rates, productive contig proportions, and clonotype diversity distributions;
* **Assembly & Annotations**: Primary filtered annotations in `filtered_contig_annotations.csv` and assembly sequences in `filtered_contig.fasta`;
* **Immune Repertoire Standards**: Standard `clonotypes.csv` and `airr_annotations.tsv` (directly compatible with `scRepertoire` or `immunarch`).

For complete output files and annotation definitions, see [scVDJ Output Details](outs/scVDJ.md) and [Reading Results in R / Python](io.md#scvdj-analysis).

---

## Integrated Multi-Omics Analysis <a id="integrated-multi-omics-analysis"></a>

Use one configuration file to run RNA, ATAC, TCR, and BCR libraries and generate a combined report. The example below uses **5′ RNA + ATAC + TCR + BCR from one biological sample**. Keep only the modalities available in your experiment; all four libraries are not required. Configure and run independent samples separately. For pooled C6 RNA libraries labeled with Sample Barcodes, use the [C6 multiplexed workflow](#c6-multi-sample-analysis) below.

!!! note "Scope of integration"
    RNA and V(D)J can share cell information. ATAC is currently analyzed independently and summarized in the combined report. This command does not perform joint RNA + ATAC dimensionality reduction or clustering.

### Step 1: Prepare Sequencing Data and References {#multi-prepare-inputs}

Place each library from the sample in its own directory, for example:

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

- **RNA**: Set `fastqs` to `/test/data/rna`, the root containing both `cDNA/` and `oligo/`. Do not point it to `cDNA/` alone or to an individual FASTQ file.
- **ATAC, TCR, and BCR**: Provide the directory containing the paired FASTQs for each library. Keep TCR and BCR separate. See the [automatic filename pairing rules](#file-naming-conventions).
- **Only one FASTQ root is supported per modality**, and each modality may appear only once in `[libraries]`. If a library has multiple sequencing files, place matched R1/R2 files in the corresponding directory, with compatible read structures and dark-cycle settings. Do not include other samples or unrelated libraries.
- **RNA / ATAC references**: Use reference directories already built with `rna mkref` and `atac mkref`, respectively. Do not supply a FASTA, GTF, or a directory containing only the original reference files. See the [RNA](#single-cell-rna-analysis) and [ATAC](#single-cell-atac-analysis) sections above for reference building.
- **VDJ reference**: Use `human` or `mouse` for these species, or provide a custom VDJ reference directory containing `reference.json`. See the [VDJ parameters](parameter/scVDJ.md).

The `/test/data/...` paths above and `/database/...` paths below are placeholders. Replace them with existing data and reference directories on your system before running.

### Step 2: Write the Multi-Omics Configuration {#multi-prepare-config}

Save the following as a plain-text file named `multi.config.csv`. The configuration uses `[sections]` with comma-separated content: retain the header in `[libraries]`, and use `parameter,value` rows in each modality section.

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

| Setting | Meaning and value |
| :--- | :--- |
| `[libraries] fastqs` | FASTQ root for the library, following the layout above. |
| `[libraries] feature_types` | `rna`, `atac`, `vdj-t` (TCR), or `vdj-b` (BCR); must match the corresponding modality section. |
| `[rna] genomeDir` / `[atac] genomeDir` | Previously built reference directory for each modality; provide the RNA and ATAC references separately. |
| `[rna] end5,true` | Specifies 5′ RNA data in this example. For 3′ RNA, remove this line instead of copying the setting. |
| `[vdj-t] ref` / `[vdj-b] ref` | VDJ species identifier or custom reference directory; `human` in this example is a species identifier, not a file path. |

**Remove modalities you do not have**: For RNA + TCR only, delete the `atac` and `vdj-b` rows from `[libraries]` and remove the entire `[atac]` and `[vdj-b]` sections. Declare only available libraries; do not leave empty paths. When 5′ RNA is enabled and its cell table is generated successfully, VDJ uses that table by default. You do not need to run RNA separately first or set `beadstrans` manually.

**Path resolution**: Relative paths inside the configuration are resolved against the directory containing `multi.config.csv`. Absolute paths are recommended for your first run. For example, if the CSV is `/project/config/multi.config.csv`, `../fastqs/rna` resolves to `/project/fastqs/rna`. Relative `--csv` and `--outdir` command-line paths are resolved against the current working directory when you run the command.

For other modality parameters, Boolean values, and values containing commas, see the [Multi parameters](parameter/multi.md).

### Step 3: Run the Multi-Omics Analysis {#multi-run}

Run this command from the directory containing `multi.config.csv`:

```bash
$dnbc4tools multi run \
    --name test_multi \
    --csv ./multi.config.csv \
    --threads 20
```

Here, `--name test_multi` sets the run name; by default, outputs are generated under `./test_multi/outs/` (use `--outdir` to specify another root directory); and `--threads 20` sets the CPU thread count.

### Step 4: Inspect Multi-Omics Outputs {#multi-check-outputs}

Upon completion, results are consolidated in `./test_multi/outs/`:

* **Combined Interactive Report**: Open `test_multi_multi_report.html` in a web browser to inspect cross-modality summary QC across RNA, ATAC, TCR, and BCR;
* **Decoupled Modality Subdirectories**: Output directories (`rna/`, `atac/`, `vdj-t/`, `vdj-b/`) follow standard single-modality specifications and can be analyzed independently;
* **Execution Audit Manifest**: `logs/run_manifest.json` tracks per-modality execution status and runtimes.

For full multi-omics directory hierarchy and file specifications, see [Multi-Omics Output Details](outs/multi.md).

---

## C6 Multiplexed Single-Cell RNA Analysis <a id="c6-multi-sample-analysis"></a>

Use this workflow for C6 RNA samples labeled with Sample Barcodes and pooled during library preparation. Multiple biological samples share one set of cDNA and Oligo sequencing data. The software uses the configured barcode assignments to demultiplex samples, then performs cell calling, counting, and downstream analysis separately for each sample. For samples with independent libraries and FASTQs, use [single-sample RNA analysis](#single-cell-rna-analysis) or [batch script generation](#batch-script-generation).

### Step 1: Prepare Shared Data, Reference, and Sample Assignments {#c6-prepare-inputs}

Place paired cDNA and Oligo reads from **one pooled C6 library** in the following directories:

```text
/test/data/c6_pooled_data/
├── cDNA/
│   ├── pooled_cDNA_R1.fastq.gz
│   └── pooled_cDNA_R2.fastq.gz
└── oligo/
    ├── pooled_oligo_R1.fastq.gz
    └── pooled_oligo_R2.fastq.gz
```

- **Shared FASTQ root**: Set `[libraries] fastqs` to `/test/data/c6_pooled_data`, not to `cDNA/`, `oligo/`, or an individual FASTQ file. All samples share this single input row; do not create FASTQ directories per sample or repeat the `rna` row.
- **Multiple sequencing files**: For multiple files from the same pooled library, place matched pairs in the corresponding `cDNA/` and `oligo/` directories. Read structures and dark-cycle settings must be compatible. See the [automatic filename pairing rules](#file-naming-conventions). Configure and run different pooled libraries separately.
- **Reference**: Prepare a reference directory already built with `rna mkref`. Set `genomeDir` to that directory, not to a FASTA or GTF file. See [RNA reference building](#single-cell-rna-analysis) above.
- **Sample assignments**: Check your experimental records for the Sample Barcode assigned to each biological sample. The mappings `Sample_01 → BC01` and `Sample_02 → BC02;BC03` below are examples only. Replace them with the actual assignments; do not infer barcodes from sample order.

Both `/test/data/c6_pooled_data` and `/database/scRNA/Homo_sapiens` are placeholders. Replace them with existing data and reference directories on your system.

### Step 2: Write the C6 Configuration {#c6-prepare-config}

Save the following as a plain-text file named `sample.config.csv`, retaining all three sections and both table headers:

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

| Setting | Meaning and value |
| :--- | :--- |
| `[rna] genomeDir` | RNA reference directory. |
| `[rna] chemistry,scRNAC6` | C6 read structure; fixed to `scRNAC6` when `[samples]` is present. An omitted value is also normalized to this name. |
| `[rna] darkreaction,auto` | Automatically detect cDNA and Oligo dark cycles; this does not select the chemistry version. |
| `[rna] no_bam,false` | Retain the default BAM output. Change to `true` to save storage by omitting per-sample, unassigned, and Oligo BAMs and their indexes. |
| `[libraries] fastqs` / `feature_types` | Shared FASTQ root and library type; use one row with type `rna` in this example. |
| `[samples] sample_id` | Biological sample name used for output directories and reports; it does not need to match a FASTQ filename. |
| `[samples] probe_barcode_ids` | Sample Barcode IDs actually used for that sample; separate multiple IDs for the same sample with semicolons `;`. |

**Sample table rules**: Use one row per biological sample. In this example, data labeled `BC02` and `BC03` are assigned together to `Sample_02`, rather than creating two separate samples. Sample names must be unique ignoring case, begin with a letter or digit, and contain only letters, digits, `.`, `_`, or `-`. Do not use the reserved names `unassigned` or `non_multiplexed`. Do not repeat a barcode within a row or assign it to multiple samples. Built-in IDs and custom DNA sequences are supported; see the [C6 sample table specification](parameter/c6.md#samples-specification).

**Path resolution**: Relative paths inside the configuration are resolved against the directory containing `sample.config.csv`. Relative `--csv` and `--outdir` command-line paths are resolved against the current working directory. Absolute paths in the configuration are recommended for your first run.

**Optional cell-calling settings**: Add `expectcells`, `forcecells`, or `minumi` columns to `[samples]` when per-sample settings are needed, using positive integers. Empty fields inherit global settings. Do not copy the pooled experiment's expected cell count into every sample row. `high_occupancy_filter` is an experiment-wide switch, enabled by default, and belongs only in `[rna]`. See the [C6 parameter examples](parameter/c6.md#sample-overrides).

### Step 3: Run the C6 Analysis {#c6-run}

Run this command from the directory containing `sample.config.csv`:

```bash
$dnbc4tools multi run \
    --name test_c6 \
    --csv ./sample.config.csv \
    --threads 40
```

`--name test_c6` names the entire pooled-library run, separately from `Sample_01` and `Sample_02` in `[samples]`. This command writes results to `./test_c6/outs/` under the current working directory (use `--outdir` to specify another root directory) and uses 40 CPU threads.

### Step 4: Inspect Global and Per-Sample Outputs {#c6-check-outputs}

Upon completion, results are stored in `./test_c6/outs/`:

* **Batch Summary Report**: Open `test_c6_multi_report.html` in a web browser to inspect overall library QC, Sample Barcode demultiplexing yield, and per-sample cell count comparisons;
* **Per-Sample Dedicated Deliverables**: Each sample has dedicated results in `rna/per_sample_outs/<sample>/`, including individual interactive reports (`<sample>_scRNA_report.html`), count matrices (MEX / `.h5` / `.h5ad`), and alignment BAMs (if enabled);
* **Physical Library Pooled Matrix**: `rna/filtered_feature_bc_matrix/` (and `.h5` / `.h5ad`) retains the global unintegrated counts across the pooled library.

For detailed C6 directory specifications and batch integration considerations, see [C6 Output Details](outs/c6.md) and [Reading Results in R / Python](io.md#c6-analysis).

---

## Batch Script Generation <a id="batch-script-generation"></a>

Designed for scaling up analysis across dozens of independent single-cell samples. By providing a tab-separated sample list, dnbc4tools automatically generates standalone shell scripts for each sample, ready to run directly or queue through workload managers such as Slurm or SGE.

### Step 1: Prepare Sample Manifest

**RNA Sample Manifest (`rna_samples.tsv`)**

Tab-delimited with 3 columns: `sample_id`, `cDNA_R1;cDNA_R2`, `oligo_R1;oligo_R2` (comma-separated for multi-lane files per read):

```text
Sample1	sample1_cDNA_R1.fq.gz;sample1_cDNA_R2.fq.gz	sample1_oligo_R1.fq.gz;sample1_oligo_R2.fq.gz
Sample2	sample2_cDNA_R1.fq.gz;sample2_cDNA_R2.fq.gz	sample2_oligo_R1.fq.gz;sample2_oligo_R2.fq.gz
```

**ATAC Sample Manifest (`atac_samples.tsv`)**

Tab-delimited with 2 columns: `sample_id`, `FASTQ_R1;FASTQ_R2` (comma-separated for multi-lane files per read):

```text
Sample1	sample1_R1.fq.gz;sample1_R2.fq.gz
Sample2	sample2_R1.fq.gz;sample2_R2.fq.gz
```

### Step 2: Generate Analysis Scripts

```bash
# Batch generate RNA execution scripts
$dnbc4tools rna multi \
    --list ./rna_samples.tsv \
    --genomeDir /database/scRNA/Homo_sapiens \
    --threads 20

# Batch generate ATAC execution scripts
$dnbc4tools atac multi \
    --list ./atac_samples.tsv \
    --genomeDir /database/scATAC/Homo_sapiens \
    --threads 20
```

> **Execution Behavior:**
> The `multi` command generates standalone `.sh` scripts (e.g., `run_Sample1.sh`) in the current working directory without automatically starting computational workloads. Execute generated scripts on demand (e.g., `sh run_Sample1.sh`) or submit them to your HPC cluster queue.

---

After completing the quick start walkthroughs, consult detailed documentation for advanced options:

* Explore underlying pipeline workflows: [Pipeline Overview](./pipeline/pipeline.md)
* Learn comprehensive parameters and CLI options: [Parameters Overview](./parameter/parameter.md)
* Understand structured deliverable files: [Output Deliverables Overview](./outs/outs.md)
