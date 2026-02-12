# Voice-to-Claude Implementation TODO

## Phase 1: Core Components ✅ (Setup Complete)

- [x] Project structure
- [x] SPEC.md - Comprehensive specification
- [x] .clinerules - Agent skills and best practices
- [x] requirements.txt - Core dependencies
- [x] config.yaml.example - Configuration template
- [x] pyproject.toml - Package metadata
- [x] README.md - User documentation

## Phase 2: Core Implementation 🔨 (Next Steps)

### 2.1 Configuration Management
- [ ] Create `voice_prompt/config.py`
  - ConfigManager class
  - Load YAML with defaults
  - Validate configuration schema
  - Expand user paths (~/.voice-to-claude)
  - Handle missing/invalid config gracefully

### 2.2 Audio Recording
- [ ] Create `voice_prompt/recorder.py`
  - AudioRecorder class
  - Record audio with sounddevice
  - Support hold-to-record and toggle modes
  - Silence detection (optional)
  - Save to temporary WAV file
  - Handle microphone errors gracefully

### 2.3 Whisper Transcription
- [ ] Create `voice_prompt/transcriber.py`
  - WhisperTranscriber class
  - Load large-v3 model (auto-download first run)
  - Keep model in memory (don't reload)
  - GPU auto-detection with CPU fallback
  - Transcribe audio files to text
  - Handle transcription errors

### 2.4 Text Output
- [ ] Create `voice_prompt/outputter.py`
  - TextOutputter class
  - Type text into active window with pynput
  - Support instant and realistic typing speeds
  - Alternative clipboard mode
  - Handle special characters (newlines, tabs)
  - Cross-platform keyboard simulation

### 2.5 Hotkey Management
- [ ] Create `voice_prompt/hotkey.py`
  - HotkeyManager class
  - Register global hotkeys with pynput
  - Parse hotkey strings (e.g., "ctrl+shift+v")
  - Run listener in background thread
  - Handle hotkey events (record, cancel)
  - Cross-platform key mapping

### 2.6 Main Integration
- [ ] Create `voice_prompt/__init__.py`
  - Package initialization
  - Version info
  - Export main classes

- [ ] Create `voice_prompt/main.py`
  - CLI interface with commands (start, stop, test, status)
  - Integrate all components
  - Event loop for hotkey → record → transcribe → output
  - Error handling and logging
  - Desktop notifications
  - Graceful shutdown

## Phase 3: Installation & Tooling 🔧

### 3.1 Installation Scripts
- [ ] Create `scripts/setup.sh` (Linux)
  - Create virtual environment
  - Install dependencies
  - Create config directory
  - Copy config.yaml.example
  - Optional: Download model
  - Optional: Install systemd service

- [ ] Create `scripts/setup.ps1` (Windows)
  - Same as Linux but PowerShell
  - Windows-specific paths
  - Optional: Install as Windows service

### 3.2 Service Installation
- [ ] Create `scripts/install-service.sh` (Linux systemd)
  - Generate systemd unit file
  - Install to ~/.config/systemd/user/
  - Enable and start service
  - Instructions for uninstall

- [ ] Create `scripts/install-service.ps1` (Windows)
  - Windows service or startup entry
  - Auto-start on login

### 3.3 Model Download Script
- [ ] Create `scripts/download-model.py`
  - Pre-download Whisper model
  - Show download progress
  - Verify integrity
  - Handle network errors

## Phase 4: Testing 🧪

### 4.1 Unit Tests
- [ ] Create `tests/test_config.py`
  - Test config loading
  - Test defaults
  - Test validation
  - Test path expansion

- [ ] Create `tests/test_recorder.py`
  - Mock sounddevice
  - Test recording logic
  - Test error handling

- [ ] Create `tests/test_transcriber.py`
  - Test with sample audio files
  - Test model loading
  - Test GPU/CPU fallback

- [ ] Create `tests/test_outputter.py`
  - Mock pynput
  - Test typing simulation
  - Test clipboard mode

### 4.2 Integration Tests
- [ ] Create `tests/test_integration.py`
  - End-to-end workflow
  - Test with real audio samples
  - Test cross-platform compatibility

### 4.3 Test Audio Samples
- [ ] Create `tests/samples/` directory
  - technical_speech.wav (Harbor, Stagehand, Claude Code)
  - fast_speech.wav
  - accented_speech.wav
  - long_prompt.wav

## Phase 5: Documentation 📚

### 5.1 User Documentation
- [ ] Update README.md
  - Add actual screenshots/demos
  - Real performance benchmarks
  - More troubleshooting cases

- [ ] Create `CONTRIBUTING.md`
  - Development setup
  - Code style guidelines
  - Pull request process
  - Testing requirements

- [ ] Create `CHANGELOG.md`
  - Version history
  - Breaking changes
  - New features

### 5.2 Developer Documentation
- [ ] Add docstrings to all classes/methods
- [ ] Generate API documentation
- [ ] Architecture diagrams

## Phase 6: Polish & Release 🚀

### 6.1 Code Quality
- [ ] Run black formatter
- [ ] Run ruff linter
- [ ] Run mypy type checker
- [ ] Fix all warnings

### 6.2 Cross-Platform Testing
- [ ] Test on Arch Linux (Omarchy)
- [ ] Test on Ubuntu/Debian
- [ ] Test on Windows 10
- [ ] Test on Windows 11
- [ ] Document platform-specific issues

### 6.3 Performance Optimization
- [ ] Profile transcription speed
- [ ] Optimize memory usage
- [ ] Test with different model sizes
- [ ] Benchmark on CPU vs GPU

### 6.4 Release Preparation
- [ ] Create LICENSE file (MIT)
- [ ] Add GitHub Actions CI/CD
- [ ] Create release binaries (optional)
- [ ] Publish to PyPI (optional)
- [ ] Create demo video

## Phase 7: Future Enhancements 🔮

- [ ] Multi-language support
- [ ] Voice commands ("newline", "delete last")
- [ ] Custom vocabulary training
- [ ] GUI/system tray icon
- [ ] Configuration profiles
- [ ] Real-time streaming transcription
- [ ] Integration plugins (VS Code extension, etc.)

## Current Status

**Phase 1**: ✅ Complete - Setup and specification done
**Phase 2**: 🔨 Ready to start - Core implementation
**Next Step**: Create `voice_prompt/config.py`

## Notes for Claude Code

- Start with Phase 2.1 (Configuration Management)
- Build components in order (config → recorder → transcriber → outputter → hotkey → main)
- Test each component independently before integration
- Follow patterns in .clinerules
- Refer to SPEC.md for detailed requirements
- Ask for clarification if anything is ambiguous
