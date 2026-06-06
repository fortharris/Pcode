"""File read/write helpers for editor tabs."""

import logging
import os
import sys
import traceback

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox


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
