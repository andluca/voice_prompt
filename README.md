# Voice-to-Claude

**Voice-to-text tool for hands-free Claude Code prompting using local Whisper**

Turn your voice into text instantly with near-perfect accuracy for technical speech. No API costs, 100% local processing.

## ✨ Features

- 🎤 **Voice-activated recording** - Press a hotkey, speak, get text
- 🧠 **High accuracy** - Whisper large-v3 model optimized for technical vocabulary
- 🔒 **Completely private** - All processing happens locally, no cloud required
- ⚡ **Fast transcription** - ~5 seconds for typical prompts
- 🖥️ **Cross-platform** - Works on Linux and Windows
- 🎯 **Works everywhere** - Terminal, VS Code, browsers, any text input
- 💰 **Zero cost** - No API credits, no subscriptions

## 🚀 Quick Start

### Linux

```bash
git clone https://github.com/yourusername/voice-to-claude
cd voice-to-claude
./scripts/setup.sh
voice-prompt start
```

### Windows

```powershell
git clone https://github.com/yourusername/voice-to-claude
cd voice-to-claude
.\scripts\setup.ps1
voice-prompt start
```

## 📖 Usage

1. **Start the service** (runs in background):
   ```bash
   voice-prompt start
   ```

2. **Position your cursor** in any text input (terminal, VS Code, browser)

3. **Press `Ctrl+Shift+V`** and speak your prompt

4. **Wait 3-5 seconds** for transcription to complete

5. **Text appears** where your cursor is

6. **Press Enter** to submit (or continue editing)

### Example: Claude Code Terminal

```bash
# Open Claude Code in terminal
claude-code

# Press Ctrl+Shift+V and speak:
# "Add error handling to the Harbor parser for missing task files"

# Text appears in terminal:
> Add error handling to the Harbor parser for missing task files

# Press Enter to submit to Claude Code
```

### Example: VS Code

```
1. Open VS Code with Claude Code extension
2. Click into chat input box
3. Press Ctrl+Shift+V
4. Speak: "Create a function that extracts behaviors from PRD markdown"
5. Text appears in chat box
6. Press Enter to send
```

## ⚙️ Configuration

Configuration file: `~/.voice-to-claude/config.yaml`

### Change Hotkey

```yaml
hotkeys:
  record: "ctrl+alt+v"  # Change to your preferred combination
```

### Adjust Accuracy vs Speed

```yaml
transcription:
  model: "large-v3"     # Best accuracy (default)
  # model: "medium"     # Faster, slightly less accurate
  # model: "base"       # Fastest, good for simple speech
```

### Output Mode

```yaml
output:
  mode: "type"          # Type into active window (default)
  # mode: "clipboard"   # Copy to clipboard instead
```

See [config.yaml.example](config.yaml.example) for all options.

## 📊 Model Comparison

| Model    | Size  | Speed | Accuracy | Best For                |
|----------|-------|-------|----------|-------------------------|
| tiny     | 75MB  | ⚡⚡⚡  | 85%      | Simple commands         |
| base     | 140MB | ⚡⚡   | 90%      | General use             |
| small    | 460MB | ⚡    | 95%      | Technical speech        |
| large-v3 | 3GB   | ⚡    | 98%      | Perfect technical terms |

**Recommended**: large-v3 (default) - Worth the disk space for near-perfect accuracy with technical vocabulary like "Harbor", "Stagehand", "epic-webdev-bench", etc.

## 🔧 Requirements

- **Python**: 3.9 or higher
- **Disk Space**: ~3GB for large-v3 model
- **RAM**: ~4GB when running
- **OS**: Linux (any distro) or Windows 10/11
- **Microphone**: Any USB or built-in mic

## 🐛 Troubleshooting

### "No microphone detected"

**Linux:**
```bash
# Check available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Install audio libraries if needed
sudo pacman -S portaudio  # Arch
sudo apt install portaudio19-dev  # Ubuntu/Debian
```

**Windows:**
- Check microphone permissions in Windows Settings
- Ensure microphone is set as default device

### "Model download failed"

```bash
# Download manually
python scripts/download-model.py

# Or specify custom cache directory in config.yaml
system:
  model_cache_dir: "/path/to/models"
```

### "Hotkey not working"

- Check if another application is using the same hotkey
- Try a different combination in `config.yaml`
- On Linux, ensure you have permission for global hotkeys

### "Transcription is slow"

```bash
# Check if GPU is being used (if available)
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# If no GPU, switch to smaller model for speed
# Edit config.yaml:
transcription:
  model: "base"  # Much faster on CPU
```

## 🔍 How It Works

```mermaid
graph LR
    A[Press Hotkey] --> B[Record Audio]
    B --> C[Save to Temp File]
    C --> D[Transcribe with Whisper]
    D --> E[Type into Active Window]
    E --> F[Cleanup Temp File]
```

1. **Global hotkey listener** detects `Ctrl+Shift+V`
2. **Audio recorder** captures from microphone
3. **Whisper model** transcribes audio to text
4. **Keyboard simulator** types text into active window
5. **Cleanup** removes temporary files

All processing happens locally on your machine. No internet required (after initial model download).

## 🛠️ Development

### Running from Source

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run directly
python -m voice_prompt
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Quality

```bash
# Format code
black voice_prompt/

# Lint
ruff check voice_prompt/

# Type checking
mypy voice_prompt/
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Optimized inference
- Built for seamless [Claude Code](https://claude.ai/code) workflows

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/voice-to-claude/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/voice-to-claude/discussions)

---

**Made with ❤️ for agentic coding workflows**
