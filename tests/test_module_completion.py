"""Module Completion settings tab should not crash on empty selection."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QContextMenuEvent
from PyQt6.QtWidgets import QApplication  # noqa: E402

from Extensions.Settings.ModuleCompletion import ModuleCompletion  # noqa: E402


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance() or QApplication([])
    return instance


class _UseData:
    def __init__(self, library_dict=None):
        self.libraryDict = library_dict or {}

    def saveModulesForCompletion(self):
        pass


def test_context_menu_empty_tree_does_not_raise(app, monkeypatch):
    widget = ModuleCompletion(_UseData({}))
    monkeypatch.setattr(widget.contextMenu, "exec", lambda *a, **k: None)

    event = QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse, QPoint(10, 10), QPoint(10, 10))
    widget.contextMenuEvent(event)  # must not raise IndexError

    assert widget.selectedItem is None
    assert widget.addItemAct.isEnabled()
    assert not widget.removeItemAct.isEnabled()
    assert not widget.removeModuleAct.isEnabled()


def test_context_menu_with_modules(app, monkeypatch):
    data = _UseData({"os": [["path", "getcwd"], "True"]})
    widget = ModuleCompletion(data)
    assert widget.topLevelItemCount() == 1
    assert widget.topLevelItem(0).checkState(0) == Qt.CheckState.Checked
    assert widget.topLevelItem(0).childCount() == 2

    monkeypatch.setattr(widget.contextMenu, "exec", lambda *a, **k: None)
    widget.setCurrentItem(widget.topLevelItem(0))
    event = QContextMenuEvent(
        QContextMenuEvent.Reason.Mouse, QPoint(10, 10), QPoint(10, 10))
    widget.contextMenuEvent(event)

    assert widget.selectedItem is not None
    assert widget.removeItemAct.isEnabled()
