"""Smoke tests for PyQt6 scoped enums used in production code."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QDir, QIODevice, Qt  # noqa: E402
from PyQt6.QtGui import QKeySequence  # noqa: E402
from PyQt6.QtWidgets import QFileDialog  # noqa: E402


def test_mouse_button_enums():
    assert Qt.MouseButton.LeftButton == Qt.MouseButton.LeftButton
    assert Qt.MouseButton.MiddleButton == Qt.MouseButton.MiddleButton


def test_filedialog_option_enums():
    options = (QFileDialog.Option.DontResolveSymlinks
               | QFileDialog.Option.ShowDirsOnly)
    assert QFileDialog.AcceptMode.AcceptOpen is not None
    assert options is not None


def test_keysequence_and_iodevice_and_dir():
    assert QKeySequence.StandardKey.Copy == QKeySequence.StandardKey.Copy
    assert QIODevice.OpenModeFlag.ReadWrite == QIODevice.OpenModeFlag.ReadWrite
    assert QDir.Filter.Files == QDir.Filter.Files


def test_qscintilla_enum_access():
    pytest.importorskip("PyQt6.Qsci")
    import Extensions.qscintilla_compat  # noqa: F401
    from PyQt6.Qsci import QsciScintilla
    assert hasattr(QsciScintilla, "WrapWord")
    assert hasattr(QsciScintilla, "WrapMode")
