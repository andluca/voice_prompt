#!/usr/bin/env bash
# Linux/macOS setup script for Voice-to-Claude
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_DIR/venv"

echo "=== Voice-to-Claude Setup ==="

# 1. Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment…"
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 2. Install dependencies
echo "Installing dependencies…"
pip install --upgrade pip
pip install -r "$REPO_DIR/requirements.txt"

# 3. Create config directory
CONFIG_DIR="$HOME/.voice-to-claude"
mkdir -p "$CONFIG_DIR"
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    cp "$REPO_DIR/config.yaml.example" "$CONFIG_DIR/config.yaml"
    echo "Config copied to $CONFIG_DIR/config.yaml"
fi

# 4. Optionally download the model
echo ""
read -rp "Download Whisper large-v3 model now? (~3 GB) [y/N] " dl
if [[ "$dl" =~ ^[Yy]$ ]]; then
    python "$REPO_DIR/scripts/download-model.py"
fi

echo ""
echo "Setup complete!"
echo "  Activate venv:  source $VENV_DIR/bin/activate"
echo "  Run:            python -m voice_prompt"
echo "  Quick test:     python -m voice_prompt test"
