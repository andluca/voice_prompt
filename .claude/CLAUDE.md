# Voice Prompt Project

## Project Overview

Voice-to-text tool for hands-free Claude Code prompting using local Whisper large-v3 model. Enables developers to speak their prompts naturally and have them transcribed with high accuracy for technical vocabulary.

### Key Goals
1. **Reduce friction** in agentic coding workflows by eliminating typing
2. **High accuracy** for technical terms (Harbor, Stagehand, Claude Code, etc.)
3. **Zero cost** - all processing happens locally, no API calls
4. **Cross-platform** - works identically on Linux and Windows
5. **Fast** - transcription completes in <10 seconds for typical prompts

## Architecture

### Component Structure
```
voice_prompt/
├── config.py       → ConfigManager: YAML config with defaults
├── recorder.py     → AudioRecorder: Capture mic audio with sounddevice
├── transcriber.py  → WhisperTranscriber: Local Whisper large-v3 inference
├── outputter.py    → TextOutputter: Type text into active window
├── hotkey.py       → HotkeyManager: Global hotkey listener with pynput
└── main.py         → CLI & integration: Ties everything together
```

### Data Flow
```
User presses Ctrl+Shift+V
  ↓
HotkeyManager triggers recording
  ↓
AudioRecorder captures audio → temp WAV file
  ↓
WhisperTranscriber processes audio → text
  ↓
TextOutputter types into active window
  ↓
Cleanup temp files
```

## Technical Stack

### Core Libraries
- **faster-whisper**: 4x faster than openai-whisper, uses CTranslate2
- **sounddevice**: Cross-platform audio recording (works on Linux & Windows)
- **pynput**: Global hotkeys and keyboard simulation (no admin required)
- **PyYAML**: Configuration management
- **rich**: Terminal UI for status/errors
- **plyer**: Desktop notifications

### Why These Choices
- **faster-whisper over openai-whisper**: Performance, same accuracy
- **pynput over keyboard**: Better cross-platform, no root/admin needed
- **sounddevice over pyaudio**: Simpler setup, no PortAudio compilation
- **large-v3 model**: Best for technical vocabulary, user has 200GB free

## Design Principles

### 1. Lazy Model Loading
Load Whisper model on first use, not at startup. Keep in memory for subsequent uses.
- Startup: Instant
- First transcription: ~10 seconds (model load + transcription)
- Subsequent: ~3-5 seconds (transcription only)

### 2. Clean Component Separation
Each component has single responsibility:
- Config only manages configuration
- Recorder only captures audio
- Transcriber only does transcription
- Outputter only handles text output
- Hotkey only listens for keyboard events

This makes testing easier and code more maintainable.

### 3. Cross-Platform by Default
Use platform-agnostic libraries and pathlib for paths. Test on both Linux and Windows regularly.

### 4. Graceful Error Handling
Never crash on errors. Log, notify user, continue running.
- No microphone? → Show error, keep listening for hotkey
- Transcription fails? → Save audio for debugging, notify user
- Model won't load? → Provide manual download instructions

### 5. Zero Configuration Required
Provide sensible defaults for everything. Config file is optional customization.

## Development Workflow

### Phase-Based Implementation
Follow TODO.md phases:
1. ✅ **Phase 1**: Project setup (complete)
2. 🔨 **Phase 2**: Core components (current)
3. **Phase 3**: Installation scripts
4. **Phase 4**: Testing
5. **Phase 5**: Documentation polish
6. **Phase 6**: Release preparation

### Component Development Order
Build in this order (reduces dependencies):
1. ConfigManager (foundation, no dependencies)
2. AudioRecorder (test independently with sample recording)
3. WhisperTranscriber (test with pre-recorded audio samples)
4. TextOutputter (test by typing into terminal)
5. HotkeyManager (requires manual testing)
6. Main integration (ties everything together)

### Testing Strategy
- **Unit tests**: Mock external dependencies (mic, keyboard, model)
- **Integration tests**: Use real audio samples
- **Manual tests**: Test in real environments (terminal, VS Code)

## Current Status

**Phase**: 2.1 - Configuration Management
**Next Component**: `voice_prompt/config.py`

### Completed
- [x] Project structure and documentation
- [x] SPEC.md with detailed requirements
- [x] .clinerules with implementation guidance
- [x] requirements.txt with dependencies
- [x] config.yaml.example with all options
- [x] README.md with user documentation

### In Progress
- [ ] ConfigManager implementation
- [ ] Unit tests for ConfigManager

### Blocked/Waiting
- None currently

## Key Implementation Notes

### Config Loading Pattern
```python
# Load user config, merge with defaults
defaults = {...}
user_config = yaml.safe_load(config_file) if exists else {}
config = {**defaults, **user_config}  # User overrides defaults
```

### Audio Recording Pattern
```python
# Simple, cross-platform recording with sounddevice
import sounddevice as sd
audio = sd.rec(frames, samplerate=16000, channels=1, dtype='int16')
sd.wait()  # Block until recording completes
```

### Model Caching Pattern
```python
class WhisperTranscriber:
    def __init__(self):
        self.model = None  # Don't load yet
    
    def transcribe(self, audio_path):
        if self.model is None:
            self.model = WhisperModel("large-v3", ...)  # Load once
        return self.model.transcribe(audio_path)
```

### Hotkey Listener Pattern
```python
# Must run in background thread
listener = keyboard.Listener(on_press=..., on_release=...)
listener.start()  # Non-blocking
# Main thread continues...
```

## Critical Gotchas

### 1. Hotkey Listener Blocks
```python
# ❌ WRONG - blocks forever
with keyboard.Listener(...) as listener:
    listener.join()  # Nothing below here runs!

# ✅ RIGHT - runs in background
listener = keyboard.Listener(...)
listener.start()
```

### 2. Temp File Cleanup
Always use context managers or explicit cleanup:
```python
with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as f:
    # File auto-deleted after this block
```

### 3. Platform-Specific Paths
```python
# ❌ WRONG
config_path = "~/.voice_prompt/config.yaml"

# ✅ RIGHT
from pathlib import Path
config_path = Path.home() / ".voice_prompt" / "config.yaml"
```

### 4. Model Download on First Run
Don't assume model is downloaded. Handle gracefully:
```python
try:
    model = WhisperModel("large-v3", download_root=cache_dir)
except Exception as e:
    print("Downloading model (one-time, ~3GB)...")
    # Let it download, or provide manual instructions
```

## Target Platforms

### Primary: Linux (Arch-based Omarchy)
- Developer's main environment
- Test here first
- Use systemd for service management

### Secondary: Windows 10/11
- Test regularly during development
- Windows-specific installer (PowerShell)
- Windows service or startup entry

## Performance Targets

- **Startup**: <1 second (without model load)
- **First transcription**: <10 seconds (including model load)
- **Subsequent transcriptions**: <5 seconds
- **Memory footprint (idle)**: <100MB
- **Memory footprint (active)**: ~3-4GB (model in RAM)
- **Transcription accuracy**: >95% for technical speech

## Success Criteria

The project is successful when:
1. ✅ Works on both Linux and Windows with same commands
2. ✅ Transcribes "Harbor", "Stagehand", "Claude Code" correctly >95% of the time
3. ✅ Completes typical 30-second prompt in <5 seconds
4. ✅ Can be installed with single command on fresh systems
5. ✅ Used daily by André for Claude Code prompting
6. ✅ Zero crashes over 1000 uses

## Resources

- **SPEC.md**: Detailed technical specification
- **.clinerules**: Implementation patterns and best practices
- **TODO.md**: Phase-by-phase checklist
- **config.yaml.example**: All configuration options explained

## Questions & Decisions

### Resolved
- ✅ Model size: large-v3 (user has space, wants accuracy)
- ✅ Libraries: faster-whisper, sounddevice, pynput
- ✅ Architecture: Component-based with clean separation

### Open
- Should we support wake word activation? (Phase 7)
- Should we add real-time streaming? (Phase 7)
- Should we build a GUI? (Phase 7)

## Development Commands

See `.claude/commands/` for workflow-specific commands.

Common patterns:
```bash
# Test component
python -m voice_prompt.config
python -m voice_prompt.recorder

# Run full system
python -m voice_prompt

# Run tests
pytest tests/test_config.py -v
```
