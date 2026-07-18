"""StyleSheet theme tokens overlay Default lexer styles."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions import StyleSheet  # noqa: E402


def test_theme_overlay_style_applies_dark_tokens():
    StyleSheet.apply_theme(None, "Dark")
    base = {
        "Default": ["Consolas", "#000000", 10, False, False, "#ffffff"],
        "Comment": ["Consolas", "#0000ff", 10, False, False, "#ffffff"],
        "Keyword": ["Consolas", "#0000ff", 10, False, False, "#ffffff"],
    }
    out = StyleSheet.theme_overlay_style(base)
    assert out["Default"][1] == StyleSheet.DARK["editorText"]
    assert out["Default"][5] == StyleSheet.DARK["editorPaper"]
    assert out["Comment"][1] == StyleSheet.DARK["editorComment"]
    assert out["Keyword"][1] == StyleSheet.DARK["editorKeyword"]
    # Original dict is not mutated.
    assert base["Default"][1] == "#000000"


def test_theme_overlay_style_light_tokens():
    StyleSheet.apply_theme(None, "Light")
    base = {
        "Default": ["Consolas", "#111111", 10, False, False, "#eeeeee"],
    }
    out = StyleSheet.theme_overlay_style(base)
    assert out["Default"][1] == StyleSheet.LIGHT["editorText"]
    assert out["Default"][5] == StyleSheet.LIGHT["editorPaper"]
