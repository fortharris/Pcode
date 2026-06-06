"""Unit tests for Extensions.font_metrics."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.font_metrics import font_metrics_width  # noqa: E402
from PyQt6.QtGui import QFont, QFontMetrics  # noqa: E402


def test_font_metrics_width():
    fm = QFontMetrics(QFont())
    assert font_metrics_width(fm, "0000") > 0
