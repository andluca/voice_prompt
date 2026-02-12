"""Tests for HotkeyManager and _to_pynput_format."""

from unittest.mock import MagicMock, patch

import pytest

from voice_prompt.hotkey import HotkeyManager, _to_pynput_format, _MODIFIER_MAP


class TestToPynputFormat:
    """Tests for the _to_pynput_format conversion function."""

    def test_converts_standard_modifier_combo(self):
        assert _to_pynput_format("ctrl+shift+v") == "<ctrl>+<shift>+v"

    def test_converts_single_modifier_with_key(self):
        assert _to_pynput_format("ctrl+r") == "<ctrl>+r"

    def test_converts_triple_modifier_combo(self):
        assert _to_pynput_format("ctrl+shift+alt+x") == "<ctrl>+<shift>+<alt>+x"

    def test_converts_single_plain_key(self):
        assert _to_pynput_format("a") == "a"

    def test_converts_esc_to_angle_bracket_format(self):
        assert _to_pynput_format("esc") == "<esc>"

    def test_converts_escape_alias_to_esc(self):
        assert _to_pynput_format("escape") == "<esc>"

    def test_converts_special_keys_space(self):
        assert _to_pynput_format("space") == "<space>"

    def test_converts_special_keys_enter(self):
        assert _to_pynput_format("enter") == "<enter>"

    def test_converts_special_keys_tab(self):
        assert _to_pynput_format("tab") == "<tab>"

    def test_converts_cmd_modifier(self):
        assert _to_pynput_format("cmd+c") == "<cmd>+c"

    def test_handles_uppercase_input(self):
        assert _to_pynput_format("CTRL+SHIFT+V") == "<ctrl>+<shift>+v"

    def test_handles_mixed_case_input(self):
        assert _to_pynput_format("Ctrl+Shift+V") == "<ctrl>+<shift>+v"

    def test_handles_spaces_around_parts(self):
        assert _to_pynput_format("ctrl + shift + v") == "<ctrl>+<shift>+v"

    def test_unknown_key_passes_through(self):
        assert _to_pynput_format("ctrl+f12") == "<ctrl>+f12"

    def test_multiple_unknown_keys_pass_through(self):
        assert _to_pynput_format("f1+f2") == "f1+f2"

    def test_all_modifiers_in_map_are_converted(self):
        """Every key in _MODIFIER_MAP should be wrapped in angle brackets."""
        for friendly, pynput_form in _MODIFIER_MAP.items():
            result = _to_pynput_format(friendly)
            assert result == pynput_form, (
                f"_to_pynput_format({friendly!r}) returned {result!r}, expected {pynput_form!r}"
            )


class TestHotkeyManager:
    """Tests for the HotkeyManager class."""

    def test_initial_state_has_no_bindings(self):
        mgr = HotkeyManager()
        assert mgr._bindings == {}
        assert mgr._listener is None

    def test_register_stores_binding_with_pynput_format_key(self):
        mgr = HotkeyManager()
        callback = MagicMock()
        mgr.register("ctrl+shift+v", callback)
        assert "<ctrl>+<shift>+v" in mgr._bindings

    def test_register_multiple_bindings(self):
        mgr = HotkeyManager()
        mgr.register("ctrl+shift+v", MagicMock())
        mgr.register("esc", MagicMock())
        assert "<ctrl>+<shift>+v" in mgr._bindings
        assert "<esc>" in mgr._bindings
        assert len(mgr._bindings) == 2

    def test_register_overwrites_duplicate_combo(self):
        mgr = HotkeyManager()
        cb1 = MagicMock()
        cb2 = MagicMock()
        mgr.register("ctrl+a", cb1)
        mgr.register("ctrl+a", cb2)
        assert len(mgr._bindings) == 1

    def test_registered_callback_is_wrapped_in_thread(self):
        """The stored callback should spawn a thread when invoked, not call the original directly."""
        mgr = HotkeyManager()
        original_cb = MagicMock()
        mgr.register("ctrl+shift+v", original_cb)

        stored_cb = mgr._bindings["<ctrl>+<shift>+v"]
        # The stored callback is a wrapper, not the original
        assert stored_cb is not original_cb

    @patch("voice_prompt.hotkey.threading.Thread")
    def test_registered_callback_spawns_daemon_thread(self, mock_thread_cls):
        """Invoking the registered wrapper should create a daemon thread targeting the original callback."""
        mgr = HotkeyManager()
        original_cb = MagicMock()
        mgr.register("ctrl+shift+v", original_cb)

        stored_cb = mgr._bindings["<ctrl>+<shift>+v"]
        stored_cb()

        mock_thread_cls.assert_called_once_with(target=original_cb, daemon=True)
        mock_thread_cls.return_value.start.assert_called_once()

    @patch("voice_prompt.hotkey.keyboard.GlobalHotKeys")
    def test_start_creates_listener(self, mock_ghk_cls):
        mock_listener = MagicMock()
        mock_ghk_cls.return_value = mock_listener

        mgr = HotkeyManager()
        mgr.register("ctrl+shift+v", MagicMock())
        mgr.start()

        mock_ghk_cls.assert_called_once_with(mgr._bindings)
        assert mock_listener.daemon is True
        mock_listener.start.assert_called_once()
        assert mgr._listener is mock_listener

    @patch("voice_prompt.hotkey.keyboard.GlobalHotKeys")
    def test_stop_clears_listener(self, mock_ghk_cls):
        mock_listener = MagicMock()
        mock_ghk_cls.return_value = mock_listener

        mgr = HotkeyManager()
        mgr.register("ctrl+shift+v", MagicMock())
        mgr.start()
        mgr.stop()

        mock_listener.stop.assert_called_once()
        assert mgr._listener is None

    def test_stop_without_start_is_safe(self):
        mgr = HotkeyManager()
        mgr.stop()  # Should not raise
        assert mgr._listener is None

    @patch("voice_prompt.hotkey.keyboard.GlobalHotKeys")
    def test_stop_twice_is_safe(self, mock_ghk_cls):
        mock_listener = MagicMock()
        mock_ghk_cls.return_value = mock_listener

        mgr = HotkeyManager()
        mgr.register("ctrl+shift+v", MagicMock())
        mgr.start()
        mgr.stop()
        mgr.stop()  # Second stop should not raise

        mock_listener.stop.assert_called_once()
