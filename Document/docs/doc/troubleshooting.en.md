# Running & Troubleshooting

This guide provides comprehensive information on execution workflows, log auditing, troubleshooting diagnostics, and checkpoint recovery for the DNBelab C Series™ single-cell analysis software (`dnbc4tools`).

---

## Pre-Run Verification & Preflight Checks <a id="pre-run-verification"></a>

### 1. Basic Environment Verification
Before launching large-scale production analyses, verify the following prerequisites:
* **Software Version**: Confirm your installation by running `dnbc4tools --version` (ensuring it matches `3.2` or higher);
* **Tool Dependencies**: Ensure that native system dependencies (such as STAR, SAMtools, MACS2, etc.) are available in the system `$PATH`;
* **Input Integrity**: Paired-end FASTQ files must be intact, uncorrupted, and properly paired (MD5 checksum validation is recommended);
* **Reference Compatibility**: Ensure reference files (FASTA, GTF, and aligner indexes) match the experimental organism and library chemistry version.

### 2. Preflight Snapshot & Run Locking
At startup, the pipeline executes strict preflight checks before any heavy computation:
* **Preflight Snapshot (`logs/preflight.json`)**: Records resolved execution parameters including thread count (`Threads`), requested execution steps (`Steps`), reference genome directory (`Reference`), library chemistry protocol (`Chemistry`), and the memory budget (`resource_budget`, detailing available system RAM and configured ceilings);
* **Exclusive Run Lock (`logs/run.lock`)**: An exclusive filesystem lock file is established under the log directory during execution to prevent concurrent write collisions on the same output directory. If a run is terminated abnormally by external signals (e.g. `kill -9`), confirm the previous process is dead before removing the lock or retrying.

!!! tip "Batch Script Generation vs. Execution"
    - Commands such as `dnbc4tools rna multi` and `atac multi` only generate `.sh` batch shell scripts in the working directory; **they do not create analysis logs by themselves**;
    - Executing the generated `.sh` scripts (or invoking `multi run` directly) initializes the full output hierarchy, creates the `logs/` directory, and records comprehensive step logs.
    - Batch sample lists should use plain-text TAB delimiters, with semicolons `;` separating R1/R2 pairs, and commas `,` separating multiple lane files of the same read.

---

## Logging System & logs Directory Structure <a id="logging-system"></a>

Once a pipeline run starts, all terminal logs, subprocess command invocations, performance metrics, structured errors, and stage completion markers are stored under `<outdir>/<name>/logs/`.

### Directory Overview

```text
<outdir>/<name>/logs/
├── YYYYMMDD.txt                          # Main daily execution log (chronological record of all stages)
├── run_manifest.json                     # Run audit manifest (records stage statuses, durations, and errors)
├── preflight.json                        # Startup preflight snapshot (records runtime environment and budgets)
├── errors.jsonl                          # Structured error tracking records (JSON Lines format)
├── run.lock                              # Exclusive process file lock (prevents concurrent write conflicts)
├── report_model.snapshot.json            # Complete web report data model snapshot
├── runs/                                 # Historical invocation audit directory
│   └── <run_id>/                         # Independent snapshots per invocation
│       ├── run.json                      # Parameter and status backup for this invocation
│       └── preflight.json                # Preflight configuration backup for this invocation
├── stage_manifests/                      # Stage execution manifests & fingerprints (checkpoint resume validation)
│   └── <pipeline>.<stage>.json
├── stage_completion/                     # Lightweight stage completion pointers
│   └── <pipeline>.<stage>.json
└── <sample>_upload.info                  # Compressed log & diagnostic archive (can be provided to MGI support for troubleshooting)
```

---

### Core Log Files Detailed

#### 1. Main Daily Execution Log (`logs/YYYYMMDD.txt`)
* **Role**: The primary chronological log for pipeline execution, dynamically named by current date (e.g., `logs/20261106.txt`).
* **Standard Format**: Follows the canonical format:
  ```text
  %(asctime)s - %(name)s - %(levelname)s - %(message)s
  ```
* **Recorded Information**:
  * Initialization, input parameters, progress milestones, and completion status for every bioinformatics stage (`data/QC`, `alignment`, `count`, `similarity`, `analysis`, `report`, etc.);
  * Exact shell invocations, working directories, and standard output streams for underlying algorithms and external tools (STAR, SAMtools, MACS2);
  * Processed biological metrics including cell counts, feature dimensions, and matrix shapes;
  * **Resource Profiling & Timing**: Stage elapsed durations (seconds) are always recorded. When `export DNBC4TOOLS_PROFILE_RESOURCES=1` is set, the main log also outputs detailed CPU and resident memory usage (e.g., `process CPU user=142.50s, system=18.20s; process lifetime peak RSS=12.45 GiB`).

#### 2. Structured Error Tracking Log (`logs/errors.jsonl`)
* **Role**: Machine-readable structured error tracking log in JSON Lines format (one JSON object per line). This is the definitive record for diagnosing pipeline crashes.
* **Schema & Fields**:
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
* **Diagnostic Value**: Terminal crashes print a 12-character `Error ID: <id>`. Searching this ID in `errors.jsonl` immediately surfaces the full Python stack trace, the failed shell command, and captured standard error lines (`stderr_tail`).

#### 3. Run Audit Manifest (`logs/run_manifest.json`)
* **Role**: Top-level audit manifest summarizing execution status for the sample, consumed by cluster automation and downstream workflows.
* **Recorded Information**:
  * Execution status: `status` (`success`, `failed`, `aborted`, etc.) and boolean `success`;
  * Invocation ID: Unique `run_id` (format: `YYYYMMDDTHHMMSS-<pid>-<hash>`);
  * Timestamps and duration: `start_time`, `end_time`, and total runtime `duration_sec`;
  * Terminal error detail: When execution fails, the `terminal_error` dictionary captures `error_id`, `error_type`, and `message`;
  * Modality statuses: Separate completion records for active modalities (RNA, ATAC, VDJ-T, VDJ-B).

#### 4. Stage Checkpoints (`stage_manifests/` & `stage_completion/`)
* **`stage_manifests/<pipeline>.<stage>.json`**:
  * Records detailed execution metadata, including the `stage_fingerprint` (binding the software version and contract schema) and the `input_fingerprint` (hash of inputs and arguments);
  * When running with `--resume`, the pipeline verifies fingerprint consistency. Stage results are reused only when checks of inputs, parameters, tool versions, and output integrity pass.
* **`stage_completion/<pipeline>.<stage>.json`**:
  * Lightweight atomic completion pointer tracking generated output files (`outputs`), integrity hashes (`output_integrity`), and completion timestamps (`completed_at`).

#### 5. Compressed Log & Diagnostic Archive (`logs/<sample>_upload.info`)
* **Role**: A binary streaming compressed archive automatically generated by internal pipeline tools upon web report creation;
* **Included Data**: Securely packages and compresses the sample's execution log (`YYYYMMDD.txt`), stage run manifests, intermediate QC diagnostic tables, and execution context;
* **Submitting to MGI Support for Troubleshooting**: When encountering intricate algorithmic abnormalities, unexpected runtime crashes, or when requesting assistance from MGI technical support, **users do not need to manually gather scattered log files—simply provide the `<sample>_upload.info` file to MGI technical support**. MGI support engineers can read the execution information and logs stored in the archive using diagnostic utilities (`c4_diagnose`) to assist troubleshooting.

---

## Error Classification & Troubleshooting Guide <a id="error-classification"></a>

When a run exits with an error, the terminal and logs report a standardized `Error code`. The table below outlines common error codes, typical root causes, and recommended investigation paths:

| Error code | Category & Common Causes | Investigation & Resolution Paths |
| :--- | :--- | :--- |
| **`CLI-CONFIG`** | **Option or syntax misconfiguration**<br>• Misspelled options or missing required parameters<br>• Missing section headers in multi-omics configs (e.g. missing `[libraries]`, `[rna]`, `[samples]`) | • Inspect CLI syntax and option spellings;<br>• Check that configuration CSVs adhere to required section syntax. |
| **`INPUT`** | **Input files missing, unreadable, or truncated**<br>• FASTQ path does not exist or lacks read permission<br>• Paired FASTQ line counts do not match or file truncated<br>• Barcode whitelist file missing | • Verify file paths and Linux read permissions;<br>• Test archive integrity using `gzip -t <file.fq.gz>`;<br>• Ensure paired R1 and R2 files contain identical numbers of reads. |
| **`REFERENCE`** | **Reference genome or annotation issue**<br>• Genome directory invalid or missing required index files<br>• STAR index version mismatch with installed STAR binary<br>• GTF missing `gene_id` or `transcript_id` attributes | • Verify genome directory contains intact FASTA, GTF, and index files;<br>• Confirm species configuration (e.g. `Human` / `Mouse`) matches the experimental chemistry. |
| **`TOOL`** | **External tool or binary failure**<br>• STAR out of memory (OOM killed)<br>• MACS2 or SAMtools error or terminated by signal<br>• Shared dynamic library incompatibilities (`glibc`, `libz`) | • Open `logs/errors.jsonl` to review the command and `context.stderr_tail`;<br>• Increase RAM allocation or reduce thread counts if out-of-memory occurs;<br>• Verify system shared libraries. |
| **`OUTPUT`** | **Output filesystem or disk errors**<br>• Output directory does not exist and cannot be created<br>• Disk storage capacity exhausted (No space left on device)<br>• Disk quota or inode quota exceeded | • Check available space using `df -h`;<br>• Verify write permissions on `<outdir>`;<br>• Check cluster storage quota or inode limits. |
| **`INTERRUPTED`** | **Process terminated externally**<br>• Cluster schedulers (SLURM/SGE/PBS) sending SIGKILL/SIGTERM due to timeout or memory limits<br>• Manual `Ctrl+C` or `kill` termination | • Inspect cluster job logs (e.g. `slurm-<jobid>.out`) for node eviction or timeout reasons;<br>• Confirm prior processes are terminated, then restart with resume options if desired. |
| **`INTERNAL`** | **Unexpected Python runtime exception**<br>• Unhandled corner case or internal logic exception | • Note the 12-character `Error ID` from the console;<br>• Extract the complete `traceback` from `logs/errors.jsonl` for in-depth resolution. |

---

## Practical Troubleshooting Walkthroughs <a id="troubleshooting-walkthroughs"></a>

### Scenario 1: Non-Zero Exit Code with `TOOL` Error

1. **Locate Error ID**: Check the terminal output for the error footer, e.g., `Error ID: a7f8b91c2d3e (Error code: TOOL)`;
2. **Search Error Record**: Grep the error ID in the log directory:
   ```bash
   grep "a7f8b91c2d3e" <outdir>/<sample>/logs/errors.jsonl
   ```
3. **Identify Root Cause**: Inspect `context.command` and `context.stderr_tail`, and check the cluster job log for memory-limit or OOM-kill messages. Identify whether the failure occurred during alignment, matrix generation, or BAM output before changing resource settings;
4. **Apply Resolution**: For memory exhaustion, increase the job memory allocation or reduce `--threads` to lower concurrency. If BAM output is unnecessary, use `--no_bam` for RNA runs or `no_bam,true` in the `[rna]` section for multi/C6 runs. Version 3.2 uses embedded STAR alignment; STAR does not create or sort BAM files in this mode. Do not use `--limitBAMsortRAM` or pass `--limitBAM*` through `--star_parameters` to tune BAM output; these parameters are not applicable and are rejected by parameter validation.

### Scenario 2: Resuming an Interrupted or Cancelled Run

1. **Ensure Process Cleanup**: Verify that no zombie processes from the previous run are active;
2. **Clear Run Lock**: If an interrupted run left a stale lock file, remove it cleanly:
   ```bash
   rm -f <outdir>/<sample>/logs/run.lock
   ```
3. **Inspect Completed Stages**: Review `logs/stage_completion/` to verify which stages completed successfully;
4. **Execute Resume**: Re-run the original command with the `--resume` flag appended. The runner will validate fingerprints and bypass previously verified stages, picking up directly from the point of interruption.

---

## Artifact Validation & Advanced Diagnostics (`validate-artifacts`) <a id="artifact-validation"></a>

To assist bioinformatics engineers and operations teams in validating deliverable integrity post-analysis, `dnbc4tools` includes an internal artifact validation utility:

```bash
# Lightweight structural check (verifies required directories and files exist and are non-empty)
dnbc4tools validate-artifacts --sample-dir /path/to/sample --level shallow

# Deep content and consistency inspection (verifies HDF5 structures, MEX dimensions, BAM indexes)
dnbc4tools validate-artifacts --sample-dir /path/to/sample --level deep --json /path/to/sample/logs/artifact-validation.json
```

* `--level shallow`: Performs rapid checks, confirming required delivery files are present and non-empty;
* `--level deep`: Scans H5/H5AD datasets, compares matrix row/column dimensions, and verifies BAM index headers, exporting diagnostics to a JSON manifest;
* Note: This command provides structural integrity validation and does not replace biological review of QC metrics.
