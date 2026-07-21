"""Unit tests for cx_Freeze build path discovery."""

import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.Projects.ProjectManager.Build import BuildThread  # noqa: E402
from Extensions.python_paths import venv_search_paths  # noqa: E402


def test_interpreter_search_paths_skips_missing_dirs(tmp_path):
    thread = BuildThread.__new__(BuildThread)
    thread.projectPathDict = {"sourcedir": str(tmp_path / "src")}
    (tmp_path / "src").mkdir()

    paths = thread._interpreter_search_paths(sys.executable)

    assert str(tmp_path / "src") in paths
    assert all(os.path.isdir(p) for p in paths)
    assert not any(p.endswith(os.path.join("Scripts", "DLLs")) for p in paths)


def test_path_list_from_dir_missing_path():
    thread = BuildThread.__new__(BuildThread)
    assert thread.pathListFromDir("/nonexistent/pcode/path") == []


def test_venv_search_paths_used_for_use_virtual_env(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    venv = tmp_path / "Venv"
    if sys.platform == "win32":
        (venv / "Scripts").mkdir(parents=True)
        (venv / "Lib" / "site-packages").mkdir(parents=True)
    else:
        (venv / "bin").mkdir(parents=True)
        (venv / "lib" / "python{0}.{1}".format(
            sys.version_info.major, sys.version_info.minor) / "site-packages").mkdir(
            parents=True)
    paths = venv_search_paths(str(venv), sourcedir=str(src))
    assert all(os.path.isdir(p) for p in paths)
    assert any("site-packages" in p for p in paths)
    assert os.path.normpath(str(src)) in [os.path.normpath(p) for p in paths]
