# Voice-to-Claude

Voice-to-text for hands-free coding with [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Press a hotkey, speak, and your words appear wherever your cursor is — terminal, editor, browser, anywhere.

All transcription runs locally via [faster-whisper](https://github.com/SYSTRAN/faster-whisper). No API calls, no cloud, no cost.

## How It Works

```
Press hotkey -> Record audio -> Transcribe locally -> Type into active window
```

1. Press **Ctrl+Shift+Q** (configurable).
2. Speak your prompt.
3. Stop talking — recording ends automatically after 2 seconds of silence.
4. Text appears where your cursor is.

The Whisper model stays loaded in memory after the first transcription, so subsequent prompts take only a few seconds.

## Installation

### Linux

```bash
git clone https://github.com/yourusername/voice-to-claude.git
cd voice-to-claude
./scripts/setup.sh
```

### Windows

```powershell
git clone https://github.com/yourusername/voice-to-claude.git
cd voice-to-claude
.\scripts\setup.ps1
```

Both scripts create a virtual environment, install dependencies, copy the default config, and optionally download the Whisper model (~460 MB for the default `small` model).

## Usage

```bash
# Start the service (foreground)
python -m voice_prompt start

# Quick test — records 5 seconds, transcribes, prints result
python -m voice_prompt test

# Pre-download the model without starting the service
python -m voice_prompt download-model
```

On Linux you can also use the launcher scripts:

```bash
./voice-prompt.sh          # foreground
./voice-prompt-bg.sh       # background (nohup)
```

### Running in the Background on Windows

Use `pythonw.exe` to run without a console window:

```powershell
.\venv\Scripts\pythonw.exe -m voice_prompt start
```

You can create a desktop shortcut pointing to that command for one-click startup.

## Configuration

Configuration lives at `~/.voice-to-claude/config.yaml`. A copy of `config.yaml.example` is placed there during setup. All settings have sensible defaults — the config file is optional.

### Common Options

```yaml
hotkeys:
  record: "ctrl+shift+q"   # Change to any key combo
  cancel: "escape"

audio:
  silence_duration: 2.0     # Seconds of silence to auto-stop
  grace_period: 10.0        # Wait this long for first speech before giving up

transcription:
  model: "small"            # tiny | base | small | medium | large-v3
  language: "en"            # Language code, or "" for auto-detect
  beam_size: 1              # Higher = more accurate, slower
  num_threads: 0            # 0 = auto

output:
  mode: "type"              # "type" into active window, or "clipboard"
```

See [config.yaml.example](config.yaml.example) for all options with descriptions.

### Model Comparison

| Model    | Size  | Speed   | Accuracy | Notes                      |
|----------|-------|---------|----------|----------------------------|
| tiny     | 75 MB | Fastest | ~85%     | Simple commands             |
| base     | 140 MB| Fast    | ~90%     | General use                 |
| small    | 460 MB| Medium  | ~95%     | Good for technical speech   |
| medium   | 1.5 GB| Slower  | ~97%     | High accuracy               |
| large-v3 | 3 GB  | Slowest | ~98%     | Best for technical vocabulary|

**Default: `small`** — good balance of speed and accuracy for coding prompts. Use `large-v3` if you need the highest accuracy for technical vocabulary and have the disk space / RAM.

## Requirements

- Python 3.9+
- ~460 MB disk for the default `small` model (~1 GB RAM when running)
- A microphone
- Linux or Windows 10/11

### Linux Audio Dependencies

```bash
# Arch
sudo pacman -S portaudio

# Ubuntu / Debian
sudo apt install portaudio19-dev
```

## Architecture

```
voice_prompt/
  config.py       Config loading with deep-merge defaults
  recorder.py     Microphone capture with silence detection
  transcriber.py  Whisper inference (lazy model loading, auto GPU/CPU)
  outputter.py    Keyboard simulation via pynput
  hotkey.py       Global hotkey listener via pynput GlobalHotKeys
  main.py         CLI, wiring, single-instance lock
```

## Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check voice_prompt/

# Format
black voice_prompt/
```

## Troubleshooting

**Hotkey not working** — Another application may be using the same key combo. Change it in `config.yaml`. On Windows, note that `Ctrl+Alt` is equivalent to `AltGr` on some keyboard layouts (e.g., ABNT Brazilian), which can cause conflicts.

**No microphone detected** — Run `python -c "import sounddevice as sd; print(sd.query_devices())"` to check available devices. On Windows, verify mic permissions in system settings.

**Slow transcription** — If you have an NVIDIA GPU, install PyTorch with CUDA support and set `device: "cuda"` in config. Otherwise, try a smaller model like `base` or `small`.

**Model download fails** — Run `python -m voice_prompt download-model` directly. You can also set a custom cache directory via `system.model_cache_dir` in the config or the `VOICE_PROMPT_MODEL_DIR` environment variable.

## License

MIT

## Acknowledgments

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — CTranslate2-based Whisper inference
- [OpenAI Whisper](https://github.com/openai/whisper) — The underlying speech recognition model
- [pynput](https://github.com/moses-palmer/pynput) — Cross-platform keyboard control
