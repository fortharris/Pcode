"""Tests for tinted chrome icons."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.Icons import image_path, tinted_icon  # noqa: E402


def test_image_path_resolves_png():
    path = image_path("config")
    assert path.endswith("config.png") or path.endswith("config")
    assert os.path.isfile(path) or os.path.isfile(path + ".png")


def test_tinted_icon_not_null():
    icon = tinted_icon("config", "#E8E8E8", size=16)
    assert icon is not None
    assert not icon.isNull()
