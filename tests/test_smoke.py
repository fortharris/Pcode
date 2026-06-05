"""Headless UI smoke tests (formerly scripts/exercise_editor.py steps)."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util

_smoke_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "exercise_editor.py")
_spec = importlib.util.spec_from_file_location("exercise_editor", _smoke_path)
smoke = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(smoke)

pytestmark = pytest.mark.smoke


@pytest.fixture(scope="module")
def session():
    win = smoke.Pcode()
    projects_dir = os.path.abspath(win.useData.appPathDict["projectsdir"])
    os.makedirs(projects_dir, exist_ok=True)
    proj_path = smoke.make_project(projects_dir)
    win.loadProject(proj_path, show=True, new=True)

    editor_window = None
    for i in range(win.projectWindowStack.count()):
        w = win.projectWindowStack.widget(i)
        if hasattr(w, "editorTabWidget"):
            editor_window = w
            break
    assert editor_window is not None

    etw = editor_window.editorTabWidget
    editor = etw.getEditor() if hasattr(etw, "getEditor") else None
    if editor is not None:
        editor.setText("x = 1\n")

    yield win, editor_window, etw, editor, proj_path


def test_main_window(session):
    win, *_ = session
    assert win.windowTitle()


def test_save(session):
    smoke.exercise_save(session[2])


def test_run(session):
    smoke.exercise_run(session[1], session[0], session[4])


def test_completion(session):
    smoke.exercise_completion(session[3])


def test_find_replace(session):
    smoke.exercise_find_replace(session[1])


def test_find_in_files(session):
    smoke.exercise_find_in_files(session[1], session[4])


def test_settings(session):
    smoke.exercise_settings(session[0])


def test_library(session):
    smoke.exercise_library(session[0])


def test_project_view(session):
    smoke.exercise_project_view(session[1])


def test_rope_rename(session):
    smoke.exercise_rope_rename(session[1], session[4])


def test_snippets(session):
    smoke.exercise_snippets(session[0])


def test_export(session):
    projects_dir = os.path.abspath(session[0].useData.appPathDict["projectsdir"])
    smoke.exercise_export(session[4], projects_dir)


def test_filedialog_enums():
    smoke.exercise_filedialog_enums()


def test_mouse_events(session):
    smoke.exercise_mouse_events(session[3], session[1])


def test_command_palette(session):
    smoke.exercise_command_palette(session[0])


def test_themes(session):
    smoke.exercise_themes(session[0])


def test_about(session):
    smoke.exercise_about(session[0])


def test_assistant(session):
    smoke.exercise_assistant(session[1], session[2])


def test_tasks(session):
    smoke.exercise_tasks(session[1], session[2])


def test_profiler(session):
    smoke.exercise_profiler(session[1])


def test_diff(session):
    smoke.exercise_diff(session[2])


def test_color_scheme(session):
    smoke.exercise_color_scheme(session[0])


def test_build_profile(session):
    smoke.exercise_build_profile(session[1])


@pytest.mark.slow
def test_build_freeze(session):
    if os.environ.get("PCODE_SKIP_BUILD") == "1":
        pytest.skip("PCODE_SKIP_BUILD=1")
    smoke.exercise_build_freeze(session[1], session[0])


def test_outline(session):
    smoke.exercise_outline(session[1])


def test_file_explorer(session):
    smoke.exercise_file_explorer(session[1])


def test_bookmarks(session):
    smoke.exercise_bookmarks(session[1], session[2])


def test_git_panel(session):
    smoke.exercise_git_panel(session[1])


def test_go_to_definition(session):
    smoke.exercise_go_to_definition(session[1], session[4])
