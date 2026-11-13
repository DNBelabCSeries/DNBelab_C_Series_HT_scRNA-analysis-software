<div align="center">

# DNBelab C Series™ HT Single-Cell Analysis Software

[![Github Release](https://img.shields.io/github/v/release/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software)](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://lishuangshuang0616.github.io/DNBelab_C_Series_HT_scRNA-analysis-software/Document/site/en/index.html)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://lishuangshuang0616.github.io/DNBelab_C_Series_HT_scRNA-analysis-software/Document/site/en/doc/installation.html)

A high-performance single-cell analysis toolkit for DNBelab C Series™ data. CLI tool: **`dnbc4tools`**.

**scRNA-seq** | **scATAC-seq** | **scVDJ-seq** | **Multi-omics**
</div>
<br>

---

## Documentation

> We recommend starting with the online manual for a complete guide to using this pipeline.

| Resource | Description |
|:---|:---|
| [**Documentation Home**](https://lishuangshuang0616.github.io/DNBelab_C_Series_HT_scRNA-analysis-software/Document/site/en/index.html) | Full reference documentation and tutorials |
| [**Installation Guide**](https://lishuangshuang0616.github.io/DNBelab_C_Series_HT_scRNA-analysis-software/Document/site/en/doc/installation.html) | System requirements and installation steps |
| [**Quick Start**](https://lishuangshuang0616.github.io/DNBelab_C_Series_HT_scRNA-analysis-software/Document/site/en/doc/quickstart.html) | Get up and running in minutes |

---

## What's New in v3.2 Beta

- **C6 multiplexed RNA**: Demultiplex sample barcodes and generate per-sample matrices, analyses and reports.
- **RNA and mixed-species analysis**: Update oligo filtering, UMI conflict handling, cell calling safeguards and species classification.
- **ATAC analysis**: Use cutsite-based peak calling and matrix counts by default; FRIP and TSS metrics remain fragment-based.
- **V(D)J analysis**: Update chain pairing, contig assembly and multithreaded sampling.
- **Outputs and operation**: Standardize RNA and ATAC matrices and H5 files, and add startup checks, process locks and structured diagnostics.

See the [Upgrade Guide](https://lishuangshuang0616.github.io/DNBelab_C_Series_HT_scRNA-analysis-software/Document/site/en/doc/migration.html) and [Release Notes](https://lishuangshuang0616.github.io/DNBelab_C_Series_HT_scRNA-analysis-software/Document/site/en/doc/release.html).

---

## Support & Community

- **Questions, bug reports, feature requests** → [GitHub Issues](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/issues)
- **Website** → [www.mgi-tech.com](https://www.mgi-tech.com)

---

## Version Note

This branch documents **v3.2 Beta**. The formal release package and release date have not yet been confirmed.
The documentation header can switch to the archived **3.1** manual.

For version **2.1.3**, use the [`version2.0`](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/tree/version2.0) branch.

