# 运行与排错

本指南汇总了 DNBelab C Series™ 单细胞分析软件（`dnbc4tools`）在分析运行、日志审计、故障诊断及断点恢复等方面的核心知识与排查步骤。

---

## 运行前检查与预检机制 <a id="运行前检查"></a>

### 1. 基础环境核验
在执行大规模分析前，请确保：
* 软件版本确认：执行 `dnbc4tools --version`，确认为当前最新版本（如 `3.2`）；
* 依赖工具完备：确保原生环境依赖（如 STAR、SAMtools、MACS2 等）在系统 `$PATH` 中可用；
* 输入数据完整性：FASTQ 文件成对匹配、未发生意外损坏或截断（建议校验 MD5 值）；
* 参考基因组正确性：确认使用的物种参考基因组（FASTA、GTF、STAR 索引）与实验物种及建库化学版本匹配。

### 2. 预检快照与运行锁
流程启动初期会在内存与磁盘执行严格的预检（Preflight）：
* **环境预检快照 (`logs/preflight.json`)**：记录流程解析出的执行线程数（`Threads`）、运行步骤（`Steps`）、参考基因组路径（`Reference`）、建库试剂体系（`Chemistry`）以及系统内存预算（`resource_budget`，包含当前可用物理内存与配置的内存上限）；
* **独占运行锁 (`logs/run.lock`)**：流程运行期间会在输出日志目录下创建 `run.lock` 文件锁，防止针对同一输出目录的并发重复调用。若作业被非正常外部信号中断（如 `kill -9`），需在确认原作业彻底结束后再进行清理或重试。

!!! tip "脚本批量生成与执行说明"
    - `dnbc4tools rna multi` 与 `atac multi` 命令仅负责根据输入列表在当前目录生成 `.sh` 批处理脚本，**本身不创建分析日志目录**；
    - 真正执行生成的 `.sh` 脚本（或直接调用 `multi run`）时，流程才会初始化输出目录、创建 `logs/` 结构并记录各分析阶段的详细日志。
    - 批量样本列表推荐使用纯文本制表符（TAB）分列，分号 `;` 分隔双端测序 R1 与 R2，逗号 `,` 分隔同端多 Lane 文件。

---

## 日志系统与 logs 目录结构 <a id="日志系统说明"></a>

每次分析启动后，所有控制台输出、子进程外部命令调用、性能监控、结构化异常以及阶段完成状态均统一归档在 `<outdir>/<name>/logs/` 目录下。

### logs 目录结构总览

```text
<outdir>/<name>/logs/
├── YYYYMMDD.txt                          # 主执行日志文件 (按日期命名，记录全阶段详细输出)
├── run_manifest.json                     # 运行清单审计日志 (记录各阶段状态、耗时与终止错误)
├── preflight.json                        # 启动预检快照 (记录运行环境、参数与资源预算)
├── errors.jsonl                          # 结构化错误追踪日志 (JSON Lines 格式，机器可读)
├── run.lock                              # 运行独占文件锁 (防止同一目录多作业并发写冲突)
├── report_model.snapshot.json            # 交互式网页报告完整数据模型快照
├── runs/                                 # 历史运行审计归档目录
│   └── <run_id>/                         # 单次调用的独立快照
│       ├── run.json                      # 该次调用的参数与状态备份
│       └── preflight.json                # 该次调用的预检配置备份
├── stage_manifests/                      # 阶段执行清单与指纹校验 (断点续跑关键记录)
│   └── <pipeline>.<stage>.json
├── stage_completion/                     # 阶段成功完成轻量级指针标记
│   └── <pipeline>.<stage>.json
└── <sample>_upload.info                  # 分析日志与诊断压缩归档包 (供提供给 MGI 用于排查问题)
```

---

### 核心日志文件详解

#### 1. 主日期执行日志 (`logs/YYYYMMDD.txt`)
* **定位**：流程运行的核心主日志，根据当前日期动态命名（如 `logs/20261106.txt`）。
* **格式规范**：采用统一标准时间戳格式：
  ```text
  %(asctime)s - %(name)s - %(levelname)s - %(message)s
  ```
* **记录内容**：
  * 每个生信分析阶段（如 `data/QC`、`alignment`、`count`、`similarity`、`analysis`、`report` 等）的启动、传参、实时进展与完成状态；
  * 底层核心算法及外部工具（如 STAR 比对、SAMtools 排序、MACS2 寻峰）调用的确切命令行、工作路径及执行输出流；
  * 各阶段处理的细胞数、特征数、数据矩阵维度等生信统计值；
  * **资源消耗与耗时分析**：每个阶段完成时均会记录运行耗时（秒）。若开启了环境变量 `export DNBC4TOOLS_PROFILE_RESOURCES=1`，主日志中还会输出详细的 CPU 耗时与内存峰值统计（如 `process CPU user=142.50s, system=18.20s; process lifetime peak RSS=12.45 GiB`）。

#### 2. 结构化错误追踪日志 (`logs/errors.jsonl`)
* **定位**：机器可读的结构化异常追踪日志，采用 JSON Lines 格式（一行一个独立 JSON 对象），是故障定位的最核心证据。
* **数据字段结构**：
  ```json
  {
    "timestamp": "2026-11-06T13:00:00.123+08:00",
    "error_id": "e4f1a23b9c0d",
    "error_code": "TOOL",
    "run_id": "20261106T130000-12345-a1b2c3d4",
    "sample": "demo_sample",
    "pipeline": "rna",
    "stage": "align",
    "fatal": true,
    "error_type": "ToolExecutionError",
    "message": "STAR alignment failed with exit code 104",
    "traceback": "Traceback (most recent call last):\n  File ...\nToolExecutionError: ...",
    "context": {
      "command": "STAR --genomeDir /ref/STAR_index ...",
      "exit_code": 104,
      "stderr_tail": "EXITING because of FATAL ERROR: could not open genome file ..."
    }
  }
  ```
* **排查价值**：终端报错时通常会输出 `Error ID: <12位字符>`。在 `errors.jsonl` 中检索该 `error_id`，可查看 Python 调用栈、失败的底层 Shell 命令以及标准错误输出尾部（`stderr_tail`）。

#### 3. 运行清单审计日志 (`logs/run_manifest.json`)
* **定位**：当前样本分析执行状态的总清单，提供给自动化生产集群与下游质控流水线读取。
* **记录内容**：
  * 全局运行状态：`status`（`success`、`failed`、`aborted` 等）及布尔值 `success`；
  * 唯一执行标识：`run_id`（格式为 `YYYYMMDDTHHMMSS-<pid>-<hash>`）；
  * 时间与耗时：启动时间 `start_time`、结束时间 `end_time` 以及总执行耗时 `duration_sec`；
  * 终止错误明细：当流程发生异常中断时，记录 `terminal_error` 块（含 `error_id`、`error_type` 与 `message`）；
  * 多组学模态完成状态：分别记录各启用的组学模态（RNA、ATAC、VDJ-T、VDJ-B）的独立执行状态。

#### 4. 阶段清单与断点恢复标记 (`stage_manifests/` & `stage_completion/`)
* **`stage_manifests/<pipeline>.<stage>.json`**：
  * 详细记录每个分析阶段执行时的 `stage_fingerprint`（阶段指纹，绑定了当前执行的软件算法版本与阶段契约）以及 `input_fingerprint`（输入数据与参数的哈希指纹）；
  * 流程在启用 `--resume` 断点续跑时，检查输入、参数、工具版本与输出校验信息；仅在检查通过时复用相应阶段的结果。
* **`stage_completion/<pipeline>.<stage>.json`**：
  * 阶段成功完成的轻量级原子指针，记录该阶段成功产出的输出文件列表 `outputs`、完整性哈希 `output_integrity` 及完成时间戳 `completed_at`。

#### 5. 分析日志压缩归档包 (`logs/<sample>_upload.info`)
* **定位**：流程在生成报告后通过底层工具自动生成的二进制流式压缩归档文件；
* **包含内容**：结构化打包并压缩了该样本的执行日志文件（`YYYYMMDD.txt`）、阶段运行清单、中间质控诊断表及环境上下文；
* **提供给 MGI 排查问题**：当遇到难以排查的生信算法异常、意外报错或需要向华大智造（MGI）技术支持团队寻求协助时，**无需手动翻找和搜集零散日志，直接将该 `<sample>_upload.info` 文件提供给 MGI 技术支持即可**。MGI 工程师可通过配套的诊断分析工具（`c4_diagnose`）读取归档中保存的运行信息与日志，辅助定位问题。

---

## 错误代码分类与排查指南 <a id="错误代码分类"></a>

当流程运行遇到错误退出时，终端与日志中会显示标准的 `Error code` 分类码。下表列出了常见分类码、产生诱因及对应的优先排查方向：

| Error code | 错误类别与常见诱因 | 优先检查与定位路径 |
| :--- | :--- | :--- |
| **`CLI-CONFIG`** | **参数与配置格式错误**<br>• 参数拼写错误、遗漏必需参数<br>• 多组学配置文件分段格式缺失（如缺少 `[libraries]`、`[rna]`、`[samples]` 等） | • 检查命令行语法与参数拼写；<br>• 核对配置文件 CSV 是否符合分段规范（参阅各流程参数说明）。 |
| **`INPUT`** | **输入文件不可用或损坏**<br>• FASTQ 路径不存在、无读取权限<br>• 双端 FASTQ 读段数不匹配或文件意外被截断<br>• 条形码白名单文件缺失或格式不符 | • 检查文件路径拼写与 Linux 文件读写权限；<br>• 检查 FASTQ 文件是否完整（可使用 `gzip -t` 测试压缩包完整性）；<br>• 核查双端 FASTQ 文件的 Read 行数是否完全一致。 |
| **`REFERENCE`** | **参考基因组与注释库异常**<br>• 参考基因组目录路径错误或缺少必需索引<br>• STAR 索引版本与当前 STAR 运行版本不兼容<br>• GTF 注释文件缺少 `gene_id` 或 `transcript_id` 属性 | • 检查参考基因组路径是否存在完整的 FASTA、GTF 及构建好的索引；<br>• 核查物种名配置（如 `Human` / `Mouse`）是否与实际建库体系对应。 |
| **`TOOL`** | **底层外部工具执行失败**<br>• STAR 比对内存溢出（OOM Killed）<br>• MACS2 或 SAMtools 执行抛错或被系统终止<br>• 底层 C/C++ 二进制依赖与当前操作系统动态链接库不匹配 | • 打开 `logs/errors.jsonl` 查看失败命令与 `context.stderr_tail`；<br>• 若提示内存不足，增加可用内存分配或调低线程数；<br>• 检查系统动态库依赖（如 `libz`、`glibc`）。 |
| **`OUTPUT`** | **输出目录与磁盘写入错误**<br>• 输出路径不存在且无创建权限<br>• 磁盘存储空间耗尽（Disk full）<br>• 存储配额（Quota）超限或文件系统只读 | • 执行 `df -h` 检查目标磁盘分区剩余可用空间；<br>• 检查当前用户对 `<outdir>` 是否具有写权限；<br>• 检查是否触发了集群节点或用户目录的 Inode 配额上限。 |
| **`INTERRUPTED`** | **任务被外部意外中断**<br>• 集群调度系统（SLURM/SGE/PBS）因超时或超限发送 SIGKILL / SIGTERM<br>• 人为使用 `Ctrl+C` 或 `kill` 终止作业 | • 检查集群作业管理系统的任务日志（如 `slurm-<jobid>.out`），确认是否发生节点超限强制杀死；<br>• 确认原作业彻底停止后，检查日志确认已完成的检查点，按需重新投递。 |
| **`INTERNAL`** | **未知 Python 运行时异常**<br>• 未被预期捕获的边界情况或代码逻辑异常 | • 记录控制台显示的 12 位 `Error ID`；<br>• 打开 `logs/errors.jsonl` 提取完整的 `traceback` 与环境信息进行深入排查。 |

---

## 典型故障排障步骤示例 <a id="典型故障排障"></a>

### 场景 1：流程报 `TOOL` 错误，终端仅显示命令退出码非零

1. **获取 Error ID**：查看终端最后输出的错误摘要，例如提示 `Error ID: a7f8b91c2d3e (Error code: TOOL)`；
2. **检索错误日志**：在日志目录下检索该 ID：
   ```bash
   grep "a7f8b91c2d3e" <outdir>/<sample>/logs/errors.jsonl
   ```
3. **定位失败原因**：检查 `context.command` 与 `context.stderr_tail`，并在集群作业日志中核对内存超限或 OOM 终止信息；先确认失败发生在比对、矩阵生成还是 BAM 输出阶段，再调整资源设置；
4. **针对性修复**：若确认内存不足，增加作业内存配额，或降低 `--threads` 以减少并发。若不需要 BAM，RNA 命令可添加 `--no_bam`，multi/C6 可在 `[rna]` 中设置 `no_bam,true`。3.2 使用嵌入式 STAR 比对，STAR 不负责生成或排序 BAM；不要使用 `--limitBAMsortRAM`，也不要通过 `--star_parameters` 透传 `--limitBAM*` 调整 BAM 输出，这些参数不适用且会被参数校验拒绝。

### 场景 2：集群任务超时被杀或意外中断后断点续跑

1. **确认旧进程已释放**：确保之前的任务进程已彻底终止，不存在残留后台进程；
2. **检查运行锁**：若旧任务异常终止残留了 `logs/run.lock`，可安全删除该锁文件：
   ```bash
   rm -f <outdir>/<sample>/logs/run.lock
   ```
3. **查阅阶段状态**：查阅 `logs/stage_completion/` 目录，确认哪些阶段已顺利完成；
4. **启动断点续跑**：在原命令中追加 `--resume` 参数重新启动。流程会自动校验输入指纹与已完成阶段的合法性，直接跳过已完成的大计算量阶段（如已完成的比对或矩阵生成），从断点处平滑继续。

---

## 现有产物检查与高级诊断 (`validate-artifacts`) <a id="产物检查与高级诊断"></a>

为协助运维人员与生信工程师在交付或分析后快速验证交付目录的完整性，`dnbc4tools` 提供了内部产物验证诊断工具：

```bash
# 轻量级快速结构校验 (检查必需目录与关键文件是否存在且非空)
dnbc4tools validate-artifacts --sample-dir /path/to/sample --level shallow

# 深度内容与数据一致性扫描 (校验 HDF5 结构、MEX 维度及片段索引，并导出 JSON 诊断结果)
dnbc4tools validate-artifacts --sample-dir /path/to/sample --level deep --json /path/to/sample/logs/artifact-validation.json
```

* `--level shallow`：执行轻量检查，适合快速排查是否遗漏了核心交付文件；
* `--level deep`：校验 H5/H5AD 内部数据组、MEX 矩阵行数与特征数一致性以及 BAM 索引，并将诊断详情记录至 JSON 文件；
* 注意：该命令用于自动化工程结构验证，不能替代真实的生物学实验质量评估。
