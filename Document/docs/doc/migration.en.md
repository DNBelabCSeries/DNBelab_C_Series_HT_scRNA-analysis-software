# Upgrading from 3.1 to 3.2

This document summarizes the major new features, algorithmic optimizations, and output file changes in DNBelab C Series™ HT Single-Cell Analysis Software (dnbc4tools) between versions 3.1 and 3.2. Use the version switcher in the header to view the archived 3.1 documentation.

---

## Major New Feature: C6 Multiplexed scRNA Analysis

Version 3.2 introduces native support for **C6 Multiplexed scRNA Analysis**, enabling pooled multiplexed sequencing and Sample Barcode demultiplexing within a single library:

- **Configuration and Execution**: Declare sample names and associated Sample Barcodes in the `[samples]` section of the `multi run` configuration. The software automatically detects and runs the C6 multiplexed pipeline without requiring manual chemistry flags.
- **Pooled and Per-Sample Expression Matrices**:
    - Complete gene expression matrices are generated for both the pooled library (in the root output directory) and for each demultiplexed sample (under `per_sample_outs/<sample>/`), provided concurrently in MEX directory, standard H5, and H5AD formats;
    - Each sample delivers a sample-specific interactive HTML QC and analysis report (`per_sample_outs/<sample>/<sample>_scRNA_report.html`).
- **Sample-Specific BAM Outputs**:
    - By default, generates aligned BAM files for each individual sample (`per_sample_outs/<sample>/<sample>_alignments.bam` with index), facilitating sample-specific IGV visualization and variant detection;
    - When `[rna] no_bam` is `false` (the default), reads not uniquely assignable to any sample barcode are collected in `unassigned_alignments.bam`. Setting `no_bam,true` omits all BAM files and their indexes, including per-sample, unassigned, and oligo BAM outputs.
- **Independent Dual-UMI Correction**: Independently corrects and deduplicates both UMI segments for C6 dual-UMI architectures, for subsequent molecule counting.

---

## Algorithmic Updates & Metric Interpretation

### 1. Single-Cell RNA (scRNA)
- **Optimized Intra-Cell Multi-Gene Duplicate UMI Resolution**:
    - Version 3.1 already supported this filtering mechanism, but had boundary condition defects. Version 3.2 resolves these defects and optimizes conflict resolution: when a UMI within a cell maps to multiple genes, it is assigned to the dominant gene with strictly higher read counts; if read counts tie, the ambiguous molecule is removed and excluded from gene expression counts.
- **Bound Safeguards for Automatic Cell Calling**:
    - Version 3.1 lacked explicit upper and lower bounds for automatic cell number prediction. Version 3.2 introduces automatic prediction bound constraints, to constrain the estimated cell count; assess the resulting cell calls alongside sample QC metrics.
- **Oligo Read 2 Filtering Optimization to Minimize Data Discard**:
    - Updates quality control, barcode correction, and filtering rules for barcode and structural sequences in Oligo Read 2.

### 2. Dual-Species Mixed Classification Algorithm Upgrade
- **Bidirectional Background Prediction Bands**:
    - Updates the mixed-species classification model (e.g. human-mouse), replacing legacy rigid cutoffs (such as fixed 1,000 UMI / 90% purity rules and empirical quantiles) with empirical bidirectional continuous prediction band models;
    - Employs two-stage robust Huber regression to independently model cross-species background leakage and observation variance between host and secondary species, to assess cell species assignments;
    - Incorporates bead-aware modeling for ATAC species assignment, jointly modeling merged bead counts (N1, N2...) alongside chromatin accessibility depth to distinguish cross-species multiplets from deeply sequenced single cells.

### 3. Single-Cell ATAC (scATAC)
- **Cutsite-Based Quantification for Peaks and Matrices**:
    - **What is a cutsite?** In ATAC-seq, Tn5 transposase binds open chromatin and cleaves the DNA double helix while inserting sequencing adapters, introducing a characteristic 9-bp staggered cut. **Cutsite mode counts the actual Tn5 insertion cleavage endpoints after 9-bp offset adjustment**. Cutsite mode counts cleavage endpoints, whereas fragment mode counts sequencing fragments; the counting units differ.
    - **Metric Semantics**: Peak calling and matrix counts default to cutsite quantification; key QC metrics—including FRIP (Fraction of Reads in Peaks), TSS enrichment fraction, and Cell Calling—remain strictly evaluated on deduplicated unique fragments.

### 4. Single-Cell V(D)J (scVDJ)
- Updates chain pairing and full-length contig assembly logic.
- Updates deterministic handling of multi-threaded sampling. Keep inputs, parameters, and the software environment consistent when comparing runs.

---

## Changes Requiring Adaptation from 3.1

<a id="output-directory-file-format-changes"></a>

The table below covers changes to existing 3.1 workflows. C6 is new in 3.2 and has no equivalent 3.1 output layout. Its per-sample results are under `outs/rna/per_sample_outs/<sample>/`, and pooled matrices are under `outs/rna/`. The new C6 detail table is `outs/rna/singlecell.csv.gz`; read it with gzip support and use `is_cell_barcode` to select called cells.

### Output Directory & File Format Changes

| Change Item | Version 3.1 | Version 3.2 | Migration Action |
| :--- | :--- | :--- | :--- |
| **RNA Matrix Directories** | `raw_matrix/`<br>`filter_matrix/` | `raw_feature_bc_matrix/`<br>`filtered_feature_bc_matrix/` | Aligned with standard 10X directory naming; companion `.h5` files added for single-file loading. |
| **ATAC Matrix Directories** | `raw_peak_matrix/`<br>`filter_peak_matrix/` | `raw_peak_bc_matrix/`<br>`filtered_peak_bc_matrix/` | Standardized directory naming; companion `.h5` files added. |
| **ATAC Text Matrix** | `matrix.mtx.gz` tab-separated | `matrix.mtx.gz` **single-space** separated | Update custom scripts to split on whitespace (`line.split()`) or use standard MatrixMarket readers. |
| **Batch Analysis Scripts** | Written to output directory | Generated **only in the current working directory** | Run scripts from the current directory; `--outdir` sets analysis output; existing scripts are not overwritten. |
