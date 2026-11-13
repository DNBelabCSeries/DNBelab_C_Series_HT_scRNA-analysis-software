# 版本说明

**DNBelab C Series™ HT 单细胞分析软件版本更新记录**

[开发版本](#latest-release) • [过往版本](#release-history) • [版本选择指南](#version-selection-guide)

## 开发版本 <a id="latest-release"></a>

**dnbc4tools 3.2 — 开发版文档（未发布）**，文档更新于 2026 年 10 月 23 日。

正式发布日期、安装包和校验值待确认。本次更新前记录的最新发布版本为 3.1（2026 年 5 月 15 日）。

### 3.2 主要更新内容 <a id="32-source"></a>

- **C6 多样本 RNA 分析**：支持在单个物理文库中混合测序并通过 Sample Barcode 自动拆分样本，独立交付各样本的表达矩阵（MEX / H5 / H5AD）、比对 BAM（`[rna] no_bam` 默认为 `false` 时生成）及交互式 HTML 报告。
- **双物种区分算法升级**：引入双向背景预测带模型与两阶段稳健 Huber 回归，替代固定硬阈值规则，用于评估细胞物种归属。
- **scRNA 算法与过滤优化**：更新 Oligo Read 2 过滤规则；完善跨基因同 UMI 冲突裁决；增加 Cell Calling 自动预测上下限保护。
- **scATAC 核心升级**：Peak 召回与表达矩阵计数口径切换为 cutsite（经 9 bp 偏移修正的实际 Tn5 切割位点）；FRIP 与 TSS 保持基于唯一 fragment 统计。
- **scVDJ 算法升级**：更新链配对、全长重叠群（Full-length Contigs）拼接和多线程抽样的确定性处理。
- **输出规范与工程底座**：统一 RNA/ATAC 表达矩阵目录命名并同级提供 `.h5` 文件；批处理脚本解耦至当前目录生成；引入启动预检、运行锁、结构化错误跟踪及日志诊断压缩包。

更详尽的算法原理、参数与输出适配说明请参阅[升级指南](migration.md)。顶部版本菜单可打开冻结的 3.1 完整文档。

## 过往版本记录 <a id="release-history"></a> <a id="legacy-version-notes"></a>

以下为过往版本更新记录（按时间倒序）：

<details markdown="block">
<summary><strong>3.1（2026-05-15）</strong> <a id="31-2026-05-15"></a></summary>

- **新增多组学模式**：支持单样本多组学分析，可执行 RNA + VDJ 联合分析或单组学独立分析。
- **RNA 功能增强与修复**：新增 `--consistent_cells` 参数以复用已有合并结果并保持细胞分配一致性；修复 Fraction Reads in Cells 指标计算；修复双物种数据库在物种名称包含下划线时的异常问题。
- **性能优化与 CLI 规范**：优化 `bam2fastq` 与 `fqsubC4` 运行效率；统一各模块帮助文本与命令行参数展示格式（含 multi 命令）。

</details>

<details markdown="block">
<summary><strong>3.0（2025-12-18）</strong></summary>

- **RNA 模块增强**：
    - 优化比对与注释优先级，提升定量准确性；
    - 新增含 N 碱基 barcode 纠错逻辑；
    - 增强双物种参考库构建和分析支持；
    - 丰富 BAM 与矩阵输出字段；
    - 新增 `minumi`，优化 `expectcells` 自动估计。
- **ATAC 模块增强**：
    - 扩展 Q30、插入片段长度等质控指标；
    - 升级比对引擎并优化 barcode 纠错与 BAM 输出。
- **VDJ 模块增强**：
    - 改进单细胞组装与注释流程，提高全长 contig 恢复能力；
    - 优化内存管理，减少预加载压力；
    - 增强 `contig_annotations.csv` 与报告内容；
    - 支持非人/鼠物种自定义参考库构建。
- **跨模块改进**：
    - 统一 `customize` 参数行为；
    - 优化中间文件组织，降低磁盘占用；
    - 弃用 `process` 参数并自动清理中间文件。

</details>

<details markdown="block">
<summary><strong>2.1.3（2024-10-09）</strong></summary>

- **新增功能**：
    - 新增 RNA 5' 转录组分析模块；
    - 新增单细胞 VDJ 分析模块；
    - 新增 GTF 文件格式检查与修正功能。
- **安装与性能**：
    - 以 `tar.gz` 发布，减少环境配置依赖；
    - 移除 conda 安装方式；
    - 修复 scATAC 合并过程中的内存异常；
    - 优化 RNA 比对与注释性能。

</details>

<details markdown="block">
<summary><strong>2.1.2（2024-04-24）</strong></summary>

- **ATAC 改进**：
    - 细胞识别策略由 Jaccard 合并升级为 peak fragment 驱动；
    - 新增多个过滤参数并支持 BAM 输入；
    - 增强参考库构建中的叶绿体处理；
    - 统一 RNA/ATAC 网页报告风格。
- **通用改进**：
    - 简化安装流程（移除 R 包依赖）；
    - 优化 barcode/UMI 区域 N 碱基过滤逻辑。

</details>

<details markdown="block">
<summary><strong>2.1.1（2023-09-21）</strong></summary>

- **RNA 流程优化**：
    - 细胞识别前先使用 oligo 数据执行微珠合并分析；
    - 优化 marker gene 展示逻辑（每群体展示 top50）。
- **问题修复**：
    - 修复容器环境下的高内存占用问题；
    - 修复 ATAC 报告图像显示异常。

</details>

<details markdown="block">
<summary><strong>2.1.0（2023-07-28）</strong></summary>

- **主要新增**：
    - 新增 ATAC 分析模块。
- **RNA 更新**：
    - 参考库构建流程优化，增加 `ref.json` 信息文件；
    - 降维聚类由 Seurat 切换为 Scanpy 以提升速度。

</details>

<details markdown="block">
<summary><strong>2.0.7（2022-11-04）</strong></summary>

- **自动化与参数**：
    - 支持试剂版本和暗反应周期自动识别；
    - 新增参数：`chemistry`、`darkreaction`、`customize`；
    - 移除 `mixseq` 参数。
- **技术改进**：
    - 增加 RNA cDNA 文库接头序列切除；
    - 新增 `limitram` 以优化参考库构建内存控制。

</details>

<details markdown="block">
<summary><strong>2.0.6（2022-09-19）</strong></summary>

- **容器与稳定性**：
    - 新增 Singularity 支持；
    - 修复结果一致性相关问题；
    - 修复 cDNA 文库 Q30 与 barcode 统计异常。

</details>

<details markdown="block">
<summary><strong>2.0.5（2022-08-19）</strong></summary>

- **容器与格式兼容**：
    - 新增 Docker 版本；
    - 放宽 GTF 字段格式要求；
    - 优化默认参数与异常处理逻辑。

</details>

<details markdown="block">
<summary><strong>2.0.0（2022-06-20）</strong></summary>

- **主要发布**：
    - 新增命令行工具支持；
    - 增强流程稳定性与异常处理能力；
    - 优化比对与注释性能；
    - 默认使用 emptydrops 细胞识别方法；
    - 新增饱和度分析与细胞类型注释。

</details>

## 版本选择指南 <a id="version-selection-guide"></a>

<table>
  <thead>
    <tr>
      <th>版本</th>
      <th>关键能力</th>
      <th>推荐场景</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>3.2（开发版）</b></td>
      <td>C6 多样本 RNA 分析</td>
      <td>C6 多样本混合分析</td>
    </tr>
    <tr>
      <td><b>3.1+</b></td>
      <td>多组学（RNA + VDJ）</td>
      <td>RNA + VDJ 联合分析</td>
    </tr>
    <tr>
      <td><b>2.1.3+</b></td>
      <td>RNA 5'、VDJ</td>
      <td>VDJ、5' RNA</td>
    </tr>
    <tr>
      <td><b>2.1.0+</b></td>
      <td>支持 ATAC 分析</td>
      <td>ATAC-seq 分析</td>
    </tr>
    <tr>
      <td><b>2.0.0+</b></td>
      <td>命令行工具支持</td>
      <td>标准 3' RNA 分析</td>
    </tr>
  </tbody>
</table>

### 历史版本获取

旧版本的下载链接与安装说明可参考[旧版安装指南](./installation_previous.md)。更多发布信息可参考 [GitHub Releases](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/releases)。

!!! note "版本状态说明"
    - **Stable（稳定版）**：推荐用于生产环境，持续接收安全更新与关键缺陷修复。
    - **Release Candidate (RC)**：功能基本冻结，适合最终验证与预生产测试；可能仍有小范围修复。
    - **Beta（测试版）**：仅用于测试与开发，接口和行为可能变动。

---

*详细安装与使用说明请参考[安装指南](./installation.md)与[快速开始](./quickstart.md)。*
