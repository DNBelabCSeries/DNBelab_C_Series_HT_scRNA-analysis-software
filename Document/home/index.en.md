<div class="doc-hero-badge">
  <span class="doc-badge-pill">v3.2 Development Documentation</span>
  <span class="doc-badge-sub">DNBC4TOOLS Single-Cell Suite</span>
</div>

# DNBelab C Series™ HT Single-Cell Analysis Software

A single-cell analysis toolkit for DNBelab C Series™ sequencing data. CLI tool: **`dnbc4tools`**. Supports single-cell RNA, ATAC, V(D)J, and C6 multi-sample pipelines with quality control, quantification, annotation, and interactive HTML reporting.

<div class="doc-actions">
<a href="doc/quickstart.md" class="doc-btn-primary">Quick Start →</a>
<a href="doc/installation.md" class="doc-btn-outline">Installation Guide</a>
<a href="doc/migration.md" class="doc-btn-outline">Upgrade Guide (3.1 → 3.2)</a>
</div>

## Analysis Modalities

<div class="doc-module-grid">
<div class="doc-module mod-rna">
<div class="doc-module-header">
  <span class="doc-module-tag">scRNA</span>
  <h3>RNA Gene Expression</h3>
</div>
<p>Gene quantification, cell calling (EmptyDrops), UMI correction, and cell clustering.</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/scRNA.md">Workflow</a>
<a class="doc-pill-link" href="doc/parameter/scRNA.md">Parameters</a>
<a class="doc-pill-link" href="doc/outs/scRNA.md">Outputs</a>
</div>
</div>
<div class="doc-module mod-multi">
<div class="doc-module-header">
  <span class="doc-module-tag">Multi</span>
  <h3>Multi-Omics Analysis</h3>
</div>
<p>Unified pipeline coordination for single-cell RNA, ATAC, and V(D)J libraries with cross-modality interactive reports.</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/multi.md">Workflow</a>
<a class="doc-pill-link" href="doc/parameter/multi.md">Parameters</a>
<a class="doc-pill-link" href="doc/outs/multi.md">Outputs</a>
</div>
</div>
<div class="doc-module mod-vdj">
<div class="doc-module-header">
  <span class="doc-module-tag">scVDJ</span>
  <h3>V(D)J Immune Profiling</h3>
</div>
<p>De novo assembly of full-length TCR / BCR sequences, V(D)J gene annotation, and clonotype identification.</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/scVDJ.md">Workflow</a>
<a class="doc-pill-link" href="doc/parameter/scVDJ.md">Parameters</a>
<a class="doc-pill-link" href="doc/outs/scVDJ.md">Outputs</a>
</div>
</div>
<div class="doc-module mod-c6">
<div class="doc-module-header">
  <span class="doc-module-tag">C6</span>
  <h3>C6 Multiplexed RNA</h3>
</div>
<p>Supports sample barcode demultiplexing and generates separate results for each sample.</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/c6.md">Workflow</a>
<a class="doc-pill-link" href="doc/parameter/c6.md">Parameters</a>
<a class="doc-pill-link" href="doc/outs/c6.md">Outputs</a>
</div>
</div>
<div class="doc-module mod-atac">
<div class="doc-module-header">
  <span class="doc-module-tag">scATAC</span>
  <h3>ATAC Chromatin Accessibility</h3>
</div>
<p>Open chromatin profiling, peak calling, fragment filtering, and QC metrics.</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/scATAC.md">Workflow</a>
<a class="doc-pill-link" href="doc/parameter/scATAC.md">Parameters</a>
<a class="doc-pill-link" href="doc/outs/scATAC.md">Outputs</a>
</div>
</div>
</div>

## Common Tasks

| I want to... | Quick Link | Notes |
| :--- | :--- | :--- |
| **Run my first sample** | [Quick Start Guide →](doc/quickstart.md) | Human / mouse reference build and end-to-end examples |
| **Configure a C6 multi-sample experiment** | [C6 Configuration →](doc/parameter/c6.md) | `[samples]` section and multi-sample matrix demultiplexing |
| **Load matrices in R or Python** | [Downstream Analysis & Matrix Loading →](doc/io.md) | Sample scripts for Seurat and Scanpy |
| **Review changes from 3.1 to 3.2** | [Version Upgrade Guide →](doc/migration.md) | Matrix directory changes, C6 summaries, and compatibility |
| **Troubleshoot pipeline failures** | [Running & Troubleshooting →](doc/troubleshooting.md) | Memory limits, STAR parameters, and thread tuning |
| **Download example datasets** | [Example Datasets →](doc/dataset.md) | Public benchmark FASTQ files and genome references |

## Versions & Updates

The version selector in the header opens the **3.1 archive** in the current language. If the target version contains the current page, that page is opened; otherwise, the corresponding language homepage is opened. The default documentation entry is **3.2**.

Version 3.2 adds C6 multi-sample analysis and QC reporting, updated matrix outputs, ATAC default counting logic, and runtime diagnostics. See [Release Notes](doc/release.md) for full details.

> 💡 **Feedback & Issues**: [GitHub Issues](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/issues) · **Official Website**: [www.mgi-tech.com](https://www.mgi-tech.com)
