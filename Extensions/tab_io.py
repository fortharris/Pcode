"""File read/write helpers for editor tabs."""

import logging
import os
import sys
import traceback


def write_editor_to_path(editor, path):
    """Write editor text to path. Returns True on success."""
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(editor.text())
        editor.setModified(False)
        return True
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        return False


def read_file_for_editor(use_data, file_path):
    """Return (text, encoding, eol_mode) for opening a file in the editor."""
    file_path = os.path.normpath(file_path)
    return use_data.readFile(file_path), file_path
