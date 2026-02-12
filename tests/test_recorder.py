"""Tests for AudioRecorder."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voice_prompt.recorder import AudioRecorder


class TestAudioRecorder:
    def test_initial_state(self):
        rec = AudioRecorder()
        assert not rec.is_recording

    def test_default_parameters(self):
        rec = AudioRecorder()
        assert rec.sample_rate == 16000
        assert rec.silence_duration == 2.0
        assert rec.grace_period == 10.0

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

        # Simulate audio callback delivering data (loud enough to register as speech)
        fake_audio = np.full((1600, 1), 5000, dtype=np.int16)
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

    @patch("voice_prompt.recorder.sd.InputStream")
    def test_grace_period_auto_stops_when_no_speech(self, mock_stream_cls):
        """When no speech is detected within the grace period, recording stops automatically."""
        mock_stream = MagicMock()
        mock_stream_cls.return_value = mock_stream

        auto_stopped = []
        rec = AudioRecorder(
            grace_period=0.5,  # 0.5 seconds = 5 chunks at 100ms each
            on_auto_stop=lambda: auto_stopped.append(True),
        )
        rec.start()

        # Feed silent audio until grace period expires (need >= 5 chunks)
        silent_audio = np.zeros((1600, 1), dtype=np.int16)
        for _ in range(6):
            rec._audio_callback(silent_audio, 1600, None, None)

        assert not rec.is_recording

    @patch("voice_prompt.recorder.sd.InputStream")
    def test_grace_period_does_not_stop_when_speech_detected(self, mock_stream_cls):
        """Speech within the grace period prevents the grace-period auto-stop."""
        mock_stream = MagicMock()
        mock_stream_cls.return_value = mock_stream

        rec = AudioRecorder(grace_period=0.5)
        rec.start()

        # Feed loud audio (speech) within the grace period
        loud_audio = np.full((1600, 1), 5000, dtype=np.int16)
        for _ in range(3):
            rec._audio_callback(loud_audio, 1600, None, None)

        assert rec.is_recording
        assert rec._speech_detected

    @patch("voice_prompt.recorder.sd.InputStream")
    def test_silence_after_speech_auto_stops(self, mock_stream_cls):
        """After speech is detected, sustained silence triggers auto-stop."""
        mock_stream = MagicMock()
        mock_stream_cls.return_value = mock_stream

        rec = AudioRecorder(silence_duration=0.3, grace_period=10.0)
        rec.start()

        # First deliver speech
        loud_audio = np.full((1600, 1), 5000, dtype=np.int16)
        rec._audio_callback(loud_audio, 1600, None, None)
        assert rec._speech_detected

        # Then deliver enough silence to trigger auto-stop (0.3s / 0.1s = 3 chunks)
        silent_audio = np.zeros((1600, 1), dtype=np.int16)
        for _ in range(4):
            rec._audio_callback(silent_audio, 1600, None, None)

        assert not rec.is_recording

    @patch("voice_prompt.recorder.sd.InputStream")
    def test_custom_grace_period_value(self, mock_stream_cls):
        """Verify that custom grace_period is stored and used for chunk calculation."""
        mock_stream = MagicMock()
        mock_stream_cls.return_value = mock_stream

        rec = AudioRecorder(grace_period=5.0)
        rec.start()
        assert rec.grace_period == 5.0
        # 5.0 seconds / 0.1 second chunks = 50 chunks
        assert rec._grace_chunks == 50
