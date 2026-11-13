#!/usr/bin/env bash
set -euo pipefail
DOC_ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "${PYTHON_BIN:-python3}" "$DOC_ROOT/build_docs.py" "$@"
