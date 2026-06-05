"""Tests for session_restore.apply logic."""

import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.session_restore import restore_entries  # noqa: E402


def test_restore_entries_skips_failed_loads():
    editor_tab = MagicMock()
    editor_tab.loadfile.return_value = False
    editor_tab.count.return_value = 0

    restored = restore_entries(
        editor_tab,
        [{"path": "/missing.py", "active": False, "locked": False}],
        backup=False,
    )

    assert restored == 0
    editor_tab._newPythonFile.assert_called_once()


def test_restore_entries_sets_active_tab():
    editor_tab = MagicMock()
    editor_tab.loadfile.return_value = True
    editor_tab.count.return_value = 2
    editor = MagicMock()
    editor_tab.getEditor.return_value = editor

    restore_entries(
        editor_tab,
        [
            {"path": "/a.py", "active": False, "locked": False,
             "cursorPosition": "1,0", "firstVisibleLine": 0,
             "bookmarks": "", "folds": ""},
            {"path": "/b.py", "active": True, "locked": False,
             "cursorPosition": "2,0", "firstVisibleLine": 1,
             "bookmarks": "", "folds": ""},
        ],
        backup=False,
    )

    editor_tab.setCurrentIndex.assert_called_once_with(1)
