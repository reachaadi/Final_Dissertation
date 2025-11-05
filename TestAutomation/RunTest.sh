#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
venv_python="$script_dir/.venv/bin/python"

if [ ! -x "$venv_python" ]; then
  echo "Error: Python not found at $venv_python" >&2
  exit 1
fi

for script in TestScript.py TestScript2.py TestScript3.py; do
  echo "Running $script..."
  "$venv_python" "$script_dir/$script"
done

echo "All scripts executed."
