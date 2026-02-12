"""CLI entry-point and integration layer for Voice Prompt."""

import argparse
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from voice_prompt.config import ConfigManager
from voice_prompt.hotkey import HotkeyManager
from voice_prompt.outputter import TextOutputter
from voice_prompt.recorder import AudioRecorder
from voice_prompt.transcriber import WhisperTranscriber

console = Console()
logger = logging.getLogger("voice_prompt")

LOCK_FILE = Path.home() / ".voice_prompt" / "voice-prompt.lock"


def _acquire_lock() -> bool:
    """Try to acquire a lock file. Returns False if another instance is running."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            os.kill(old_pid, 0)  # signal 0 = just check if alive
            return False
        except (OSError, ValueError):
            pass  # process is dead or bad pid, stale lock
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def _release_lock() -> None:
    LOCK_FILE.unlink(missing_ok=True)


def _setup_logging(
    level: str,
    log_file: Optional[str],
    log_max_size: int = 10,
    log_backup_count: int = 3,
) -> None:
    handlers: list[logging.Handler] = [RichHandler(rich_tracebacks=True, show_path=False)]

    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        from logging.handlers import RotatingFileHandler

        handlers.append(
            RotatingFileHandler(
                log_path,
                maxBytes=log_max_size * 1024 * 1024,
                backupCount=log_backup_count,
            )
        )

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
    )


def _notify(
    title: str,
    message: str,
    timeout: int = 3,
    *,
    enabled: bool = True,
) -> None:
    if not enabled:
        return
    try:
        from plyer import notification

        notification.notify(title=title, message=message, timeout=timeout)
    except Exception:
        pass  # notifications are best-effort


class VoicePrompt:
    """Main application that glues all components together."""

    def __init__(self, config: ConfigManager) -> None:
        self.config = config

        self.recorder = AudioRecorder(
            sample_rate=config.audio["sample_rate"],
            channels=config.audio["channels"],
            silence_threshold=config.audio["silence_threshold"],
            silence_duration=config.audio["silence_duration"],
            grace_period=config.audio.get("grace_period", 10.0),
            max_duration=config.audio["max_recording_duration"],
            temp_dir=config.system.get("temp_dir"),
            on_auto_stop=self._finish_recording,
        )

        self.transcriber = WhisperTranscriber(
            model_size=config.transcription["model"],
            device=config.transcription["device"],
            compute_type=config.transcription["compute_type"],
            cache_dir=str(config.model_cache_dir),
            language=config.transcription["language"],
            beam_size=config.transcription["beam_size"],
            vad_filter=config.transcription["vad_filter"],
            initial_prompt=config.transcription["initial_prompt"],
            num_threads=config.transcription["num_threads"],
        )

        self.outputter = TextOutputter(
            mode=config.output["mode"],
            typing_speed=str(config.output["typing_speed"]),
            add_newline=config.output["add_newline"],
            cleanup=config.output["cleanup"],
        )

        self.hotkey_mgr = HotkeyManager()
        self._notify_enabled = config.notifications["enabled"]
        self._notify_timeout = config.notifications["timeout"]
        self._running = False

    # -- hotkey callbacks ------------------------------------------------------

    def _on_record_toggle(self) -> None:
        if self.recorder.is_recording:
            self._finish_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        try:
            self.recorder.start()
            console.print("[bold green]Recording…[/] Press hotkey again to stop.")
        except Exception:
            logger.exception("Failed to start recording")

    def _finish_recording(self) -> None:
        audio_path = self.recorder.stop()
        if audio_path is None:
            return

        console.print("[cyan]Transcribing…[/]")
        try:
            text = self.transcriber.transcribe(audio_path)
        except Exception:
            logger.exception("Transcription failed")
            if self.config.system["save_failed_audio"]:
                failed_dir = Path(self.config.system["failed_audio_dir"]).expanduser()
                failed_dir.mkdir(parents=True, exist_ok=True)
                dest = failed_dir / audio_path.name
                shutil.copy2(audio_path, dest)
                logger.info("Saved failed audio to %s", dest)
            return
        finally:
            audio_path.unlink(missing_ok=True)

        if not text:
            return

        console.print(f"[green]Transcribed:[/] {text}")
        self.outputter.output(text)

    def _on_cancel(self) -> None:
        if self.recorder.is_recording:
            self.recorder.cancel()
            console.print("[yellow]Recording cancelled.[/]")

    # -- lifecycle -------------------------------------------------------------

    def run(self) -> None:
        """Start listening for hotkeys (blocks until interrupted)."""
        console.print("[cyan]Loading Whisper model into memory…[/]")
        self.transcriber.load_model()
        console.print("[green]Model ready![/]")
        _notify(
            "Voice Prompt",
            "Model loaded. Ready to record!",
            timeout=self._notify_timeout,
            enabled=self._notify_enabled,
        )

        self.hotkey_mgr.register(
            self.config.hotkeys["record"], self._on_record_toggle
        )
        self.hotkey_mgr.register(
            self.config.hotkeys["cancel"], self._on_cancel
        )
        self.hotkey_mgr.start()

        self._running = True
        record_key = self.config.hotkeys["record"]
        console.print(
            f"[bold]Voice Prompt running.[/] Press [cyan]{record_key}[/] to record, "
            f"[cyan]Ctrl+C[/] to quit."
        )
        _notify(
            "Voice Prompt",
            f"Ready! Press {record_key} to record.",
            timeout=self._notify_timeout,
            enabled=self._notify_enabled,
        )

        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.hotkey_mgr.stop()
            console.print("[bold]Stopped.[/]")


def _cmd_start(args: argparse.Namespace) -> None:
    if not _acquire_lock():
        _notify("Voice Prompt", "Already running!")
        return

    cfg = ConfigManager(config_path=Path(args.config) if args.config else None)
    _setup_logging(
        cfg.log_level,
        cfg.system.get("log_file"),
        log_max_size=cfg.system["log_max_size"],
        log_backup_count=cfg.system["log_backup_count"],
    )
    app = VoicePrompt(cfg)
    try:
        app.run()
    finally:
        _release_lock()


def _cmd_test(args: argparse.Namespace) -> None:
    """Quick test: record 5 seconds and transcribe."""
    cfg = ConfigManager(config_path=Path(args.config) if args.config else None)
    _setup_logging(cfg.log_level, None)

    console.print("[bold]Test mode[/] — recording for 5 seconds…")
    recorder = AudioRecorder(
        sample_rate=cfg.audio["sample_rate"],
        channels=cfg.audio["channels"],
    )
    recorder.start()
    time.sleep(5)
    audio_path = recorder.stop()

    if audio_path is None:
        console.print("[red]No audio captured.[/]")
        return

    console.print("[cyan]Transcribing…[/]")
    transcriber = WhisperTranscriber(
        model_size=cfg.transcription["model"],
        device=cfg.transcription["device"],
        compute_type=cfg.transcription["compute_type"],
        cache_dir=str(cfg.model_cache_dir),
        language=cfg.transcription["language"],
    )
    text = transcriber.transcribe(audio_path)
    audio_path.unlink(missing_ok=True)
    console.print(f"[green]Result:[/] {text}")


def _cmd_download_model(args: argparse.Namespace) -> None:
    cfg = ConfigManager(config_path=Path(args.config) if args.config else None)
    _setup_logging("INFO", None)

    console.print(
        f"[bold]Downloading Whisper {cfg.transcription['model']}[/] "
        f"to {cfg.model_cache_dir}…"
    )
    transcriber = WhisperTranscriber(
        model_size=cfg.transcription["model"],
        device=cfg.transcription["device"],
        compute_type=cfg.transcription["compute_type"],
        cache_dir=str(cfg.model_cache_dir),
    )
    transcriber.load_model()
    console.print("[green]Model downloaded and ready![/]")


def cli() -> None:
    parser = argparse.ArgumentParser(
        prog="voice-prompt",
        description="Voice-to-text for hands-free Claude Code prompting",
    )
    parser.add_argument(
        "-c", "--config", default=None, help="Path to config YAML file"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("start", help="Start listening for voice input")
    sub.add_parser("test", help="Record 5 seconds and transcribe (quick test)")
    sub.add_parser("download-model", help="Pre-download the Whisper model")

    args = parser.parse_args()
    command = args.command or "start"

    dispatch = {
        "start": _cmd_start,
        "test": _cmd_test,
        "download-model": _cmd_download_model,
    }
    dispatch[command](args)


if __name__ == "__main__":
    cli()
