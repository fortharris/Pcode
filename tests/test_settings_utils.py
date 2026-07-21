"""Tests for boolean settings helpers."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.settings_utils import (  # noqa: E402
    to_bool, from_bool, normalize_app_settings, app_settings_for_json,
)


def test_to_bool_variants():
    assert to_bool(True) is True
    assert to_bool("True") is True
    assert to_bool("false") is False
    assert to_bool(1) is True
    assert to_bool(None, default=True) is True


def test_from_bool():
    assert from_bool(True) == "True"
    assert from_bool(False) == "False"


def test_normalize_and_json_roundtrip():
    settings = {"EnableAlerts": "True", "Theme": "Dark", "EdgeColumn": "88"}
    normalize_app_settings(settings)
    assert settings["EnableAlerts"] is True
    out = app_settings_for_json(settings)
    assert out["EnableAlerts"] is True
    assert out["Theme"] == "Dark"


def test_normalize_migrates_native_ui_to_system():
    settings = {"UI": "Native", "Theme": "Dark"}
    normalize_app_settings(settings)
    assert settings["UI"] == "System"
    assert settings["Theme"] == "Dark"
