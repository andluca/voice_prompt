#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Error: venv not found. Run ./scripts/setup.sh first."
    exit 1
fi
source "$SCRIPT_DIR/venv/bin/activate"
python -m voice_prompt start "$@"
