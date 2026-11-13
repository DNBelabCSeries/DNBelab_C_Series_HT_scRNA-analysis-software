# Pipeline Overview

Choose a workflow based on your assay and sequencing design.

| Module | Core Steps | Guide |
| :--- | :--- | :--- |
| RNA | cDNA/oligo QC → Alignment & UMI counting → Cell calling → Clustering & report | [RNA pipeline](scRNA.md) |
| ATAC | Fragment processing → Bead merging → Peak calling & matrix → Cell QC & clustering | [ATAC pipeline](scATAC.md) |
| V(D)J | QC → De novo assembly → Annotation & filtering → Clonotypes & report | [VDJ pipeline](scVDJ.md) |
| Multi-omics | CSV configuration → Modality dispatch → Result archiving → Combined report | [Multi pipeline](multi.md) |
| C6 Multiplexed | Shared library → Sample Barcode demultiplexing → Per-sample cell calling & analysis | [C6 pipeline](c6.md) |

## Workflow Selection

- **Independent Single-Omics**: Run the respective pipeline directly (`scRNA`, `scATAC`, or `scVDJ`). VDJ accepts an optional RNA `singlecell.csv` for bead mapping and cell filtering; omitting `--beadstrans` automatically enables `keep_all_cells`.
- **Multi-omics (Multi)**: When RNA, ATAC, or VDJ data are generated for the same batch, use a single CSV file to orchestrate modules and generate combined reports.
- **C6 Multiplexed RNA**: For pooled libraries with Sample Barcodes, configure the `[samples]` section to automate demultiplexing and per-sample deliverables.
