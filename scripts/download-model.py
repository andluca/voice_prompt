#!/usr/bin/env python3
"""Pre-download the Whisper model so first transcription is instant."""

import sys
from pathlib import Path

# Add project root to path so we can import voice_prompt
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voice_prompt.config import ConfigManager
from voice_prompt.transcriber import WhisperTranscriber


def main() -> None:
    cfg = ConfigManager()
    model = cfg.transcription["model"]
    cache = cfg.model_cache_dir

    print(f"Downloading Whisper '{model}' to {cache}…")
    print("This is a one-time download (~3 GB for large-v3). Please wait.")

    t = WhisperTranscriber(
        model_size=model,
        device=cfg.transcription["device"],
        compute_type=cfg.transcription["compute_type"],
        cache_dir=str(cache),
    )
    t.load_model()
    print("Done! Model is cached and ready.")


if __name__ == "__main__":
    main()
