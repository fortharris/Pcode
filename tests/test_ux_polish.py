"""Tests for UX polish helpers."""

from pathlib import Path

from Extensions.Workspace import ensure_workspace_dirs, looks_like_workspace
from Extensions.file_dialog_utils import reveal_in_file_manager


def test_split_defaults_not_f10_f11():
    src = Path("Extensions/UseData.py").read_text(encoding="utf-8")
    assert '"Split-Horizontal": "Ctrl+Alt+H"' in src
    assert '"Remove-Split": "Ctrl+Alt+U"' in src
    assert '"Split-Horizontal": "F10"' not in src
    assert '"Remove-Split": "F11"' not in src
    assert '"Command-Palette": "Ctrl+Shift+P"' in src
    assert '"Quick-Open": "Ctrl+P"' in src
    assert '"Debug-Continue": "F5"' in src


def test_looks_like_workspace(tmp_path):
    assert not looks_like_workspace(str(tmp_path))
    pcode = tmp_path / "PcodeProjects"
    pcode.mkdir()
    assert looks_like_workspace(str(pcode))
    other = tmp_path / "myws"
    other.mkdir()
    (other / "Projects").mkdir()
    (other / "Settings").mkdir()
    assert looks_like_workspace(str(other))


def test_ensure_workspace_dirs(tmp_path):
    root = tmp_path / "ws"
    root.mkdir()
    ensure_workspace_dirs(str(root))
    assert (root / "Projects").is_dir()
    assert (root / "Settings").is_dir()


def test_reveal_helper_importable():
    assert callable(reveal_in_file_manager)
