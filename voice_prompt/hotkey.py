"""Global hotkey listener using pynput's built-in GlobalHotKeys."""

import logging
import threading
from typing import Callable, Optional

from pynput import keyboard

logger = logging.getLogger(__name__)

# Map friendly config names → pynput hotkey format
_MODIFIER_MAP = {
    "ctrl": "<ctrl>",
    "shift": "<shift>",
    "alt": "<alt>",
    "cmd": "<cmd>",
    "esc": "<esc>",
    "escape": "<esc>",
    "space": "<space>",
    "enter": "<enter>",
    "tab": "<tab>",
}


def _to_pynput_format(combo: str) -> str:
    """Convert 'ctrl+shift+q' → '<ctrl>+<shift>+q' for pynput."""
    parts = []
    for part in combo.lower().split("+"):
        part = part.strip()
        if part in _MODIFIER_MAP:
            parts.append(_MODIFIER_MAP[part])
        else:
            parts.append(part)
    return "+".join(parts)


class HotkeyManager:
    """Registers global hotkeys and dispatches callbacks."""

    def __init__(self) -> None:
        self._bindings: dict[str, Callable] = {}
        self._listener: Optional[keyboard.GlobalHotKeys] = None

    def register(self, combo: str, callback: Callable) -> None:
        """Register a hotkey combination (e.g. 'ctrl+shift+r')."""
        pynput_combo = _to_pynput_format(combo)
        # Wrap callback so it runs in a separate thread and won't block the listener
        def _threaded() -> None:
            threading.Thread(target=callback, daemon=True).start()
        self._bindings[pynput_combo] = _threaded
        logger.info("Registered hotkey: %s -> %s", combo, pynput_combo)

    def start(self) -> None:
        """Start listening for hotkeys in a background thread."""
        self._listener = keyboard.GlobalHotKeys(self._bindings)
        self._listener.daemon = True
        self._listener.start()
        logger.info("Hotkey listener started")

    def stop(self) -> None:
        """Stop the hotkey listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None
            logger.info("Hotkey listener stopped")
