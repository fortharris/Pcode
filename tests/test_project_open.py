"""Regression: opening a project must not fail on editor tab creation."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.qt_bindings import QtWidgets  # noqa: E402


@pytest.fixture(scope="module")
def app():
    instance = QtWidgets.QApplication.instance()
    if instance is None:
        instance = QtWidgets.QApplication([])
    QtWidgets.QMessageBox.warning = staticmethod(lambda *a, **k: None)
    QtWidgets.QMessageBox.critical = staticmethod(lambda *a, **k: None)
    return instance


def test_open_project_creates_editor_tabs(app):
    import importlib.util
    import shutil

    from Pcode import Pcode  # noqa: E402

    _path = os.path.join(os.path.dirname(__file__), "..", "scripts", "exercise_editor.py")
    _spec = importlib.util.spec_from_file_location("exercise_editor", _path)
    ex = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(ex)

    win = Pcode()
    projects_dir = os.path.abspath(win.useData.appPathDict["projectsdir"])
    os.makedirs(projects_dir, exist_ok=True)
    proj_path = ex.make_project(projects_dir)

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
