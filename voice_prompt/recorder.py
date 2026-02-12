"""Audio recording using sounddevice."""

import logging
import tempfile
import threading
import wave
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Captures microphone audio to a WAV file."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        silence_threshold: float = 0.01,
        silence_duration: float = 2.0,
        max_duration: float = 120.0,
        temp_dir: Optional[str] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.temp_dir = temp_dir

        self._recording = False
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        """Begin recording audio from the default microphone."""
        if self._recording:
            logger.warning("Already recording")
            return

        self._frames = []
        self._recording = True
        self._silent_chunks = 0
        self._chunk_size = int(self.sample_rate * 0.1)  # 100ms chunks
        self._max_chunks = int(self.max_duration / 0.1)
        self._silence_chunks_needed = int(self.silence_duration / 0.1)

        logger.info("Recording started (sample_rate=%d)", self.sample_rate)

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self._chunk_size,
            callback=self._audio_callback,
        )
        self._stream.start()

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info: object, status: object
    ) -> None:
        if status:
            logger.warning("Audio status: %s", status)
        if not self._recording:
            return

        with self._lock:
            self._frames.append(indata.copy())

            # Silence detection
            if self.silence_threshold > 0:
                amplitude = np.abs(indata).mean() / 32768.0
                if amplitude < self.silence_threshold:
                    self._silent_chunks += 1
                else:
                    self._silent_chunks = 0

                if self._silent_chunks >= self._silence_chunks_needed and len(self._frames) > 10:
                    logger.info("Silence detected, auto-stopping")
                    self._recording = False

            # Max duration safety
            if len(self._frames) >= self._max_chunks:
                logger.info("Max recording duration reached")
                self._recording = False

    def stop(self) -> Optional[Path]:
        """Stop recording and save audio to a temp WAV file. Returns the file path."""
        if not self._recording and not self._frames:
            logger.warning("Not recording")
            return None

        self._recording = False

        if hasattr(self, "_stream"):
            self._stream.stop()
            self._stream.close()

        with self._lock:
            if not self._frames:
                logger.warning("No audio captured")
                return None
            audio_data = np.concatenate(self._frames, axis=0)

        # Save to temp WAV
        tmp = tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False, dir=self.temp_dir
        )
        tmp_path = Path(tmp.name)
        tmp.close()

        with wave.open(str(tmp_path), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

        duration = len(audio_data) / self.sample_rate
        logger.info("Saved %.1fs of audio to %s", duration, tmp_path)
        return tmp_path

    def cancel(self) -> None:
        """Cancel the current recording and discard audio."""
        self._recording = False
        if hasattr(self, "_stream"):
            self._stream.stop()
            self._stream.close()
        self._frames = []
        logger.info("Recording cancelled")
