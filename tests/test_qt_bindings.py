"""Fast, headless unit tests for the qt_bindings compatibility layer.

These don't need a running event loop; they assert the PyQt4->PyQt6 shims
(enum flattening, file-dialog return normalization, helpers) behave as the
legacy code expects.
"""

import os
import sys

import pytest

# Headless: a QApplication is created on import of some Qt pieces.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions import qt_bindings as qb  # noqa: E402
from Extensions.qt_bindings import QtCore, QtGui, QtWidgets  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app


# --- file dialog return normalization --------------------------------------

@pytest.mark.parametrize("value,expected", [
    (("/tmp/file.py", "All Files (*)"), "/tmp/file.py"),
    (("", "All Files (*)"), None),
    ("/tmp/legacy.py", "/tmp/legacy.py"),
    ("", None),
    (None, None),
])
def test_file_dialog_path(value, expected):
    assert qb.file_dialog_path(value) == expected


def test_file_dialog_paths():
    assert qb.file_dialog_paths((["a.py", "b.py"], "filter")) == ["a.py", "b.py"]
    assert qb.file_dialog_paths(([], "filter")) == []
    assert qb.file_dialog_paths(None) == []


# --- enum flattening (PyQt4 flat names re-exposed on Qt6 scoped enums) ------

def test_mouse_button_flattening():
    assert QtCore.Qt.LeftButton == QtCore.Qt.MouseButton.LeftButton
    assert QtCore.Qt.MiddleButton == QtCore.Qt.MouseButton.MiddleButton
    # MidButton was the removed Qt4/5 alias.
    assert QtCore.Qt.MidButton == QtCore.Qt.MouseButton.MiddleButton


def test_filedialog_option_flattening():
    fd = QtWidgets.QFileDialog
    assert fd.ShowDirsOnly == fd.Option.ShowDirsOnly
    assert fd.DontResolveSymlinks == fd.Option.DontResolveSymlinks
    # The combination the open/browse handlers build must not raise.
    assert (fd.ShowDirsOnly | fd.DontResolveSymlinks) is not None


def test_keysequence_and_iodevice_and_dir():
    assert QtGui.QKeySequence.Copy == QtGui.QKeySequence.StandardKey.Copy
    assert QtCore.QIODevice.ReadWrite == QtCore.QIODevice.OpenModeFlag.ReadWrite
    assert QtCore.QDir.Files == QtCore.QDir.Filter.Files


def test_qfiledialog_options_shim_returns_empty_option():
    # PyQt4 code calls QFileDialog.Options(); the shim returns an empty Option.
    opts = QtWidgets.QFileDialog.Options()
    assert isinstance(opts, QtWidgets.QFileDialog.Option)


def test_qscintilla_enum_flattening():
    pytest.importorskip("PyQt6.Qsci")
    from PyQt6.Qsci import QsciScintilla
    # Flattened scoped enums used with integer-style access in legacy code.
    assert hasattr(QsciScintilla, "PlainIndicator")
    assert hasattr(QsciScintilla, "WrapWord") or hasattr(QsciScintilla, "WrapNone")


# --- helper functions -------------------------------------------------------

def test_primary_screen_geometry():
    geo = qb.primary_screen_geometry()
    assert geo.width() > 0 and geo.height() > 0


def test_font_metrics_width_reexport():
    """Shim re-exports font_metrics_width for legacy tooling."""
    fm = QtGui.QFontMetrics(QtGui.QFont())
    assert qb.font_metrics_width(fm, "0000") > 0
