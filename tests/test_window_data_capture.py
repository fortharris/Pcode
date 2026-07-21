"""Tests for WindowData capture/apply with minimal Qt widgets."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QSplitter, QWidget  # noqa: E402
from Extensions.WindowData import (  # noqa: E402
    LAYOUT_VERSION,
    capture,
    apply,
    save,
    load,
)


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance() or QApplication([])
    yield instance


class _FakeWritePad(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(10, 20, 300, 150)


class _FakeEditorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.hSplitter = QSplitter()
        self.vSplitter = QSplitter()
        self.sideSplitter = QSplitter()
        self.writePad = _FakeWritePad()


def test_capture_apply_roundtrip(app, tmp_path):
    win = _FakeEditorWindow()
    data = capture(win)
    assert data["writepad"] == [10, 20, 300, 150]
    assert data["version"] == LAYOUT_VERSION

    win2 = _FakeEditorWindow()
    win2.writePad.setGeometry(0, 0, 100, 100)
    apply(win2, data)
    assert win2.writePad.geometry().getRect() == (10, 20, 300, 150)

    save(str(tmp_path), data)
    loaded = load(str(tmp_path))
    assert loaded["writepad"] == data["writepad"]
