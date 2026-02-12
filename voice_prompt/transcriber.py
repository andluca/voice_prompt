"""Whisper transcription using faster-whisper."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """Lazy-loaded Whisper model for audio transcription."""

    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "auto",
        compute_type: str = "int8",
        cache_dir: Optional[str] = None,
        language: str = "en",
        beam_size: int = 5,
        vad_filter: bool = True,
        initial_prompt: str = "",
        num_threads: int = 0,
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.cache_dir = cache_dir
        self.language = language
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.initial_prompt = initial_prompt
        self.num_threads = num_threads

        self._model = None  # lazy loaded

    def _resolve_device(self) -> tuple[str, str]:
        """Determine device and compute_type, falling back to CPU."""
        if self.device != "auto":
            return self.device, self.compute_type

        try:
            import torch
            if torch.cuda.is_available():
                logger.info("CUDA available — using GPU")
                return "cuda", "float16"
        except ImportError:
            pass

        logger.info("Using CPU with int8 quantization")
        return "cpu", "int8"

    def load_model(self) -> None:
        """Load the Whisper model into memory (downloads on first run)."""
        if self._model is not None:
            return

        from faster_whisper import WhisperModel

        device, compute_type = self._resolve_device()

        logger.info(
            "Loading Whisper %s model (device=%s, compute=%s)…",
            self.model_size, device, compute_type,
        )

        kwargs: dict = {
            "device": device,
            "compute_type": compute_type,
        }
        if self.cache_dir:
            kwargs["download_root"] = self.cache_dir
        if self.num_threads > 0:
            kwargs["cpu_threads"] = self.num_threads

        self._model = WhisperModel(self.model_size, **kwargs)
        logger.info("Model loaded successfully")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe an audio file to text. Loads the model if needed."""
        self.load_model()

        logger.info("Transcribing %s", audio_path)

        segments, info = self._model.transcribe(
            str(audio_path),
            language=self.language if self.language else None,
            beam_size=self.beam_size,
            vad_filter=self.vad_filter,
            initial_prompt=self.initial_prompt or None,
        )

        text = " ".join(seg.text.strip() for seg in segments)
        logger.info(
            "Transcription complete (lang=%s, prob=%.2f, duration=%.1fs)",
            info.language, info.language_probability, info.duration,
        )
        return text.strip()
