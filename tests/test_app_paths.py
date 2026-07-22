"""Tests for frozen/source app path helpers."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.app_paths import get_app_root, get_default_workspace_dir, is_frozen


def test_is_frozen_false_in_source():
    assert is_frozen() is False


def test_get_app_root_is_repo():
    root = get_app_root()
    assert os.path.isdir(os.path.join(root, "Resources"))
    assert os.path.isfile(os.path.join(root, "Pcode.py"))


def test_default_workspace_under_repo_in_source():
    ws = get_default_workspace_dir()
    assert ws.endswith(os.path.join("workspace", "PcodeProjects"))
    assert ws.startswith(get_app_root())
