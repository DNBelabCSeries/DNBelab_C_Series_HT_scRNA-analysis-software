# Parameter Overview

Find commands, configuration specifications, and default parameter settings by module. Each module documentation page provides complete parameter quick references, detailed options, and full CLI help.

| Module | Primary Commands | Use Case | Parameter Reference |
| :--- | :--- | :--- | :--- |
| **scRNA** | `rna run`, `rna mkref`, `rna multi` | Single-cell RNA (3' / 5') profiling, reference building, and batch script generation | [RNA Parameters](scRNA.md) |
| **scATAC** | `atac run`, `atac mkref`, `atac multi` | Chromatin accessibility analysis, Chromap index & reference building, batch processing | [ATAC Parameters](scATAC.md) |
| **scVDJ** | `vdj run` | Full-length TCR/BCR immune repertoire assembly and clonotype profiling | [VDJ Parameters](scVDJ.md) |
| **Multi-omics** | `multi run` (with sectioned CSV) | Simultaneous multi-modal analysis (RNA + ATAC + VDJ) with unified orchestration and combined reporting | [Multi Parameters](multi.md) |
| **C6 Multiplexed** | `multi run` (with `[samples]`) | Sample Barcode demultiplexing, per-sample cell calling, and independent matrix generation | [C6 Parameters](c6.md) |
| **GTF Tools** | `tools mkgtf` | GTF annotation filtering, gene type filtering, and format validation | [Tools](tools.md) |

## Entry Point Recommendations

- **Individual Sample Analysis**: For an independent library, run the corresponding module command directly (e.g., `rna run`, `atac run`, `vdj run`).
- **Batch Script Generation**: `rna multi` and `atac multi` generate independent shell scripts for each sample based on a tab-separated list; verify scripts before launching.
- **Multi-Omics and Multiplexing**: Use `multi run` exclusively. Configure via a CSV file: declare `[rna]`, `[atac]`, `[vdj-*]` sections for multi-modal assays, and add `[samples]` for C6 probe demultiplexing.

## Key Configuration Principles

- **Default Values**: Omitted options adopt recommended pipeline defaults. Note that not all options accept the explicit literal string `auto`.
- **Parameter Types**: CLI boolean switches are flags that take no values (e.g., `--no_bam`, `--end5`), whereas in Multi CSV files, boolean values must be explicitly written as `true` or `false`.
- **Precedence & Overrides**: In multi-sample and multi-omics runs, when sample-level overrides conflict with global settings, the inheritance rules defined in each module's parameter documentation apply.
