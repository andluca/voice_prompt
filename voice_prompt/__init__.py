"""Voice-to-Claude: Hands-free voice prompting for Claude Code using local Whisper."""

__version__ = "0.1.0"

from voice_prompt.config import ConfigManager
from voice_prompt.hotkey import HotkeyManager
from voice_prompt.outputter import TextOutputter
from voice_prompt.recorder import AudioRecorder
from voice_prompt.transcriber import WhisperTranscriber

__all__ = [
    "ConfigManager",
    "HotkeyManager",
    "TextOutputter",
    "AudioRecorder",
    "WhisperTranscriber",
]
