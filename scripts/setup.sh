#!/usr/bin/env bash
# Linux/macOS setup script for Voice-to-Claude
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_DIR/venv"

echo "=== Voice-to-Claude Setup ==="

# 1. Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 2. Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$REPO_DIR/requirements.txt"
pip install -e "$REPO_DIR"

# 3. Create config directory
CONFIG_DIR="$HOME/.voice-to-claude"
mkdir -p "$CONFIG_DIR"
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    cp "$REPO_DIR/config.yaml.example" "$CONFIG_DIR/config.yaml"
    echo "Config copied to $CONFIG_DIR/config.yaml"
fi

# 4. Make launcher scripts executable
chmod +x "$REPO_DIR/voice-prompt.sh"
chmod +x "$REPO_DIR/voice-prompt-bg.sh"

# 5. Optionally download the model
echo ""
read -rp "Download Whisper model now? (~500 MB for small) [y/N] " dl
if [[ "$dl" =~ ^[Yy]$ ]]; then
    python -m voice_prompt download-model
fi

# 6. Optionally install desktop entry for autostart
echo ""
read -rp "Add to desktop applications and autostart? [y/N] " desktop
if [[ "$desktop" =~ ^[Yy]$ ]]; then
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/voice-prompt.desktop" << DESKTOP
[Desktop Entry]
Name=Voice Prompt
Comment=Voice-to-text for Claude Code
Exec=$REPO_DIR/voice-prompt-bg.sh
Terminal=false
Type=Application
Categories=Utility;Audio;
DESKTOP
    echo "Desktop entry created"

    mkdir -p "$HOME/.config/autostart"
    cp "$HOME/.local/share/applications/voice-prompt.desktop" "$HOME/.config/autostart/"
    echo "Added to autostart"
fi

echo ""
echo "Setup complete!"
echo "  Run (foreground): $REPO_DIR/voice-prompt.sh"
echo "  Run (background): $REPO_DIR/voice-prompt-bg.sh"
echo "  Hotkey: Ctrl+Shift+Q (default)"
