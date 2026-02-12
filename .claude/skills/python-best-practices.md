# Python Best Practices for Voice Prompt

## Code Style

### Follow PEP 8 with Modern Python
```python
# Use type hints (Python 3.9+)
def transcribe(self, audio_path: Path) -> str:
    """Transcribe audio file to text."""
    ...

# Use modern syntax
config: dict[str, Any] = {...}  # Not Dict[str, Any]
files: list[Path] = [...]        # Not List[Path]
```

### Pathlib Over os.path
```python
# ❌ Don't use os.path
config_dir = os.path.expanduser("~/.voice_prompt")
config_file = os.path.join(config_dir, "config.yaml")

# ✅ Use pathlib
config_dir = Path.home() / ".voice_prompt"
config_file = config_dir / "config.yaml"
```

### Context Managers for Resources
```python
# ✅ Always use context managers
with open(file_path) as f:
    content = f.read()

# ✅ For temp files
with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp:
    # File automatically deleted
    process(tmp.name)
```

## Error Handling

### Specific Exceptions
```python
# ❌ Too broad
try:
    model = load_model()
except Exception:
    pass

# ✅ Specific and informative
try:
    model = WhisperModel("large-v3")
except FileNotFoundError as e:
    logger.error(f"Model not found: {e}")
    raise ModelNotFoundError("Run 'voice-prompt download-model' first")
except RuntimeError as e:
    logger.error(f"Failed to load model: {e}")
    raise
```

### Never Swallow Exceptions Silently
```python
# ❌ Silent failure
try:
    transcribe(audio)
except:
    pass  # User has no idea what happened!

# ✅ Log and handle
try:
    text = transcribe(audio)
except TranscriptionError as e:
    logger.error(f"Transcription failed: {e}")
    notify_user("Transcription failed. Check logs for details.")
    return None
```

## Class Design

### Single Responsibility
```python
# ✅ Each class does one thing well
class AudioRecorder:
    """Records audio from microphone. Nothing else."""
    
    def record(self, duration: float) -> np.ndarray:
        """Record audio for specified duration."""
        ...

class WhisperTranscriber:
    """Transcribes audio to text. Nothing else."""
    
    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file to text."""
        ...
```

### Lazy Initialization for Expensive Resources
```python
class WhisperTranscriber:
    def __init__(self, model_name: str = "large-v3"):
        self.model_name = model_name
        self._model = None  # Don't load yet!
    
    @property
    def model(self):
        """Lazy load model on first access."""
        if self._model is None:
            logger.info(f"Loading {self.model_name} model...")
            self._model = WhisperModel(self.model_name)
        return self._model
    
    def transcribe(self, audio_path: Path) -> str:
        # Model loads here on first call
        segments, _ = self.model.transcribe(str(audio_path))
        return " ".join(s.text for s in segments)
```

## Logging

### Structured Logging
```python
import logging

logger = logging.getLogger(__name__)

# ✅ Use appropriate levels
logger.debug("Recording started")  # Development info
logger.info("Model loaded successfully")  # Normal operation
logger.warning("Using CPU, GPU not available")  # Degraded mode
logger.error("Failed to open microphone")  # Error occurred
logger.critical("Model file corrupted")  # Fatal error

# ✅ Include context
logger.info(f"Transcribed {len(text)} characters in {duration:.2f}s")
logger.error(f"Microphone error: {e}", exc_info=True)
```

### Don't Log Sensitive Data
```python
# ❌ Never log transcribed text (privacy!)
logger.info(f"Transcription result: {text}")

# ✅ Log metadata only
logger.info(f"Transcription complete: {len(text)} chars, {duration:.2f}s")
```

## Configuration

### Defaults + Overrides Pattern
```python
DEFAULT_CONFIG = {
    "hotkeys": {
        "record": "ctrl+shift+v",
        "mode": "toggle",
    },
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
    },
    "transcription": {
        "model": "large-v3",
        "device": "auto",
    }
}

def load_config(config_path: Path | None = None) -> dict:
    """Load config with defaults."""
    config = DEFAULT_CONFIG.copy()
    
    if config_path and config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f)
        # Deep merge user config
        config.update(user_config)
    
    return config
```

### Validate Configuration
```python
def validate_config(config: dict) -> None:
    """Validate configuration values."""
    # Check required fields
    assert "hotkeys" in config, "Missing 'hotkeys' section"
    
    # Validate values
    sample_rate = config["audio"]["sample_rate"]
    assert sample_rate in [8000, 16000, 22050, 44100], \
        f"Invalid sample_rate: {sample_rate}"
    
    # Validate model
    valid_models = ["tiny", "base", "small", "medium", "large-v3"]
    model = config["transcription"]["model"]
    assert model in valid_models, \
        f"Invalid model: {model}. Must be one of {valid_models}"
```

## Async vs Sync

### Don't Use Async Unless Necessary
```python
# ❌ Unnecessary async (no I/O benefit here)
async def transcribe(audio_path: Path) -> str:
    result = await whisper_model.transcribe(audio_path)
    return result

# ✅ Sync is simpler and sufficient
def transcribe(audio_path: Path) -> str:
    """Transcribe audio (CPU/GPU bound, async doesn't help)."""
    segments, _ = model.transcribe(str(audio_path))
    return " ".join(s.text for s in segments)
```

### When to Use Async
- Multiple I/O operations that can run concurrently
- Network requests
- File I/O if truly concurrent

For this project: **Don't use async**. The bottleneck is CPU/GPU (model inference), not I/O.

## Testing

### Mock External Dependencies
```python
from unittest.mock import patch, MagicMock
import pytest

@patch('sounddevice.rec')
def test_record_audio(mock_rec):
    """Test recording without actual microphone."""
    mock_rec.return_value = np.zeros((16000, 1))
    
    recorder = AudioRecorder()
    audio = recorder.record(duration=1.0)
    
    assert audio is not None
    assert len(audio) == 16000
    mock_rec.assert_called_once()
```

### Fixtures for Test Data
```python
@pytest.fixture
def sample_audio_file(tmp_path):
    """Create temporary audio file for testing."""
    audio_file = tmp_path / "test.wav"
    # Create minimal WAV file
    # ... (use scipy.io.wavfile.write or similar)
    return audio_file

def test_transcription(sample_audio_file):
    transcriber = WhisperTranscriber()
    text = transcriber.transcribe(sample_audio_file)
    assert isinstance(text, str)
```

## Performance

### Profile Before Optimizing
```python
import cProfile
import pstats

def profile_transcription():
    with cProfile.Profile() as pr:
        transcriber = WhisperTranscriber()
        transcriber.transcribe(audio_file)
    
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

### Cache Expensive Operations
```python
from functools import lru_cache

class ConfigManager:
    @lru_cache(maxsize=1)
    def load_config(self) -> dict:
        """Load config once, cache result."""
        # Expensive YAML parsing happens once
        ...
```

## Documentation

### Docstrings for Public APIs
```python
def transcribe(self, audio_path: Path, language: str = "en") -> str:
    """Transcribe audio file to text using Whisper.
    
    Args:
        audio_path: Path to audio file (WAV format, 16kHz)
        language: Language code (e.g., "en", "es", "fr")
    
    Returns:
        Transcribed text as string
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
        TranscriptionError: If transcription fails
    
    Example:
        >>> transcriber = WhisperTranscriber()
        >>> text = transcriber.transcribe(Path("audio.wav"))
        >>> print(text)
        'This is the transcribed text'
    """
    ...
```

### Comments for "Why", Not "What"
```python
# ❌ Obvious comment
# Load the model
model = WhisperModel("large-v3")

# ✅ Explains reasoning
# Use int8 quantization on CPU for 2x speedup with minimal accuracy loss
compute_type = "int8" if device == "cpu" else "float16"
model = WhisperModel("large-v3", compute_type=compute_type)
```

## Common Anti-Patterns to Avoid

### 1. Mutable Default Arguments
```python
# ❌ Dangerous - list is shared across calls!
def record(options={}):
    options["recorded"] = True
    return options

# ✅ Use None and create inside
def record(options=None):
    if options is None:
        options = {}
    options["recorded"] = True
    return options
```

### 2. Bare Except
```python
# ❌ Catches everything, even KeyboardInterrupt!
try:
    transcribe()
except:
    pass

# ✅ Catch specific exceptions
try:
    transcribe()
except TranscriptionError:
    handle_error()
```

### 3. String Concatenation in Loops
```python
# ❌ Inefficient - creates new string each iteration
result = ""
for segment in segments:
    result += segment.text

# ✅ Use join
result = "".join(segment.text for segment in segments)
```

### 4. Not Using enumerate
```python
# ❌ Manual indexing
for i in range(len(items)):
    print(f"{i}: {items[i]}")

# ✅ Use enumerate
for i, item in enumerate(items):
    print(f"{i}: {item}")
```

## Security

### Don't Log Credentials
```python
# ❌ Never log API keys, passwords, etc.
logger.info(f"Config: {config}")  # Might contain secrets!

# ✅ Log safely
safe_config = {k: v for k, v in config.items() if k != "api_key"}
logger.info(f"Config: {safe_config}")
```

### Validate User Input
```python
def set_hotkey(self, hotkey: str) -> None:
    """Set hotkey combination."""
    # ✅ Validate before using
    valid_pattern = r'^(ctrl|alt|shift)\+(ctrl|alt|shift\+)?[a-z]$'
    if not re.match(valid_pattern, hotkey):
        raise ValueError(f"Invalid hotkey format: {hotkey}")
    
    self.hotkey = hotkey
```

## Code Organization

### One Class Per File (Usually)
```
voice_prompt/
├── config.py       # ConfigManager only
├── recorder.py     # AudioRecorder only
├── transcriber.py  # WhisperTranscriber only
└── outputter.py    # TextOutputter only
```

### Keep __init__.py Clean
```python
# voice_prompt/__init__.py

"""Voice Prompt: Voice-to-text for hands-free coding."""

__version__ = "0.1.0"

# Only export main public API
from .main import VoicePrompt
from .config import ConfigManager

__all__ = ["VoicePrompt", "ConfigManager"]
```

## Dependencies

### Pin Major Versions, Allow Minor Updates
```python
# requirements.txt
faster-whisper>=1.0.0,<2.0.0  # Allow 1.x updates
sounddevice>=0.4.6,<0.5.0
pynput>=1.7.6,<2.0.0
```

### Import Order (PEP 8)
```python
# 1. Standard library
import logging
import sys
from pathlib import Path
from typing import Any

# 2. Third-party
import numpy as np
import yaml
from faster_whisper import WhisperModel

# 3. Local
from .config import ConfigManager
from .recorder import AudioRecorder
```
