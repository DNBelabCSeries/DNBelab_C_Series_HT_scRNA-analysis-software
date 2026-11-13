# Release Notes

**Release history of DNBelab C Series™ HT Single-Cell Analysis Software**

[Development Version](#latest-release) • [Previous Releases](#release-history) • [Version Guide](#version-selection-guide)

## Development Version <a id="latest-release"></a>

**dnbc4tools 3.2 — Development Documentation (unreleased)**, updated October 23, 2026.

The formal release date, installation package and checksums await confirmation. The latest release documented before this update was 3.1 (May 15, 2026).

### 3.2 Key Updates <a id="32-source"></a>

- **C6 Multiplexed scRNA Analysis**: Enables pooled sequencing within a single physical library with automatic Sample Barcode demultiplexing, delivering independent expression matrices (MEX / H5 / H5AD), aligned BAMs (when `[rna] no_bam` is `false`, the default), and interactive HTML reports for each sample.
- **Dual-Species Classification Upgrade**: Introduces bidirectional background prediction bands and two-stage robust Huber regression to replace rigid cutoffs, to assess cell species assignments.
- **scRNA Algorithmic & Filtering Optimizations**: Updates Oligo Read 2 filtering rules; optimizes multi-gene duplicate UMI conflict resolution; adds bound safeguards for automatic cell calling.
- **scATAC Core Upgrades**: Switches peak calling and matrix quantification to cutsite mode (9-bp offset adjusted Tn5 insertion sites); preserves fragment-based FRIP and TSS metrics.
- **scVDJ Algorithmic Upgrades**: Updates chain pairing, full-length contig assembly, and deterministic handling of multi-threaded sampling.
- **Standardized Outputs & Infrastructure**: Standardizes RNA/ATAC matrix directory structures with companion `.h5` files; decouples batch script generation to the working directory; adds startup preflight, process file locks, structured error tracking, and compressed diagnostic archives.

For detailed algorithmic rationale, parameter behavior, and migration guidelines, see the [Upgrade Guide](migration.md). Use the header menu to view the frozen 3.1 manual.

## Previous Release History <a id="release-history"></a> <a id="legacy-version-notes"></a>

The previous release records are listed below in reverse chronological order:

<details markdown="block">
<summary><strong>3.1 (2026-05-15)</strong> <a id="31-may-15-2026"></a></summary>

- **Multi-omics Mode**: Added support for single-sample multi-omics analysis, enabling combined RNA + VDJ workflows or standalone single-modality execution.
- **RNA Enhancements & Bug Fixes**: Added `--consistent_cells` to reuse merged bead assignments for downstream consistency; resolved calculation error in Fraction Reads in Cells; fixed dual-species database handling for species names containing underscores.
- **Performance & CLI Consistency**: Accelerated `bam2fastq` and `fqsubC4` processing; standardized help text and parameter formatting across all modules (including multi-sample commands).

</details>

<details markdown="block">
<summary><strong>3.0 (Dec 18, 2025)</strong></summary>

- **RNA-Seq Enhancements**:
    - Refined prioritization of exonic loci to improve quantification accuracy and resolve multi-gene mapping ambiguities;
    - Implemented error correction logic for cell barcodes containing ambiguous 'N' bases;
    - Added robust support for building and analyzing mixed-species reference genomes;
    - Enriched BAM files with cell tags (CC/CB), updated feature matrices to include gene ID, gene name, and library type;
    - Introduced automatic estimation for `expectcells` and added a new `minumi` threshold parameter.
- **ATAC-Seq Enhancements**:
    - Expanded QC metrics to include barcode/read Q30 statistics and insert size distributions derived from deduplicated fragments;
    - Upgraded alignment engine to chromap v0.3.3, enhanced barcode correction algorithms, and enriched BAM outputs.
- **VDJ Enhancements**:
    - Advanced per-cell assembly algorithms to maximize full-length contig recovery with stricter filtering criteria;
    - Optimized memory management to eliminate the need for full data preloading during analysis;
    - Enhanced `contig_annotations.csv` with comprehensive details, improved QC metrics, and added consensus sequence annotations;
    - Enabled support for custom reference generation for non-human/mouse species.
- **Cross-Module Improvements**:
    - Unified the `customize` parameter usage across all analysis modules;
    - Achieved significant reduction in disk usage through optimized file organization;
    - Deprecated the `process` parameter and automated the cleanup of intermediate files to streamline execution.

</details>

<details markdown="block">
<summary><strong>2.1.3 (October 9, 2024)</strong></summary>

- **New Features**:
    - Added RNA 5' transcriptome analysis module;
    - Added single-cell VDJ analysis module;
    - Added GTF file format checking and correction functionality.
- **Installation & Performance**:
    - Released as `tar.gz` with no additional environment configuration needed;
    - Removed conda installation method;
    - Fixed memory exceptions in scATAC bead merging;
    - Optimized RNA alignment and interval annotation performance.

</details>

<details markdown="block">
<summary><strong>2.1.2 (April 24, 2024)</strong></summary>

- **ATAC Analysis Improvements**:
    - Updated algorithm: Jaccard-based merging → cell calling via peak fragments;
    - Added multiple filtering parameters and BAM format support;
    - Enhanced chloroplast handling in database construction;
    - Unified web report style with RNA analysis.
- **General Improvements**:
    - Streamlined installation process (removed R package requirements);
    - Improved N filtering logic for cell barcodes and UMI regions.

</details>

<details markdown="block">
<summary><strong>2.1.1 (September 21, 2023)</strong></summary>

- **RNA Workflow Optimization**:
    - Bead merging analysis using oligo data before cell calling;
    - Enhanced marker gene display (top 50 genes by log2 fold change per population).
- **Bug Fixes**:
    - Fixed high memory usage in container versions;
    - Resolved ATAC report image display issues.

</details>

<details markdown="block">
<summary><strong>2.1.0 (July 28, 2023)</strong></summary>

- **Major Addition**:
    - New ATAC analysis module.
- **RNA Module Updates**:
    - Optimized reference database construction with `ref.json` information file;
    - Replaced Seurat with Scanpy for faster dimensionality reduction and clustering.

</details>

<details markdown="block">
<summary><strong>2.0.7 (November 4, 2022)</strong></summary>

- **Automation & Parameters**:
    - Automatic recognition of reagent versions and sequencing dark cycles;
    - New parameters: `chemistry`, `darkreaction`, `customize` (replacing `cDNAconfig`/`oligoconfig`);
    - Removed `mixseq` parameter.
- **Technical Improvements**:
    - Added adapter sequence trimming for RNA cDNA libraries;
    - Memory parameter `limitram` for database construction with automatic optimization.

</details>

<details markdown="block">
<summary><strong>2.0.6 (September 19, 2022)</strong></summary>

- **Container & Reliability**:
    - Added Singularity container support;
    - Fixed reproducibility issues for consistent results;
    - Corrected cDNA library Q30 statistics and barcode count consistency.

</details>

<details markdown="block">
<summary><strong>2.0.5 (August 19, 2022)</strong></summary>

- **Container & Format Support**:
    - Added Docker image version;
    - Reduced GTF format requirements (flexible `gene_name`/`transcript_name` handling);
    - Improved UMI correction logic and HTML report descriptions.

</details>

<details markdown="block">
<summary><strong>2.0.0 (June 20, 2022)</strong></summary>

- **Major Release**:
    - Command-line interface support;
    - Enhanced workflow stability and error handling;
    - Optimized alignment and annotation performance;
    - Default emptydrops cell identification method;
    - Added saturation analysis and cell cluster annotation.

</details>

## Version Selection Guide <a id="version-selection-guide"></a>

<table>
  <thead>
    <tr>
      <th>Version</th>
      <th>Key Features</th>
      <th>Recommended Use Cases</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>3.2 (development)</b></td>
      <td>C6 multiplexed scRNA</td>
      <td>C6 multiplexed scRNA analysis</td>
    </tr>
    <tr>
      <td><b>3.1+</b></td>
      <td>Multi-omics (RNA + VDJ)</td>
      <td>RNA + VDJ combined analysis</td>
    </tr>
    <tr>
      <td><b>2.1.3+</b></td>
      <td>RNA 5', VDJ</td>
      <td>VDJ, 5' RNA</td>
    </tr>
    <tr>
      <td><b>2.1.0+</b></td>
      <td>ATAC analysis support</td>
      <td>ATAC-seq analysis</td>
    </tr>
    <tr>
      <td><b>2.0.0+</b></td>
      <td>Command-line interface</td>
      <td>Standard 3' RNA analysis</td>
    </tr>
  </tbody>
</table>

### Historical Versions

Detailed download links and installation instructions for older versions are available in the [Previous Installation Guide](installation_previous.md). Additional information can be found at [GitHub Releases](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/releases).

!!! note "Release Guidance"
    - **Stable**: Recommended for production environments; receives security and critical bug fixes.
    - **Release Candidate (RC)**: Feature-complete builds intended for final validation and staging/pre-production. Minor bug fixes may still be applied.
    - **Beta**: For testing and development only; APIs and behavior may change.

---

*For detailed installation and usage instructions, see the [Installation Guide](installation.md) and [Quick Start](quickstart.md).*
