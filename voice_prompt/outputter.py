"""Text output — type or copy transcription results."""

import logging
import re
import time
from typing import Optional

from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)

_keyboard = Controller()


def _cleanup_text(text: str) -> str:
    """Remove extraneous whitespace and common transcription artefacts."""
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


class TextOutputter:
    """Delivers transcribed text to the active window."""

    def __init__(
        self,
        mode: str = "type",
        typing_speed: str = "instant",
        add_newline: bool = False,
        cleanup: bool = True,
    ) -> None:
        self.mode = mode
        self.typing_speed = typing_speed
        self.add_newline = add_newline
        self.cleanup = cleanup

    def output(self, text: str) -> None:
        if not text:
            logger.warning("Empty text, nothing to output")
            return

        if self.cleanup:
            text = _cleanup_text(text)

        if self.add_newline:
            text += "\n"

        if self.mode == "clipboard":
            self._copy_to_clipboard(text)
        else:
            self._type_text(text)

    def _type_text(self, text: str) -> None:
        logger.info("Typing %d characters (delay=%s)", len(text), self.typing_speed)
        time.sleep(0.2)  # let audio stream fully close

        delay = self._parse_delay()
        if delay:
            for char in text:
                if char == "\n":
                    _keyboard.press(Key.enter)
                    _keyboard.release(Key.enter)
                else:
                    _keyboard.type(char)
                time.sleep(delay)
        else:
            # Type entire string at once for instant mode
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if i > 0:
                    _keyboard.press(Key.enter)
                    _keyboard.release(Key.enter)
                if line:
                    _keyboard.type(line)

    def _parse_delay(self) -> Optional[float]:
        if self.typing_speed == "instant":
            return None
        try:
            return int(self.typing_speed) / 1000.0
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _copy_to_clipboard(text: str) -> None:
        """Copy text to clipboard using platform-appropriate method."""
        import platform

        system = platform.system()
        if system == "Windows":
            import subprocess
            process = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
            process.communicate(text.encode("utf-16le"))
        else:
            # Linux — try xclip, then xsel
            import shutil
            import subprocess
            if shutil.which("xclip"):
                p = subprocess.Popen(
                    ["xclip", "-selection", "clipboard"],
                    stdin=subprocess.PIPE,
                )
                p.communicate(text.encode())
            elif shutil.which("xsel"):
                p = subprocess.Popen(
                    ["xsel", "--clipboard", "--input"],
                    stdin=subprocess.PIPE,
                )
                p.communicate(text.encode())
            else:
                logger.error("No clipboard tool found (install xclip or xsel)")
                return

        logger.info("Copied %d characters to clipboard", len(text))
