# Outputs and Reports

> **Output scope**: Directory trees describe a typical completed run. Optional outputs depend on enabled modules and successful stages. Quality ranges below are interpretation guidance, not software pass/fail rules; use the configured thresholds and report status for this run.

Find output directories, file fields, and web report metrics by module. Independent pipeline runs write to `<outdir>/<name>/outs/`; Multi-omics (Multi) and C6 multiplexed workflows organize results hierarchically by modality and sample.

| Module | Main Deliverables | Documentation |
| :--- | :--- | :--- |
| **scRNA** | Gene expression matrices (MEX / H5 / H5AD), cell metadata table, clustering, and HTML QC report | [scRNA Outputs Guide](scRNA.md) |
| **scATAC** | Chromatin accessibility peak matrices, Tabix-indexed fragments, cell QC, and HTML QC report | [scATAC Outputs Guide](scATAC.md) |
| **scVDJ** | TCR / BCR contig sequences, full-length functional annotations, clonotypes, and HTML QC report | [scVDJ Outputs Guide](scVDJ.md) |
| **Multi-omics (Multi)** | Cross-modality combined QC report, modularized outputs for each modality (RNA / ATAC / VDJ) | [Multi Outputs Guide](multi.md) |
| **C6 Multiplexed** | Root combined expression matrix, `singlecell.csv.gz`, per-sample dedicated matrices, BAMs (when `[rna] no_bam` is `false`), and reports | [C6 Outputs Guide](c6.md) |

---

## Universal Delivery Standards & Architecture

dnbc4tools follows unified data delivery standards and directory organization across all omics workflows:

### 1. Standard Output Directory Hierarchy
- **Independent Single-Modality Workflows**: Output directly to `<outdir>/<name>/outs/`, housing delivered matrices, metric summary tables, BAM alignments (if enabled), and HTML interactive reports.
- **Multi-Omics Workflows (Multi)**: Deliver a combined cross-modality report `<name>_multi_report.html` in the root `outs/` directory, while decoupling each modality into dedicated subdirectories (`rna/`, `atac/`, `vdj-t/`, `vdj-b/`) fully compatible with single-modality standards.
- **C6 Multiplexed Workflows**: The combined report is `outs/<name>_multi_report.html`; pooled matrices and `singlecell.csv.gz` are under `outs/rna/`, and per-sample outputs are under `outs/rna/per_sample_outs/<sample>/`.

### 2. Feature & Expression Matrix Formats

All single-cell quantification matrices are delivered simultaneously in mainstream standard formats:

- **MEX Matrices**: RNA uses `matrix.mtx.gz`, `barcodes.tsv.gz`, and `features.tsv.gz`. ATAC uses `peaks.bed.gz` instead of `features.tsv.gz`; read its matrix, barcodes, and peak coordinates explicitly rather than assuming an RNA feature file is present. See the [loading guide](../io.md).
- **H5 Format** (`*.h5`): Single-file binary sparse matrix with metadata, loaded rapidly in R via `Seurat::Read10X_h5()` and in Python via `scanpy.read_10x_h5()`.
- **H5AD Format** (`*.h5ad`): RNA/C6 count matrices and RNA analysis objects are separate files. Count exports do not include clustering; use `analysis/QC_Cluster.h5ad` for saved downstream analysis. ATAC does not publish a count H5AD under `outs/`.

### 3. Unified Cell Calling & Metadata Filtering Rule
- `singlecell.csv` (or `singlecell.csv.gz`) records metrics across all candidate droplets/beads, including ambient noise and zero-UMI rows.
- **Universal Rule**: In downstream analysis, **always filter authentic cells using `is_cell_barcode`** (selecting rows where value is `1` or `True`). Never use the total row count of the table as the delivered cell count.

### 4. Metric Summary File Format
- `metrics_summary.xls` uses the `.xls` extension for convenient double-click inspection in spreadsheet software, but its underlying format is **standard tab-separated text (TSV)**.
- **Programmatic Reading**: In R, use `read.delim("metrics_summary.xls", check.names = FALSE)` (do not use `readxl::read_excel`); in Python, use `pd.read_csv("metrics_summary.xls", sep="\t")`.

### 5. Alignment BAM & Adaptive Indexing Rules
- **Delivery Flags**: scRNA generates BAM by default (skip with `--no_bam`); scATAC skips BAM by default to save I/O and disk (enable with `--need_bam`).
- **BAM Indexes**: The native writer selects CSI when the maximum reference length exceeds `2^29` bases (536,870,912); otherwise it selects BAI. Header-only zero-result RNA BAMs may lack an index. Oligo BAMs are not required to have a coordinate index.
- **C6 BAM Output**: `[rna] no_bam` defaults to `false`. Set `no_bam,true` to skip per-sample, unassigned, and oligo BAM files and their indexes.
- **BAM Tags**: RNA/C6 cDNA records may carry UMI tags such as `UB`; ATAC does not use RNA UMI tags. Use `CB` to select records with a merged-cell identifier; tags on unmatched, unmapped, or oligo records differ.

---

## Modality Highlights & Caveats Quick Reference

Different modalities involve specific biological mechanisms and data structures. The table below summarizes key downstream considerations with links to dedicated sections:

| Modality / Workflow | Key Caveats & Best Practices | See Section |
| :--- | :--- | :--- |
| **scRNA** | • Matrices feature UMI deduplication and conflict resolution for multi-gene mapping UMIs.<br>• Multiple beads per droplet are merged into Cell IDs formatted as `CELL<ID>_N<count>`. | [scRNA Feature Matrices](scRNA.md#feature-matrix-files) |
| **scATAC** | • **Crucial**: Peak matrices count 9-bp shifted **cutsites**, whereas cell QC metrics (FRIP/TSS) are based on **unique fragments**; never use matrix column sums as fragment sequencing depth.<br>• 3.2 `matrix.mtx.gz` uses single space delimiters. | [scATAC Fragments & Peaks](scATAC.md#atac-fragment-and-peak-files) |
| **scVDJ** | • Primary downstream entry point is `filtered_contig_annotations.csv` (excluding non-productive and ambient noise).<br>• AIRR standard file (`airr_annotations.tsv`) loads directly into `scRepertoire`/`immunarch`.<br>• `--beadstrans` maps cell identifiers for RNA association; contig tables remain one-to-many per cell. | [scVDJ Assembly & Annotation](scVDJ.md#vdj-assembly-and-annotation-files) |
| **C6 Multiplexed** | • The pooled matrix under `outs/rna/` retains raw counts and does not include joint clustering/UMAP.<br>• Demultiplexed outputs live in `outs/rna/per_sample_outs/<sample>/`.<br>• Preserve barcode suffixes to prevent cross-sample collisions. | [C6 Deliverables Guide](c6.md#detailed-deliverables) |
| **Multi-Omics (Multi)** | • Modularized directories (`rna/`, `atac/`, `vdj-t/`, `vdj-b/`) enable standalone analysis and cross-modality studies.<br>• `logs/run_manifest.json` tracks execution and resume cache status. | [Multi-Omics Detailed Outputs](multi.md#detailed-file-description) |

---

## Common Operational Guides

- For practical code recipes in R and Python, see [Import in R / Python](../io.md).
- For output format changes from 3.1 to 3.2, see [File Changes After Upgrading](../migration.md).
- For troubleshooting missing files or errors, see [Troubleshooting](../troubleshooting.md).
