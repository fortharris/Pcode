"""Unit tests for cx_Freeze build path discovery."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.Projects.ProjectManager.Build import BuildThread  # noqa: E402


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
