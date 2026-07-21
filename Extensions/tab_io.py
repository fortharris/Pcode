"""File read/write helpers for editor tabs."""

import logging
import os
import sys
import traceback

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox


def write_editor_to_path(editor, path, encoding=None):
    """Write editor text to path.

    Returns ``(ok, used_encoding)`` where ``ok`` is True on success.
    Falls back to utf-8 if the requested encoding cannot encode the text.
    """
    requested = encoding or "utf-8"
    used = requested
    try:
        try:
            with open(path, "w", encoding=requested) as file:
                file.write(editor.text())
        except (UnicodeEncodeError, LookupError):
            used = "utf-8"
            with open(path, "w", encoding=used) as file:
                file.write(editor.text())
            logging.warning(
                "Could not encode %s as %s; saved as utf-8", path, requested)
        editor.setModified(False)
        return True, used
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        return False, requested


def open_file_in_tab(editor_tab, file_path, show_error=True, index=None):
    """Open a file into editor_tab. Returns True on success."""
    file_path = os.path.normpath(file_path)
    if editor_tab.alreadyOpened(file_path):
        return True

    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    try:
        text, encoding, eol_mode = editor_tab.useData.readFile(file_path)
        base_name = os.path.basename(file_path)
        sub_stack = editor_tab.newEditor(index, base_name, file_path, encoding)

        editor = sub_stack.widget(0).getEditor(0)
        editor.setText(text)
        editor.convertEols(eol_mode)
        editor.setEolMode(eol_mode)

        snapshot_widget = sub_stack.widget(1)
        snapshot_widget.setText(text)
        snapshot_widget.convertEols(eol_mode)
        snapshot_widget.setEolMode(eol_mode)
    except Exception as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        QApplication.restoreOverrideCursor()
        if show_error:
            QMessageBox.warning(editor_tab, "Open", str(err))
        return False

    QApplication.restoreOverrideCursor()
    editor.setModified(False)
    editor.setFocus()
    editor_tab.updateRecentFilesList.emit(file_path)
    editor_tab.updateOpenedTabsMenu()
    return True
