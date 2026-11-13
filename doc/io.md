# 下游分析指南 {#_1}

本文档介绍如何将 DNBelab C Series™ 单细胞分析软件（`dnbc4tools`）输出的数据导入主流单细胞生信分析生态（**R / Seurat / Signac / scRepertoire / ArchR** 与 **Python / Scanpy / SnapATAC2 / AnnData / Scirpy**）进行深入的下游分析。

[scRNA 转录组](#scrna-analysis) • [C6 多样本 RNA](#c6-analysis) • [scATAC 染色质可及性](#scatac-analysis) • [scVDJ 免疫组库](#scvdj-analysis) • [核心产物速查](#common-output-files)

---

## 1. 单细胞转录组分析 (scRNA) <a id="scrna-analysis"></a>

3.2 版本在 `outs/` 根目录下同步交付规范化的 MEX 目录、H5 文件与 H5AD 文件。可根据下游工具选择单文件格式（`.h5` 或 `.h5ad`）；读取耗时和内存占用取决于矩阵规模、存储设备和读取方法。

### R 生态 (Seurat)

```r
library(Seurat)
library(dplyr)

# 方式一：推荐直接读取压缩 H5 格式（加载最快）
counts <- Read10X_h5("outs/filtered_feature_bc_matrix.h5")

# 方式二：读取标准 MEX 目录
# counts <- Read10X(data.dir = "outs/filtered_feature_bc_matrix")

# 创建 Seurat 对象
scRNA <- CreateSeuratObject(
  counts = counts,
  project = "dnbc4_rna",
  min.cells = 3,
  min.features = 200
)

# 计算线粒体比例并执行标准下游分析
scRNA[["percent.mt"]] <- PercentageFeatureSet(scRNA, pattern = "^MT-|^mt-")
scRNA <- NormalizeData(scRNA) %>%
  FindVariableFeatures(selection.method = "vst", nfeatures = 2000) %>%
  ScaleData() %>%
  RunPCA() %>%
  FindNeighbors(dims = 1:30) %>%
  FindClusters(resolution = 0.5) %>%
  RunUMAP(dims = 1:30)

# 可视化分群
DimPlot(scRNA, reduction = "umap", label = TRUE)
```

### Python 生态 (Scanpy)

```python
import scanpy as sc

# 方式一：推荐直接读取预置 AnnData 格式（即开即用）
adata = sc.read_h5ad("outs/filtered_feature_bc_matrix.h5ad")

# 方式二：读取 10X H5 格式
# adata = sc.read_10x_h5("outs/filtered_feature_bc_matrix.h5")

# 方式三：读取标准 MEX 文本目录
# adata = sc.read_10x_mtx("outs/filtered_feature_bc_matrix")

# 标准 Scanpy 下游质控、降维与分群
adata.var_names_make_unique()
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# 标记线粒体基因
adata.var["mt"] = adata.var_names.str.startswith(("MT-", "mt-"))
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True)

# 标准化与降维聚类
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata, svd_solver="arpack")
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)

# 可视化分群
sc.pl.umap(adata, color=["leiden"])
```

---

## 2. C6 多样本 RNA 分析 <a id="c6-analysis"></a>

C6 多样本流程在单个物理文库中对混合样本进行测序与解复用。分析结果同时交付**各样本输出目录**（`outs/rna/per_sample_outs/<sample>/`）以及**物理总文库目录**（`outs/rna/`）。

### 逐样本独立分析 (Per-Sample)

每个拆分样本具有过滤矩阵，可分别加载并开展下游分析：

```r
# R: 加载特定样本（如 Sample1）专属矩阵
library(Seurat)
sample1_counts <- Read10X_h5("outs/rna/per_sample_outs/Sample1/filtered_feature_bc_matrix.h5")
sample1_obj <- CreateSeuratObject(counts = sample1_counts, project = "Sample1")
```

```python
# Python: 加载特定样本专属 AnnData
import scanpy as sc
adata_s1 = sc.read_h5ad("outs/rna/per_sample_outs/Sample1/filtered_feature_bc_matrix.h5ad")
```

### 全量明细表与有效细胞过滤 (`singlecell.csv.gz`)

实际导出字段为 `cell,reads,gene,umi,is_cell_barcode,barcode`，不包含 `sample_id` 或 `cell_barcode`。以下示例从各样本已交付过滤矩阵的 `barcodes.tsv.gz` 建立完整 `cell` 标识到样本目录的映射，再筛选有效细胞；不通过截断条形码后缀推测样本名。若有失败或缺失的样本目录，应先排查未匹配的细胞。R 与 Python 示例可分别独立执行。

```r
library(data.table)

# Build sample membership from delivered filtered matrix barcode lists.
sample_dirs <- list.dirs("outs/rna/per_sample_outs", recursive = FALSE)
barcode_files <- file.path(sample_dirs, "filtered_feature_bc_matrix", "barcodes.tsv.gz")
barcode_files <- barcode_files[file.exists(barcode_files)]
if (!length(barcode_files)) stop("No per-sample filtered barcode files found")
cell_sample <- rbindlist(lapply(barcode_files, function(path) {
  con <- gzfile(path, "rt")
  cells <- readLines(con, warn = FALSE)
  close(con)
  cells <- cells[nzchar(cells)]
  data.table(cell = cells, sample_id = rep(basename(dirname(dirname(path))), length(cells)))
}))
if (anyDuplicated(cell_sample$cell)) stop("Cell IDs are not unique across samples")

meta_all <- fread(
  "outs/rna/singlecell.csv.gz",
  colClasses = list(character = c("cell", "is_cell_barcode"))
)
meta_cells <- meta_all[tolower(is_cell_barcode) %in% c("1", "true")]
meta_cells <- merge(meta_cells, cell_sample, by = "cell", all.x = TRUE, sort = FALSE)
if (anyNA(meta_cells$sample_id)) stop("Called cells lack sample assignments; check missing/failed outputs")
if (anyDuplicated(meta_cells$cell)) stop("Duplicate called-cell rows")
table(meta_cells$sample_id)
```

```python
from collections import Counter
from pathlib import Path
import csv
import gzip

# Build sample membership without parsing or truncating barcode suffixes.
barcode_files = sorted(Path("outs/rna/per_sample_outs").glob(
    "*/filtered_feature_bc_matrix/barcodes.tsv.gz"
))
if not barcode_files:
    raise ValueError("No per-sample filtered barcode files found")
cell_to_sample = {}
for path in barcode_files:
    sample_id = path.parents[1].name
    with gzip.open(path, "rt", newline="") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if not row or not row[0]:
                continue
            cell = row[0]
            if cell in cell_to_sample:
                raise ValueError(f"Duplicate cell ID in sample barcode lists: {cell}")
            cell_to_sample[cell] = sample_id

# Stream the full table and write only mapped, called cells.
counts = Counter()
seen_cells = set()
with gzip.open("outs/rna/singlecell.csv.gz", "rt", newline="") as source, \
        open("called_cell_metadata.csv", "w", newline="") as output:
    reader = csv.DictReader(source)
    if not {"cell", "is_cell_barcode"}.issubset(reader.fieldnames or []):
        raise ValueError("Missing cell or is_cell_barcode column")
    writer = csv.DictWriter(output, fieldnames=list(reader.fieldnames) + ["sample_id"])
    writer.writeheader()
    for row in reader:
        if row["is_cell_barcode"].strip().lower() not in {"1", "true"}:
            continue
        cell = row["cell"]
        if cell not in cell_to_sample:
            raise ValueError(f"Called cell lacks a sample assignment: {cell}")
        if cell in seen_cells:
            raise ValueError(f"Duplicate called-cell row: {cell}")
        seen_cells.add(cell)
        row["sample_id"] = cell_to_sample[cell]
        writer.writerow(row)
        counts[row["sample_id"]] += 1
print(dict(counts))
```

Python 示例输出 `called_cell_metadata.csv`，其中 `sample_id` 是根据样本矩阵建立的派生字段，原始细胞标识列仍为 `cell`。

### 多样本联合分析与批次校正

当需要对 C6 文库中的多个样本进行联合分析时，可直接加载全局合并矩阵 `outs/rna/filtered_feature_bc_matrix.h5`（或 `.h5ad`），并挂载拆分后的 `sample_id` 元数据，再通过 Harmony 或 Seurat v5 执行去批次整合：

```r
library(Seurat)
library(harmony)

# 读取全局合并矩阵
all_counts <- Read10X_h5("outs/rna/filtered_feature_bc_matrix.h5")
merged_obj <- CreateSeuratObject(counts = all_counts, project = "C6_Pool")

# Use meta_cells from the R mapping example above.
meta_df <- as.data.frame(meta_cells)
stopifnot(!anyDuplicated(meta_df$cell))
rownames(meta_df) <- meta_df$cell
common_cells <- intersect(colnames(merged_obj), rownames(meta_df))
if (!length(common_cells)) stop("No matching cell IDs")
merged_obj <- merged_obj[, common_cells]
merged_obj$sample_id <- meta_df[colnames(merged_obj), "sample_id"]

# 执行 Harmony 去批次整合
merged_obj <- NormalizeData(merged_obj) %>%
  FindVariableFeatures() %>%
  ScaleData() %>%
  RunPCA() %>%
  RunHarmony(group.by.vars = "sample_id") %>%
  RunUMAP(reduction = "harmony", dims = 1:30)

DimPlot(merged_obj, reduction = "umap", group.by = "sample_id")
```

---

## 3. 单细胞 ATAC 染色质可及性分析 (scATAC) <a id="scatac-analysis"></a>

!!! note "计数口径特别说明"
    3.2 版本的 Peak 召回与表达矩阵计数默认切换为 **cutsite** 口径（即经 9 bp 偏移修正后的实际 Tn5 插入切割位点），相比全长 fragment 更高保真地反映局部开放；而全局 FRIP 与 TSS 指标仍基于唯一 fragment 计算。

### R 生态 (Signac)

下面的 H5 和 MTX 读取方式任选一种，再执行公共的 Signac 分析代码。MTX 读取同一目录下的 `matrix.mtx.gz`、`peaks.bed.gz` 和 `barcodes.tsv.gz`；矩阵的行为峰、列为细胞。

#### H5 读取 {#atac-r-h5}

```r
counts <- Seurat::Read10X_h5("outs/filtered_peak_bc_matrix.h5")
peak_ranges <- NULL
```

#### MTX 读取 {#atac-r-mtx}

```r
read_atac_mtx <- function(mex_dir) {
  matrix_con <- gzfile(file.path(mex_dir, "matrix.mtx.gz"), "rt")
  on.exit(close(matrix_con), add = TRUE)
  counts <- as(Matrix::readMM(matrix_con), "CsparseMatrix")

  peaks <- read.delim(gzfile(file.path(mex_dir, "peaks.bed.gz")),
                      header = FALSE, colClasses = c("character", "integer", "integer"))
  barcodes <- read.delim(gzfile(file.path(mex_dir, "barcodes.tsv.gz")),
                         header = FALSE, colClasses = "character")[[1]]
  stopifnot(nrow(counts) == nrow(peaks), ncol(counts) == length(barcodes))
  rownames(counts) <- paste0(peaks[[1]], ":", peaks[[2]], "-", peaks[[3]])
  colnames(counts) <- barcodes

  # BED: 0-based, half-open; GRanges: 1-based, closed.
  peak_ranges <- GenomicRanges::GRanges(
    seqnames = peaks[[1]],
    ranges = IRanges::IRanges(start = peaks[[2]] + 1L, end = peaks[[3]])
  )
  list(counts = counts, ranges = peak_ranges)
}

mtx_data <- read_atac_mtx("outs/filtered_peak_bc_matrix")
counts <- mtx_data$counts
peak_ranges <- mtx_data$ranges
```

#### Signac 公共分析代码 {#atac-r-analysis}

使用所选读取方式生成的 `counts` 和 `peak_ranges`。MTX 示例将 BED 坐标显式转换为 Signac 使用的 1-based 区间；匹配元数据和 fragments 时保留完整细胞条形码。

```r
library(Signac)
library(Seurat)
library(GenomicRanges)

# 2. 读取细胞元数据并筛选有效细胞
metadata <- read.csv("outs/singlecell.csv", row.names = 1)
metadata <- metadata[metadata$is_cell_barcode %in% c(1, "True", "true"), ]

# 对齐条形码
common_cells <- intersect(colnames(counts), rownames(metadata))
counts <- counts[, common_cells, drop = FALSE]
metadata <- metadata[common_cells, , drop = FALSE]

# 3. 创建 ChromatinAssay（绑定 fragments 文件）
chrom_assay <- CreateChromatinAssay(
  counts = counts,
  ranges = peak_ranges,
  sep = c(":", "-"),
  fragments = "outs/fragments.tsv.gz",
  min.cells = 10,
  min.features = 200
)

# 4. 创建 Seurat 对象并执行 TF-IDF 与 LSI 降维
scATAC <- CreateSeuratObject(counts = chrom_assay, assay = "peaks", meta.data = metadata)
scATAC <- RunTFIDF(scATAC) %>%
  FindTopFeatures(min.cutoff = "q0") %>%
  RunSVD() %>%
  RunUMAP(reduction = "lsi", dims = 2:30) %>%
  FindNeighbors(reduction = "lsi", dims = 2:30) %>%
  FindClusters(algorithm = 3, resolution = 0.5)

DimPlot(scATAC, reduction = "umap", label = TRUE)
```

### R 生态 (ArchR)

ArchR 专为超大规模单细胞 ATAC 分析设计。可使用 `fragments.tsv.gz`（全量片段）或 `filtered.fragments.tsv.gz`（细胞过滤后片段）生成 Arrow 文件：

```r
library(ArchR)
addArchRThreads(threads = 16)
addArchRGenome("hg38") # 按实际参考基因组设定

# 基于 dnbc4tools 过滤后的片段文件快速创建 Arrow
ArrowFiles <- createArrowFiles(
  inputFiles = "outs/filtered.fragments.tsv.gz",
  sampleNames = "Sample_ATAC",
  filterTSS = 4,
  filterFrags = 1000,
  addTileMat = TRUE,
  addGeneScoreMat = TRUE
)

proj <- ArchRProject(ArrowFiles = ArrowFiles, outputDirectory = "ArchR_Output")
proj <- addIterativeLSI(ArchRProj = proj, useMatrix = "TileMatrix", name = "IterativeLSI")
proj <- addUMAP(ArchRProj = proj, reducedDims = "IterativeLSI")
plotEmbedding(proj, colorBy = "cellColData", name = "Sample")
```

### Python 生态 (SnapATAC2)

这里使用已有 peak 计数矩阵，通过 [SnapATAC2](https://snapatac2.scverse.org/version/2.10/index.html) 完成特征选择、谱嵌入、近邻图构建和聚类。`adata_atac.X` 保留原始 cutsite 计数，该流程无需执行 RNA 示例中的总计数归一化、对数转换、高变基因筛选或 PCA。

下面的 H5 和 MTX 读取方式任选一种。Scanpy 仅用于读取兼容 10x 格式的 H5 文件；ATAC 峰不是基因表达特征，因此需要传入 `gex_only=False`。MTX 则显式读取峰 BED 文件，不能假设存在 `features.tsv.gz`。两种方式均生成内存中的 AnnData 对象，再执行公共的 SnapATAC2 分析代码。

#### H5 读取 {#atac-python-h5}

```python
import scanpy as sc

# 读取 ATAC 过滤 peak 矩阵
adata_atac = sc.read_10x_h5("outs/filtered_peak_bc_matrix.h5", gex_only=False)
adata_atac.var_names_make_unique()
```

#### MTX 读取 {#atac-python-mtx}

`read_atac_C4` 分别读取峰 BED 和完整细胞条形码，再将稀疏矩阵转置为 AnnData 使用的“细胞 × 峰”布局。`adata_atac.var` 中的 BED 坐标保留原始的 0-based、左闭右开约定。

```python
from pathlib import Path

import anndata as ad
import pandas as pd
from scipy.io import mmread
from scipy.sparse import csr_matrix


def read_atac_C4(path):
    mex_dir = Path(path)
    counts = mmread(str(mex_dir / "matrix.mtx.gz"))
    barcodes = pd.read_csv(
        mex_dir / "barcodes.tsv.gz", sep="\t", header=None, dtype=str,
        keep_default_na=False,
    )[0]
    peaks = pd.read_csv(
        mex_dir / "peaks.bed.gz", sep="\t", header=None,
        names=["chrom", "chromStart", "chromEnd"],
        dtype={"chrom": str, "chromStart": int, "chromEnd": int},
        keep_default_na=False,
    )
    if counts.shape != (len(peaks), len(barcodes)):
        raise ValueError("Matrix dimensions do not match peaks and barcodes")
    obs = pd.DataFrame(index=pd.Index(barcodes, name="barcode"))
    peaks.index = pd.Index(
        peaks["chrom"] + ":" + peaks["chromStart"].astype(str)
        + "-" + peaks["chromEnd"].astype(str), name="peak",
    )
    # Matrix Market: peaks x cells; AnnData: cells x peaks.
    adata = ad.AnnData(X=csr_matrix(counts.T), obs=obs, var=peaks)
    adata.var_names_make_unique()
    return adata


adata_atac = read_atac_C4("outs/filtered_peak_bc_matrix")
```

#### SnapATAC2 公共分析代码 {#atac-python-analysis}

先选择上面的一种读取方式，再执行以下代码。调用方式参考 [SnapATAC2 2.10 特征选择接口](https://snapatac2.scverse.org/version/2.10/api/_autosummary/snapatac2.pp.select_features.html)和[谱嵌入接口](https://snapatac2.scverse.org/version/2.10/api/_autosummary/snapatac2.tl.spectral.html)。示例最多选择 50,000 个峰、计算 30 个谱嵌入分量；特征数、分量数、近邻数和聚类分辨率需按数据调整。示例要求矩阵非空，且有足够的细胞和峰支持这些设置。

本示例基于已输出的 peak 矩阵完成聚类。重新计算 TSS 富集、构建基因活性矩阵等依赖片段信息的操作，需要另行导入 fragments 文件。

```python
import snapatac2 as snap
from scipy.sparse import csr_matrix

# 保留原始 cutsite 计数，转换为稀疏 CSR 格式
adata_atac.X = csr_matrix(adata_atac.X)

snap.pp.select_features(adata_atac, n_features=min(50000, adata_atac.n_vars))
snap.tl.spectral(adata_atac, n_comps=30, random_state=0)
snap.pp.knn(adata_atac, n_neighbors=15, use_rep="X_spectral")
snap.tl.leiden(adata_atac, resolution=0.5, random_state=0)
snap.tl.umap(adata_atac, use_rep="X_spectral", random_state=0)
snap.pl.umap(adata_atac, color="leiden", show=True)
```

---

## 4. 单细胞 V(D)J 免疫组库分析 (scVDJ) <a id="scvdj-analysis"></a>

scVDJ 核心输出文件为 `outs/filtered_contig_annotations.csv`，记录了每个有效细胞的高置信度 TCR / BCR 链重排、CDR3 氨基酸与克隆型分类。

### R 生态 (scRepertoire 与 Seurat 联合分析)

[scRepertoire](https://github.com/ncborcherding/scRepertoire) 是结合单细胞 RNA 与免疫受体分析的常用工具：

```r
library(scRepertoire)
library(Seurat)

# 1. 读取 VDJ contig 注释表
contigs <- read.csv("outs/filtered_contig_annotations.csv")

# 2. 组合 TCR（或 BCR）克隆型数据
combined_tcr <- combineTCR(
  list(Sample1 = contigs),
  samples = "Sample1",
  removeNA = FALSE
)

# 3. 读取已分析好的 scRNA Seurat 对象
scRNA <- readRDS("scRNA_analyzed.rds")

# 4. 将免疫克隆型元数据映射到 scRNA 细胞上
scRNA <- combineExpression(
  combined_tcr,
  scRNA,
  cloneCall = "gene",
  proportion = FALSE
)

# 可视化前 Top 克隆型在 RNA 聚类群中的空间富集
DimPlot(scRNA, group.by = "cloneSize")
```

### Python 生态 (Scirpy 与 Scanpy 联合分析)

[Scirpy](https://scirpy.readthedocs.io/) 可与 Scanpy 配合使用，是 Python 的免疫组库分析库：

```python
import scanpy as sc
import scirpy as ir

# 1. 读取 RNA 与 VDJ 数据
adata_rna = sc.read_h5ad("outs/filtered_feature_bc_matrix.h5ad")
adata_vdj = ir.io.read_10x_vdj("outs/filtered_contig_annotations.csv")

# 2. 质控并对齐免疫受体链
ir.pp.index_chains(adata_vdj)

# 3. 将 VDJ 克隆型数据合并入 RNA AnnData
ir.pp.merge_with_ir(adata_rna, adata_vdj)

# 4. 分析克隆型重组与多样性
ir.tl.chain_qc(adata_rna)
ir.tl.clonal_expansion(adata_rna)

# 可视化克隆扩增在 RNA UMAP 上的分布
sc.pl.umap(adata_rna, color=["clonal_expansion", "has_ir"])
```

---

## 5. 核心交付产物速查 <a id="common-output-files"></a> {#6}

下表汇总了各流程交付的核心分析文件、对应格式以及在 R 与 Python 中的主流读取方式：

| 交付文件 / 目录 | 数据格式 | 适用流程 | R 推荐读取函数 | Python 推荐读取函数 | 核心用途与下游分析 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `filtered_feature_bc_matrix.h5` | HDF5 (`.h5`) | scRNA / C6 / Multi | `Seurat::Read10X_h5()` | `scanpy.read_10x_h5()` | 细胞过滤后的基因表达定量矩阵（单文件快速加载） |
| `filtered_feature_bc_matrix.h5ad` | AnnData (`.h5ad`) | scRNA / C6 / Multi | `anndata::read_h5ad()` | `scanpy.read_h5ad()` | 预封装稀疏矩阵与特征元数据的单文件（Python 首选） |
| `filtered_feature_bc_matrix/` | MEX 目录 (`.mtx.gz`) | scRNA / C6 / Multi | `Seurat::Read10X()` | `scanpy.read_10x_mtx()` | 经典 10X 兼容三件套文本目录 |
| `filtered_peak_bc_matrix.h5` | HDF5 (`.h5`) | scATAC / Multi | `Seurat::Read10X_h5()` | `scanpy.read_10x_h5(gex_only=False)` | 细胞过滤后的染色质开放峰可及性矩阵 |
| `filtered_peak_bc_matrix/` | MEX | scATAC / Multi | `Matrix::readMM()` + `read.delim()` | `scipy.io.mmread()` + `pandas.read_csv()` | 分别读取 `matrix.mtx.gz`、`peaks.bed.gz` 和 `barcodes.tsv.gz`；矩阵行为峰、列为细胞 |
| `fragments.tsv.gz` | TAB 文本 (带索引) | scATAC / Multi | `Signac::CreateChromatinAssay()` | `pysam.TabixFile()` | Tn5 测序片段坐标明细（含插入切割位点） |
| `filtered_contig_annotations.csv` | CSV 文本 | scVDJ / Multi | `scRepertoire::combineTCR()` | `scirpy.io.read_10x_vdj()` | 高置信度免疫受体 CDR3 与全长 Contig 注释 |
| `singlecell.csv.gz` / `singlecell.csv` | CSV 压缩文本 | scRNA / scATAC / C6 / Multi | `data.table::fread()` | `pandas.read_csv()` | 全量液滴元信息与质控指标（须按 `is_cell_barcode==1` 筛选） |
| `metrics_summary.xls` | 制表符纯文本 (TSV) | 全部流程 | `read.delim(check.names=F)` | `pandas.read_csv(sep="\t")` | 核心质控指标总览（不可用 Excel 专属包读取） |

*更详尽的各流程输出层级与指标字段定义请参阅 [分析输出概览](./outs/outs.md)。*
