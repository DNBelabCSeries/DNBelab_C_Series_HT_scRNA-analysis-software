# 文档维护

站点默认版本是 **3.2**，历史版本为 **3.1**。沿用原有 MkDocs Material 外观及中英文页面结构。

- 当前文档源：仓库根目录 `doc/` 和 `Document/home/`。
- 3.1 冻结源：`Document/versions/3.1/`，保留本次修改前的 Markdown、图片、首页和配置。不要同步当前文档覆盖它。
- 主题资产：`Document/assets/`；配置：`Document/mkdocs.yml`。
- 构建结果：`Document/docs/` 为当前版本的预处理副本；`Document/site/` 为可直接部署的静态站点。

## 本地构建

```bash
python3 -m venv .venv-docs
.venv-docs/bin/python -m pip install -r Document/requirements.txt
PYTHON_BIN=.venv-docs/bin/python bash Document/build_mkdocs.sh
.venv-docs/bin/python Document/check_site.py
python3 -m http.server 8765 --bind 127.0.0.1
```

浏览 `http://127.0.0.1:8765/Document/site/index.html`。构建脚本不依赖特定用户的 Conda 路径，也可直接运行 `python Document/build_docs.py`。使用 `--site-dir` 可指定独立的输出目录。

构建会先在临时目录完成两个版本的严格 MkDocs 构建，再替换生成站点。不要仅运行一次 `mkdocs build` 覆盖双版本站点。

## URL 与版本切换

| 版本 | 中文 | English |
| :--- | :--- | :--- |
| 3.2（默认） | `site/index.html` | `site/en/index.html` |
| 3.1（历史） | `site/3.1/index.html` | `site/3.1/en/index.html` |

原来的 `site/doc/*.html` 链接继续指向当前 3.2。顶部版本切换保留语言、页面和查询参数；仅在目标页面存在对应章节时保留锚点，否则打开页面顶部。目标版本没有该页面时进入对应语言的首页。新开默认入口始终是 3.2，不保存浏览器版本偏好。语言切换保留当前版本，并根据构建生成的锚点清单匹配章节；C6 参数与输出页使用中英文共用的稳定章节 ID，旧锚点作为别名保留。3.1 页面有历史版本提示。

控件根据脚本自身 URL 定位站点根目录，无网络 manifest 请求，支持根路径和项目子路径部署，也可直接打开本地 HTML。`versions.json` 描述两个版本的可用页面、有效锚点与章节别名。两套搜索索引分别构建，避免检索时混入另一个版本。

`check_site.py` 校验 HTML 的本地链接、图片/脚本、锚点、版本页面清单，以及 3.1 冻结源的 SHA-256。它不请求外部下载链接。

## 3.2 内容依据

核对日期：2026-10-23。只读取相邻源码仓库，未修改分析代码。

| 来源 | 本次核对的 revision | 主要依据 |
| :--- | :--- | :--- |
| `dnbc4tools_py` | `096b386` | `domain/version.py`、实际九个公开叶子命令的 `--help`、`domain/output_names.py`、Multi 配置 parser/validator、RNA/ATAC 输出归档与运行实现 |
| `dnbc4rust` | `50566ed` | `BAM_OUTPUT.md`、`c4_summary/src/rna.rs` / `atac.rs`、矩阵和汇总导出契约 |
| 原 3.1 文档 | `c1b3140` | 当前 `version3.0` 分支修改前的 `doc/` 与 `Document/home/`；完整身份见 `versions/3.1/snapshot.json` |

3.2 源码记录仍为未发布，不推断正式下载地址、发布日期或校验值。不把源码实现或接口检查描述成生产数据回归通过。安装与升级页明确记录 Python 和原生工具需要配套部署。

## 写作与排版约定

3.2 正文使用语义化 Markdown，样式集中于 `assets/stylesheets/extra.css`；3.1 构建使用 `legacy.css`，冻结源继续保持原样。

- 每页保留一个标题和简短导语；使用二、三级标题组织阅读顺序。
- 中英文用语遵循 `doc/glossary.md` 与 `doc/glossary.en.md`；翻译保持默认值、单位、条件与能力范围一致，不额外添加性能倍数或效果承诺。命令、字段和 UI 标签保留软件原文。
- 参数页按命令组织：运行示例、参数分类、默认行为、高级设置。新参数融入所属命令，不再置顶添加版本补充块。
- Multi 配置先解释两种任务，再依次给出运行入口、CSV 规则、普通配置、C6 配置和高级选项。
- 输出页按目录、文件字段、报告指标排列；原有截图和关键格式说明保留。
- 长帮助、历史运行日志和高级调优使用带 `markdown="block"` 的原生 `details`，默认折叠。
- 表格用于可比较的规则与映射；说明段落不用内联配色、阴影、大卡片或重复页脚包装。

页面重排后仍运行 `check_site.py`；检查前后保持公开参数、报告截图与旧版本快照完整。
