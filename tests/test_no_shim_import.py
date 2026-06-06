"""Guard: production imports must work without loading qt_bindings first."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    QMessageBox.warning = staticmethod(lambda *a, **k: None)
    QMessageBox.critical = staticmethod(lambda *a, **k: None)
    return instance


def test_pcode_imports_without_qt_bindings(app):
    from Pcode import Pcode  # noqa: F401


def test_editor_stack_imports_without_qt_bindings(app):
    from Extensions.Start import Start  # noqa: F401
    from Extensions.Library.AdvancedSearch import AdvancedSearch  # noqa: F401
    from Extensions.CodeEditor import CodeEditor  # noqa: F401
