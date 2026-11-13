<div class="doc-hero-badge">
  <span class="doc-badge-pill">v3.2 开发版文档</span>
  <span class="doc-badge-sub">DNBC4TOOLS 单细胞生信套件</span>
</div>

# DNBelab C Series™ HT 单细胞分析软件

面向 DNBelab C Series™ 高通量单细胞测序数据的分析工具，命令行工具为 **`dnbc4tools`**。支持单细胞 RNA、ATAC、V(D)J 及 C6 多样本实验的质控、定量、注释与交互式 HTML 报告。

<div class="doc-actions">
<a href="doc/quickstart.md" class="doc-btn-primary">快速开始 →</a>
<a href="doc/installation.md" class="doc-btn-outline">软件安装指南</a>
<a href="doc/migration.md" class="doc-btn-outline">3.1 → 3.2 升级指南</a>
</div>

## 分析类型

<div class="doc-module-grid">
<div class="doc-module mod-rna">
<div class="doc-module-header">
  <span class="doc-module-tag">scRNA</span>
  <h3>RNA 单细胞分析</h3>
</div>
<p>基因表达定量、细胞识别（EmptyDrops）、UMI 纠错与细胞聚类分析。</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/scRNA.md">流程</a>
<a class="doc-pill-link" href="doc/parameter/scRNA.md">参数说明</a>
<a class="doc-pill-link" href="doc/outs/scRNA.md">输出结果</a>
</div>
</div>
<div class="doc-module mod-multi">
<div class="doc-module-header">
  <span class="doc-module-tag">Multi</span>
  <h3>多组学联合分析</h3>
</div>
<p>单细胞 RNA、ATAC 与 V(D)J 多组学文库统一调度、质量控制与跨组学交互式组合报告。</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/multi.md">流程</a>
<a class="doc-pill-link" href="doc/parameter/multi.md">参数说明</a>
<a class="doc-pill-link" href="doc/outs/multi.md">输出结果</a>
</div>
</div>
<div class="doc-module mod-vdj">
<div class="doc-module-header">
  <span class="doc-module-tag">scVDJ</span>
  <h3>V(D)J 免疫组库</h3>
</div>
<p>TCR / BCR 全长序列从头组装、V(D)J 基因注释与克隆型识别。</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/scVDJ.md">流程</a>
<a class="doc-pill-link" href="doc/parameter/scVDJ.md">参数说明</a>
<a class="doc-pill-link" href="doc/outs/scVDJ.md">输出结果</a>
</div>
</div>
<div class="doc-module mod-c6">
<div class="doc-module-header">
  <span class="doc-module-tag">C6</span>
  <h3>C6 多样本 RNA 分析</h3>
</div>
<p>支持样本条形码解复用，并为各样本分别生成分析结果。</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/c6.md">流程</a>
<a class="doc-pill-link" href="doc/parameter/c6.md">参数说明</a>
<a class="doc-pill-link" href="doc/outs/c6.md">输出结果</a>
</div>
</div>
<div class="doc-module mod-atac">
<div class="doc-module-header">
  <span class="doc-module-tag">scATAC</span>
  <h3>ATAC 染色质可及性</h3>
</div>
<p>染色质开放区分析、峰检测（Peak Calling）、Fragment 过滤与质控分析。</p>
<div class="doc-module-links">
<a class="doc-pill-link" href="doc/pipeline/scATAC.md">流程</a>
<a class="doc-pill-link" href="doc/parameter/scATAC.md">参数说明</a>
<a class="doc-pill-link" href="doc/outs/scATAC.md">输出结果</a>
</div>
</div>
</div>

## 常用任务导航

| 我想…… | 快速直达 | 重点说明 |
| :--- | :--- | :--- |
| **运行第一份样本** | [快速开始指南 →](doc/quickstart.md) | 包含人/小鼠参考库构建与端到端示例脚本 |
| **配置 C6 多样本实验** | [C6 参数配置 →](doc/parameter/c6.md) | 支持 `[samples]` 配置与多样本表达矩阵拆分 |
| **在 R / Python 中读取分析结果** | [结果分析与矩阵加载 →](doc/io.md) | 提供 Seurat、Scanpy 读取示例代码 |
| **了解 3.1 升至 3.2 的变更** | [版本升级指南 →](doc/migration.md) | 涵盖目录结构变更、C6 汇总与兼容性注意事项 |
| **排查运行报错与性能调优** | [运行与排错指南 →](doc/troubleshooting.md) | 内存占用、STAR 比对参数及线程数推荐 |
| **获取测试数据集** | [示例数据集下载 →](doc/dataset.md) | 包含官方公共测试 FASTQ 数据与参考基因组 |

## 版本与更新说明

顶部导航栏的版本下拉菜单可切换至 **3.1 历史归档文档**，切换时保留当前语言；若目标版本包含当前页面，则打开该页面，否则进入对应语言的首页。

3.2 版本新增 C6 样本分析与质控报告，更新了矩阵输出格式、ATAC 默认计数逻辑及运行时诊断机制。完整升级详情请参阅[版本说明](doc/release.md)。

> 💡 **问题反馈与建议**：[GitHub Issues](https://github.com/MGI-tech-bioinformatics/DNBelab_C_Series_HT_scRNA-analysis-software/issues) · **官方网站**：[www.mgi-tech.com](https://www.mgi-tech.com)
