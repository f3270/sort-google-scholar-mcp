#!/usr/bin/env bash
set -euo pipefail

py_files() {
  python - <<'PY'
import os
import subprocess
import sys

paths = subprocess.check_output(["git", "ls-files", "-z", "*.py"]).split(b"\0")
existing = [p for p in paths if p and os.path.exists(p.decode("utf-8"))]
sys.stdout.buffer.write(b"\0".join(existing))
PY
}

py_files | xargs -0 -r uvx isort
py_files | xargs -0 -r uvx black

echo "✔ Formatting complete (isort → black)"
