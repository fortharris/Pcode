"""Regression: opening a project must not fail on editor tab creation."""

import importlib.util
import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

_exercise_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "exercise_editor.py")
_spec = importlib.util.spec_from_file_location("exercise_editor_helper", _exercise_path)
_exercise = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_exercise)


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    QMessageBox.warning = staticmethod(lambda *a, **k: None)
    QMessageBox.critical = staticmethod(lambda *a, **k: None)
    QMessageBox.information = staticmethod(lambda *a, **k: None)
    from Extensions import ErrorHandler
    ErrorHandler._show_dialog = lambda *a, **k: None
    return instance


def test_open_project_creates_editor_tabs(app):
    from Pcode import Pcode  # noqa: E402

    win = Pcode()
    projects_dir = os.path.abspath(win.useData.appPathDict["projectsdir"])
    os.makedirs(projects_dir, exist_ok=True)
    proj_path = _exercise.make_project(projects_dir)

    win.loadProject(proj_path, show=True, new=True)

    editor_window = None
    for i in range(win.projectWindowStack.count()):
        w = win.projectWindowStack.widget(i)
        if hasattr(w, "editorTabWidget"):
            editor_window = w
            break
    assert editor_window is not None
    assert editor_window.editorTabWidget.count() >= 1
    from Extensions.Diff import DiffWindow  # noqa: E402
    diff = editor_window.editorTabWidget.getUnifiedDiff()
    assert isinstance(diff, DiffWindow)
