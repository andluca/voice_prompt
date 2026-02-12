#!/usr/bin/env bash
# Launch Voice-to-Claude in background (no terminal needed)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
nohup python -m voice_prompt start > /dev/null 2>&1 &
echo "Voice Prompt started (PID: $!)"
