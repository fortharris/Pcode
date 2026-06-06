"""Tests for Extensions.screen_utils."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication  # noqa: E402

from Extensions.screen_utils import primary_screen_geometry  # noqa: E402


def test_primary_screen_geometry():
    app = QApplication.instance() or QApplication([])
    geo = primary_screen_geometry(app)
    assert geo.width() > 0 and geo.height() > 0
