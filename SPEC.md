# Voice-to-Claude Specification

## Overview

A cross-platform voice-to-text tool that enables hands-free prompting for Claude Code and any other text input. Uses local Whisper large-v3 model for high-accuracy transcription of technical speech without API costs.

## Core Requirements

### Functional Requirements

1. **Voice Recording**
   - Activate recording via configurable hotkey (default: Ctrl+Shift+V)
   - Visual/audio feedback when recording starts
   - Support two modes:
     - Hold-to-record (press and hold)
     - Toggle mode (press to start, press again to stop)
   - Cancel recording with Escape key
   - Automatic silence detection (optional, configurable timeout)

2. **Transcription**
   - Use faster-whisper with large-v3 model
   - Local processing (no API calls, no internet required)
   - Support both CPU and GPU (auto-detect, fallback to CPU)
   - Model auto-download on first run (~3GB)
   - Optimize for technical vocabulary (code, frameworks, APIs)

3. **Text Output**
   - Type transcribed text into currently focused application
   - Character-by-character typing simulation (looks natural)
   - Configurable typing speed (default: instant, option for realistic)
   - Optional clipboard copy mode (instead of typing)
   - Preserve formatting (newlines if detected in speech)

4. **Cross-Platform Support**
   - Linux (primary - Arch-based Omarchy)
   - Windows (secondary)
   - Same codebase, platform-specific audio backends handled automatically
   - Installation scripts for both platforms

### Non-Functional Requirements

1. **Performance**
   - Transcription completes in <10 seconds for typical prompts (30-60s audio)
   - Low memory footprint when idle (<100MB)
   - Efficient model loading (load once, keep in memory)

2. **Reliability**
   - Graceful error handling (mic not found, model load failure)
   - Log errors to file for debugging
   - Recover from transcription failures without crashing

3. **Usability**
   - Simple installation (one command)
   - Clear feedback during recording and processing
   - Configurable via YAML file
   - Detailed README with troubleshooting

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────┐
│                  Voice Prompt Tool                   │
├─────────────────────────────────────────────────────┤
│  Hotkey Listener  →  Audio Recorder  →  Transcriber │
│         ↓                                      ↓     │
│  Config Manager              Text Output Handler    │
└─────────────────────────────────────────────────────┘
```

### Core Components

1. **Hotkey Listener** (`HotkeyManager`)
   - Register global hotkey combinations
   - Platform-agnostic key handling
   - Non-blocking keyboard monitoring
   - Support multiple hotkeys (record, cancel, config reload)

2. **Audio Recorder** (`AudioRecorder`)
   - Capture audio from default microphone
   - Support hold-to-record and toggle modes
   - Visual/audio feedback (beep or notification)
   - Silence detection for auto-stop
   - WAV format output (temp file)

3. **Transcriber** (`WhisperTranscriber`)
   - Load and cache large-v3 model
   - Transcribe audio to text
   - Handle model download on first run
   - GPU acceleration when available
   - Error handling and retry logic

4. **Text Output Handler** (`TextOutputter`)
   - Simulate keyboard typing into active window
   - Alternative clipboard mode
   - Configurable typing speed
   - Special character handling

5. **Config Manager** (`ConfigManager`)
   - Load YAML configuration
   - Provide defaults for missing values
   - Hot-reload on file change
   - Validate configuration schema

### Data Flow

```
1. User presses Ctrl+Shift+V
   ↓
2. HotkeyManager triggers recording
   ↓
3. AudioRecorder captures audio to temp file
   ↓
4. WhisperTranscriber processes audio
   ↓
5. TextOutputter types result into active window
   ↓
6. Cleanup temp audio file
```

## Technical Stack

### Core Dependencies

- **faster-whisper** - Whisper model inference (4x faster than openai-whisper)
- **sounddevice** - Cross-platform audio recording
- **pynput** - Global hotkey monitoring and keyboard simulation
- **pyaudio** - Alternative audio backend (fallback)
- **PyYAML** - Configuration file parsing
- **rich** - Terminal UI for status/errors (optional)

### Python Version

- Minimum: Python 3.9
- Recommended: Python 3.11+ (faster)

## Configuration

### config.yaml Structure

```yaml
# Hotkey configuration
hotkeys:
  record: "ctrl+shift+v"        # Start/stop recording
  cancel: "escape"               # Cancel current recording
  mode: "toggle"                 # "toggle" or "hold"

# Audio settings
audio:
  sample_rate: 16000             # Whisper expects 16kHz
  channels: 1                    # Mono
  silence_threshold: 0.01        # Auto-stop threshold (0-1)
  silence_duration: 2.0          # Seconds of silence before auto-stop
  max_recording_duration: 120    # Max seconds per recording

# Transcription settings
transcription:
  model: "large-v3"              # Whisper model size
  device: "auto"                 # "auto", "cpu", "cuda"
  compute_type: "int8"           # "int8", "float16", "float32"
  language: "en"                 # Language hint for better accuracy
  initial_prompt: ""             # Context hint (optional)

# Output settings
output:
  mode: "type"                   # "type" or "clipboard"
  typing_speed: "instant"        # "instant" or delay in ms
  add_newline: false             # Add newline after text

# System settings
system:
  log_level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  log_file: "~/.voice-to-claude/voice-prompt.log"
  model_cache_dir: "~/.cache/whisper"
```

### Environment Variables (Optional)

- `VOICE_PROMPT_CONFIG` - Custom config file path
- `VOICE_PROMPT_MODEL_DIR` - Override model cache directory

## File Structure

```
voice-to-claude/
├── voice_prompt/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── hotkey.py               # HotkeyManager
│   ├── recorder.py             # AudioRecorder
│   ├── transcriber.py          # WhisperTranscriber
│   ├── outputter.py            # TextOutputter
│   └── config.py               # ConfigManager
├── tests/
│   ├── test_recorder.py
│   ├── test_transcriber.py
│   └── test_integration.py
├── scripts/
│   ├── setup.sh                # Linux installation
│   ├── setup.ps1               # Windows installation
│   ├── install-service.sh      # Systemd service (Linux)
│   └── download-model.py       # Pre-download model
├── config.yaml.example         # Example configuration
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Package metadata
├── README.md                   # User documentation
├── CONTRIBUTING.md             # Developer guide
└── LICENSE                     # MIT License
```

## Installation & Usage

### Installation (Linux)

```bash
git clone https://github.com/yourusername/voice-to-claude
cd voice-to-claude
./scripts/setup.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Download Whisper model (~3GB)
4. Copy config.yaml.example to ~/.voice-to-claude/config.yaml
5. Optionally install as systemd service

### Installation (Windows)

```powershell
git clone https://github.com/yourusername/voice-to-claude
cd voice-to-claude
.\scripts\setup.ps1
```

### Usage

```bash
# Start the service (runs in background)
voice-prompt start

# Stop the service
voice-prompt stop

# Test transcription
voice-prompt test

# Check status
voice-prompt status

# View logs
voice-prompt logs
```

Or run directly:
```bash
python -m voice_prompt
```

## User Workflows

### Workflow 1: Claude Code Terminal

```
1. Open terminal with Claude Code running
2. Position cursor at prompt
3. Press Ctrl+Shift+V
4. Speak: "Add error handling to the Harbor parser for missing task files"
5. Release key (or press again to stop)
6. Wait 3-5 seconds for transcription
7. Text appears in terminal
8. Press Enter to submit to Claude Code
```

### Workflow 2: VS Code Claude Code Chat

```
1. Open VS Code with Claude Code extension
2. Click into chat input box
3. Press Ctrl+Shift+V
4. Speak your prompt
5. Text appears in chat box
6. Press Enter to send
```

### Workflow 3: Quick Clipboard Mode

```
1. Press Ctrl+Shift+V anywhere
2. Speak your text
3. Text copied to clipboard (no typing)
4. Paste wherever needed (Ctrl+V)
```

## Error Handling

### Common Errors & Recovery

1. **Microphone not found**
   - Fallback to default system mic
   - Show error message with instructions
   - Don't crash, continue listening for hotkey

2. **Model download fails**
   - Retry with exponential backoff
   - Provide manual download instructions
   - Cache partial downloads

3. **Transcription fails**
   - Log error details
   - Show notification to user
   - Don't lose recorded audio (optional: save to file)

4. **Typing simulation fails**
   - Fallback to clipboard mode
   - Log which window/app failed
   - Notify user of fallback

## Performance Optimization

### Model Loading Strategy

```python
# Load model once at startup, keep in memory
# Don't reload for each transcription

class WhisperTranscriber:
    def __init__(self):
        self.model = None
    
    def load_model(self):
        if self.model is None:
            self.model = WhisperModel("large-v3", ...)
    
    def transcribe(self, audio_path):
        self.load_model()  # No-op if already loaded
        return self.model.transcribe(audio_path)
```

### Memory Management

- Model stays in memory (required for performance)
- Clean up temp audio files immediately after transcription
- Limit log file size (rotate when >10MB)

### GPU Acceleration

```python
# Auto-detect GPU, fallback to CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
```

## Testing Strategy

### Unit Tests

- Test each component independently
- Mock external dependencies (mic, keyboard)
- Test config loading and validation

### Integration Tests

- Test full workflow with recorded audio samples
- Test cross-platform compatibility
- Test error recovery scenarios

### Manual Testing

- Test with various accents and speech patterns
- Test technical vocabulary (Harbor, Stagehand, Claude Code)
- Test in different applications (terminal, VS Code, browser)
- Test on both Linux and Windows

## Security & Privacy

### Privacy Considerations

1. **All processing is local** - no data sent to external services
2. **Temp audio files** - deleted immediately after transcription
3. **No logging of transcribed text** - only errors logged
4. **Optional: Disable logging** - set log_level to ERROR or disable

### Security Considerations

1. **Global hotkey** - only captures keyboard when hotkey pressed
2. **No network access required** - after model download
3. **Model integrity** - verify checksum after download
4. **Permission requests** - explicit mic access request on first run

## Future Enhancements

### Phase 2 Features

1. **Multi-language support** - detect language automatically
2. **Voice commands** - special commands like "newline", "delete last"
3. **Custom vocabulary** - train on user-specific technical terms
4. **Punctuation control** - "period", "comma", "new paragraph"
5. **History** - save recent transcriptions for re-use

### Phase 3 Features

1. **GUI** - system tray icon with controls
2. **Profiles** - different configs for different contexts
3. **Macros** - combine voice + text templates
4. **Integration** - plugins for popular IDEs

## Success Metrics

1. **Accuracy** - >95% for technical speech
2. **Speed** - <10s transcription for 60s audio
3. **Reliability** - <1% crash rate over 1000 uses
4. **Adoption** - Used in daily workflow by André

## Open Questions

1. Should we support wake word activation ("Hey Claude")?
2. Should we add speaker diarization (multiple speakers)?
3. Should we integrate with Claude API for post-processing?
4. Should we support real-time streaming transcription?

## Acceptance Criteria

- [ ] Works on both Linux (Omarchy) and Windows
- [ ] Transcribes technical speech with >95% accuracy
- [ ] Completes transcription in <10 seconds for typical prompts
- [ ] Types output into any focused application
- [ ] Configurable via YAML file
- [ ] Runs as background service
- [ ] Includes installation scripts for both platforms
- [ ] Comprehensive README with troubleshooting
- [ ] All temp files cleaned up after use
- [ ] Error handling prevents crashes
