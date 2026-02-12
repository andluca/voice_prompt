"""Tests for TextOutputter."""

from unittest.mock import patch, MagicMock

from voice_prompt.outputter import TextOutputter, _cleanup_text


class TestCleanupText:
    def test_collapses_spaces(self):
        assert _cleanup_text("hello   world") == "hello world"

    def test_strips(self):
        assert _cleanup_text("  hi  ") == "hi"

    def test_empty(self):
        assert _cleanup_text("") == ""


class TestTextOutputter:
    @patch("voice_prompt.outputter._keyboard")
    def test_type_mode(self, mock_kb):
        out = TextOutputter(mode="type", typing_speed="instant")
        out.output("hi")
        # pynput .type() called per character
        assert mock_kb.type.call_count == 2

    @patch("voice_prompt.outputter._keyboard")
    def test_add_newline(self, mock_kb):
        out = TextOutputter(mode="type", add_newline=True)
        out.output("x")
        # 'x' typed + newline (enter press/release)
        assert mock_kb.press.called

    @patch("voice_prompt.outputter._keyboard")
    def test_empty_text_does_nothing(self, mock_kb):
        out = TextOutputter()
        out.output("")
        mock_kb.type.assert_not_called()
