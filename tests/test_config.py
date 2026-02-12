"""Tests for ConfigManager."""

import textwrap
from pathlib import Path

import pytest

from voice_prompt.config import ConfigManager, DEFAULTS, _deep_merge


class TestDeepMerge:
    def test_flat(self):
        assert _deep_merge({"a": 1}, {"a": 2}) == {"a": 2}

    def test_nested(self):
        base = {"a": {"b": 1, "c": 2}}
        over = {"a": {"b": 99}}
        assert _deep_merge(base, over) == {"a": {"b": 99, "c": 2}}

    def test_new_key(self):
        assert _deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


class TestConfigManager:
    def test_defaults_when_no_file(self, tmp_path):
        cfg = ConfigManager(config_path=tmp_path / "nonexistent.yaml")
        assert cfg.hotkeys["record"] == "ctrl+shift+q"
        assert cfg.hotkeys["cancel"] == "esc"
        assert "mode" not in cfg.hotkeys
        assert cfg.transcription["model"] == "small"
        assert cfg.transcription["beam_size"] == 1
        assert cfg.transcription["num_threads"] == 0
        assert "word_timestamps" not in cfg.transcription
        assert cfg.audio["sample_rate"] == 16000
        assert cfg.audio["silence_duration"] == 2.0
        assert cfg.audio["grace_period"] == 10.0
        assert "format" not in cfg.audio
        assert cfg.notifications["enabled"] is True
        assert cfg.notifications["timeout"] == 3
        assert "on_record_start" not in cfg.notifications
        assert "advanced" not in cfg.config

    def test_loads_user_overrides(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text(textwrap.dedent("""\
            hotkeys:
              record: "ctrl+alt+r"
            audio:
              sample_rate: 44100
        """))
        cfg = ConfigManager(config_path=config_file)
        assert cfg.hotkeys["record"] == "ctrl+alt+r"
        assert cfg.audio["sample_rate"] == 44100
        # defaults preserved for unset keys
        assert cfg.hotkeys["cancel"] == "esc"

    def test_get_helper(self, tmp_path):
        cfg = ConfigManager(config_path=tmp_path / "nope.yaml")
        assert cfg.get("audio", "sample_rate") == 16000
        assert cfg.get("audio", "nonexistent", "fallback") == "fallback"

    def test_model_cache_dir(self, tmp_path):
        cfg = ConfigManager(config_path=tmp_path / "nope.yaml")
        assert isinstance(cfg.model_cache_dir, Path)

    def test_reload(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("hotkeys:\n  record: ctrl+1\n")
        cfg = ConfigManager(config_path=config_file)
        assert cfg.hotkeys["record"] == "ctrl+1"

        config_file.write_text("hotkeys:\n  record: ctrl+2\n")
        cfg.reload()
        assert cfg.hotkeys["record"] == "ctrl+2"

    def test_env_override_model_dir(self, tmp_path, monkeypatch):
        monkeypatch.setenv("VOICE_PROMPT_MODEL_DIR", "/custom/models")
        cfg = ConfigManager(config_path=tmp_path / "nope.yaml")
        assert cfg.system["model_cache_dir"] == "/custom/models"
