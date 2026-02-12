"""Configuration management for Voice-to-Claude."""

import logging
import os
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    "hotkeys": {
        "record": "ctrl+shift+q",
        "cancel": "esc",
    },
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "silence_threshold": 0.01,
        "silence_duration": 2.0,
        "grace_period": 10.0,
        "max_recording_duration": 120,
    },
    "transcription": {
        "model": "small",
        "device": "auto",
        "compute_type": "int8",
        "language": "en",
        "initial_prompt": "",
        "vad_filter": True,
        "beam_size": 1,
        "num_threads": 0,
    },
    "output": {
        "mode": "type",
        "typing_speed": "instant",
        "add_newline": False,
        "cleanup": True,
    },
    "system": {
        "log_level": "INFO",
        "log_file": str(Path.home() / ".voice-to-claude" / "voice-prompt.log"),
        "log_max_size": 10,
        "log_backup_count": 3,
        "model_cache_dir": str(Path.home() / ".cache" / "whisper"),
        "temp_dir": None,
        "save_failed_audio": True,
        "failed_audio_dir": str(Path.home() / ".voice-to-claude" / "failed"),
    },
    "notifications": {
        "enabled": True,
        "timeout": 3,
    },
}

DEFAULT_CONFIG_PATH = Path.home() / ".voice-to-claude" / "config.yaml"


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override dict into base dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """Loads, validates, and provides access to configuration."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        env_path = os.environ.get("VOICE_PROMPT_CONFIG")
        if config_path:
            self.config_path = Path(config_path)
        elif env_path:
            self.config_path = Path(env_path)
        else:
            self.config_path = DEFAULT_CONFIG_PATH

        self.config = self._load()

    def _load(self) -> dict[str, Any]:
        user_config: dict[str, Any] = {}
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                logger.info("Loaded config from %s", self.config_path)
            except Exception:
                logger.warning("Failed to read %s, using defaults", self.config_path, exc_info=True)

        # Override model cache dir from env if set
        env_model_dir = os.environ.get("VOICE_PROMPT_MODEL_DIR")
        if env_model_dir:
            user_config.setdefault("system", {})["model_cache_dir"] = env_model_dir

        return _deep_merge(DEFAULTS, user_config)

    def reload(self) -> None:
        """Reload configuration from disk."""
        self.config = self._load()

    # -- convenience accessors --------------------------------------------------

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        return self.config.get(section, {}).get(key, fallback)

    @property
    def hotkeys(self) -> dict:
        return self.config["hotkeys"]

    @property
    def audio(self) -> dict:
        return self.config["audio"]

    @property
    def transcription(self) -> dict:
        return self.config["transcription"]

    @property
    def output(self) -> dict:
        return self.config["output"]

    @property
    def system(self) -> dict:
        return self.config["system"]

    @property
    def notifications(self) -> dict:
        return self.config["notifications"]

    @property
    def model_cache_dir(self) -> Path:
        return Path(self.config["system"]["model_cache_dir"]).expanduser()

    @property
    def log_level(self) -> str:
        return self.config["system"]["log_level"]
