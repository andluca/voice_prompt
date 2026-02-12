"""Tests for AudioRecorder."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voice_prompt.recorder import AudioRecorder


class TestAudioRecorder:
    def test_initial_state(self):
        rec = AudioRecorder()
        assert not rec.is_recording

    @patch("voice_prompt.recorder.sd.InputStream")
    def test_start_sets_recording(self, mock_stream_cls):
        mock_stream = MagicMock()
        mock_stream_cls.return_value = mock_stream

        rec = AudioRecorder()
        rec.start()
        assert rec.is_recording
        mock_stream.start.assert_called_once()

    def test_stop_without_start(self):
        rec = AudioRecorder()
        assert rec.stop() is None

    @patch("voice_prompt.recorder.sd.InputStream")
    def test_record_and_stop_produces_wav(self, mock_stream_cls, tmp_path):
        mock_stream = MagicMock()
        mock_stream_cls.return_value = mock_stream

        rec = AudioRecorder(temp_dir=str(tmp_path))
        rec.start()

        # Simulate audio callback delivering data
        fake_audio = np.zeros((1600, 1), dtype=np.int16)
        rec._audio_callback(fake_audio, 1600, None, None)
        rec._audio_callback(fake_audio, 1600, None, None)

        path = rec.stop()
        assert path is not None
        assert path.exists()
        assert path.suffix == ".wav"
        path.unlink()

    def test_cancel_discards_frames(self):
        rec = AudioRecorder()
        rec._frames = [np.zeros((100, 1), dtype=np.int16)]
        rec._recording = True
        rec.cancel()
        assert not rec.is_recording
        assert rec._frames == []
