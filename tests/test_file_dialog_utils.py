"""Tests for Extensions.file_dialog_utils."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.file_dialog_utils import file_dialog_path, file_dialog_paths  # noqa: E402


@pytest.mark.parametrize("value,expected", [
    (("/tmp/file.py", "All Files (*)"), "/tmp/file.py"),
    (("", "All Files (*)"), None),
    ("/tmp/legacy.py", "/tmp/legacy.py"),
    ("", None),
    (None, None),
])
def test_file_dialog_path(value, expected):
    assert file_dialog_path(value) == expected


def test_file_dialog_paths():
    assert file_dialog_paths((["a.py", "b.py"], "filter")) == ["a.py", "b.py"]
    assert file_dialog_paths(([], "filter")) == []
    assert file_dialog_paths(None) == []
