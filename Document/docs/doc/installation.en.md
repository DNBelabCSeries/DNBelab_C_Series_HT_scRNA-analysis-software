# DNBelab C Series™ Software Installation

This guide describes the system requirements, software download, installation procedure, and verification steps for the DNBelab C Series™ HT Single-Cell Analysis Software (dnbc4tools).

## System Requirements <a id="system-requirements"></a>

dnbc4tools requires the following system and hardware environment:

| Category | Minimum | Recommended | Notes |
| :--- | :--- | :--- | :--- |
| **Operating System** | 64-bit Linux | CentOS 7.x+ / Ubuntu 20.04+ | Compatible with mainstream 64-bit Linux distributions |
| **CPU / Architecture** | 8 cores (x86-64) | 16+ cores | Requires x86-64 compatible processors |
| **Memory (RAM)** | 50 GB | 128 GB or higher | Actual requirements depend on sample count and sequencing depth |
| **Disk Storage** | Adequate data space | Fast NVMe / SSD | For FASTQ inputs, reference genomes, and intermediate analysis files |

---

## Software Download <a id="software-download"></a>

### dnbc4tools 3.2

!!! note "Development documentation — package not yet available"
    Version 3.2 has not been formally released. Its installation package is not yet available for download; the release date, download URL, package name, and checksums await confirmation. The installation paths and commands below are examples to use once the release package is available.

<div style="margin-top: 15px;" markdown="block">
  <strong>Looking for older versions?</strong><br>
  Use the version switcher in the header to view the complete 3.1 manual. For earlier releases, please refer to the <a href="./installation_previous.html">Previous Installation Guide</a>.
</div>

---

## Installation Process <a id="installation-process"></a>

### Step 1: Extract the Package

Extract the dnbc4tools package to your preferred directory (example uses `/opt/software`):

```bash
# Navigate to target directory
cd /opt/software

# Extract the package
tar -xzvf dnbc4tools-3.2.tar.gz
```

### Step 2: Verify Directory Structure

After extraction, the directory structure is organized as follows:

```text
dnbc4tools3.2/
├── dnbc4tools          # Main executable launcher
├── external/           # Bundled third-party dependencies
├── lib/                # Shared runtime libraries
├── misc/               # Configuration and auxiliary resources
└── sourceC4.bash       # Environment configuration script
```

---

## Verification & Testing <a id="verification--testing"></a>

### Basic Functionality Test

Navigate to the extracted directory and run the main executable to confirm successful installation:

```bash
# Navigate to installation directory
cd /opt/software/dnbc4tools3.2

# Test command
./dnbc4tools
```

The installation is successful when the following version and help message is displayed:

```text
dnbc4tools 3.2

Single-cell analysis toolkit for RNA, ATAC, V(D)J, and multi-omics workflows

Usage: dnbc4tools <COMMAND>

Commands:
  
    rna          Single-cell RNA-seq analysis
    atac         Single-cell ATAC-seq analysis
    vdj          Single-cell V(D)J immune profiling
    tools        Utility commands and file processing
    multi        Integrated multi-omics analysis

Options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

After verifying the installation, you can proceed to the [Quick Start](quickstart.md) tutorial to run your first single-cell analysis.
