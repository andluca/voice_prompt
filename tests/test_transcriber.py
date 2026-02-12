"""Tests for WhisperTranscriber."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voice_prompt.transcriber import WhisperTranscriber


class TestWhisperTranscriber:
    def test_not_loaded_initially(self):
        t = WhisperTranscriber()
        assert not t.is_loaded

    def test_default_parameters(self):
        t = WhisperTranscriber()
        assert t.model_size == "small"
        assert t.beam_size == 1
        assert t.language == "en"
        assert t.vad_filter is True

    def test_resolve_device_cpu_when_no_torch(self):
        t = WhisperTranscriber(device="auto")
        with patch.dict("sys.modules", {"torch": None}):
            device, compute = t._resolve_device()
        assert device == "cpu"
        assert compute == "int8"

    def test_resolve_device_explicit(self):
        t = WhisperTranscriber(device="cpu", compute_type="float32")
        device, compute = t._resolve_device()
        assert device == "cpu"
        assert compute == "float32"

    @patch("faster_whisper.WhisperModel")
    def test_load_model(self, mock_model_cls):
        t = WhisperTranscriber(device="cpu")
        t.load_model()
        assert t.is_loaded
        mock_model_cls.assert_called_once()

    @patch("faster_whisper.WhisperModel")
    def test_load_model_is_idempotent(self, mock_model_cls):
        t = WhisperTranscriber(device="cpu")
        t.load_model()
        t.load_model()
        mock_model_cls.assert_called_once()

    @patch("faster_whisper.WhisperModel")
    def test_transcribe_returns_joined_segments(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model

        seg1 = MagicMock()
        seg1.text = "Hello"
        seg2 = MagicMock()
        seg2.text = "world"
        fake_info = MagicMock()
        fake_info.language = "en"
        fake_info.language_probability = 0.99
        fake_info.duration = 2.5
        mock_model.transcribe.return_value = ([seg1, seg2], fake_info)

        t = WhisperTranscriber(device="cpu")
        result = t.transcribe(Path("fake.wav"))
        assert result == "Hello world"

    @patch("faster_whisper.WhisperModel")
    def test_transcribe_single_segment(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model

        fake_seg = MagicMock()
        fake_seg.text = "Hello world"
        fake_info = MagicMock()
        fake_info.language = "en"
        fake_info.language_probability = 0.99
        fake_info.duration = 2.5
        mock_model.transcribe.return_value = ([fake_seg], fake_info)

        t = WhisperTranscriber(device="cpu")
        result = t.transcribe(Path("fake.wav"))
        assert result == "Hello world"
