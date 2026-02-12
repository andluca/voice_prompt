#!/usr/bin/env bash
# Launch Voice-to-Claude (foreground, with logs)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
python -m voice_prompt start "$@"
