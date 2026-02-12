"""Global hotkey listener using pynput."""

import logging
import threading
from typing import Callable, Optional

from pynput import keyboard

logger = logging.getLogger(__name__)

# Map config strings → pynput keys
_MODIFIER_MAP = {
    "ctrl": keyboard.Key.ctrl_l,
    "shift": keyboard.Key.shift,
    "alt": keyboard.Key.alt_l,
    "cmd": keyboard.Key.cmd,
}


def _parse_hotkey(combo: str) -> set:
    """Parse a hotkey string like 'ctrl+shift+v' into pynput key objects."""
    keys: set = set()
    for part in combo.lower().split("+"):
        part = part.strip()
        if part in _MODIFIER_MAP:
            keys.add(_MODIFIER_MAP[part])
        elif len(part) == 1:
            keys.add(keyboard.KeyCode.from_char(part))
        else:
            # Try named key (e.g. "escape", "space")
            try:
                keys.add(getattr(keyboard.Key, part))
            except AttributeError:
                logger.warning("Unknown key: %s", part)
    return keys


class HotkeyManager:
    """Registers global hotkeys and dispatches callbacks."""

    def __init__(self) -> None:
        self._hotkeys: dict[frozenset, Callable] = {}
        self._pressed: set = set()
        self._listener: Optional[keyboard.Listener] = None
        self._lock = threading.Lock()

    def register(self, combo: str, callback: Callable) -> None:
        """Register a hotkey combination (e.g. 'ctrl+shift+v')."""
        keys = frozenset(_parse_hotkey(combo))
        self._hotkeys[keys] = callback
        logger.info("Registered hotkey: %s", combo)

    def start(self) -> None:
        """Start listening for hotkeys in a background thread."""
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()
        logger.info("Hotkey listener started")

    def stop(self) -> None:
        """Stop the hotkey listener."""
        if self._listener:
            self._listener.stop()
            self._listener = None
            logger.info("Hotkey listener stopped")

    def _on_press(self, key: keyboard.Key) -> None:
        with self._lock:
            self._pressed.add(self._normalize(key))
            pressed_frozen = frozenset(self._pressed)

        for combo, callback in self._hotkeys.items():
            if combo == pressed_frozen:
                logger.debug("Hotkey matched: %s", combo)
                threading.Thread(target=callback, daemon=True).start()

    def _on_release(self, key: keyboard.Key) -> None:
        with self._lock:
            self._pressed.discard(self._normalize(key))

    @staticmethod
    def _normalize(key: keyboard.Key) -> keyboard.Key:
        """Collapse left/right modifiers into a single key."""
        if hasattr(key, "vk"):
            return key
        # Map right-side modifiers to left-side
        mapping = {
            keyboard.Key.ctrl_r: keyboard.Key.ctrl_l,
            keyboard.Key.shift_r: keyboard.Key.shift,
            keyboard.Key.alt_r: keyboard.Key.alt_l,
            keyboard.Key.alt_gr: keyboard.Key.alt_l,
        }
        return mapping.get(key, key)
