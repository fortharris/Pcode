"""Apply and capture persisted editor session entries."""

import logging
import os
import sys
import traceback

from Extensions.settings_utils import to_bool


def capture_entries(editor_tab, backup=False):
    """Build session entry dicts from the current tab widget state."""
    entries = []
    for i in range(editor_tab.count()):
        editor = editor_tab.getEditor(i)
        path = editor_tab.getEditorData("filePath", i)
        if not backup and path is None:
            continue
        line, index = editor.getCursorPosition()
        entry = {
            "path": path,
            "active": editor_tab.currentEditor == editor,
            "locked": editor.isReadOnly(),
            "lines": editor.lines(),
            "cursorPosition": "{0},{1}".format(line, index),
            "firstVisibleLine": editor.firstVisibleLine(),
            "bookmarks": str(editor.getBookmarks()).replace(', ', '-').strip('[]'),
            "folds": str(editor.contractedFolds()).replace(', ', '-').strip('[]'),
        }
        if backup:
            entry["backupKey"] = editor_tab.getEditorData("backupKey", i)
            entry["baseName"] = editor_tab.tabText(i)
        entries.append(entry)
    return entries


def restore_entries(editor_tab, entries, backup=False):
    """Load tabs from session/backup entry dicts. Returns restored backup count."""
    active_index = 0
    current_index = 0
    restored_backups = 0

    for tag in entries:
        try:
            if backup:
                backup_key = tag.get("backupKey", "")
                backup_path = os.path.join(
                    editor_tab.projectPathDict["backupdir"], backup_key)
                real_path = tag.get("path") or ""
                if real_path == '':
                    with open(backup_path, 'r') as file:
                        backup_text = file.read()

                    sub_stack = editor_tab.newEditor(current_index)
                    editor = sub_stack.widget(0).widget(0)
                    editor.setText(backup_text)
                    editor.setModified(False)
                    editor.setFocus()

                    restored_backups += 1
                else:
                    real_mod_time = os.stat(real_path).st_mtime
                    backup_mod_time = os.stat(backup_path).st_mtime
                    if real_mod_time <= backup_mod_time:
                        with open(backup_path, 'r') as file:
                            backup_text = file.read()

                        with open(real_path, "w") as file:
                            file.write(backup_text)

                        restored_backups += 1

                    path = real_path
                    loaded = editor_tab.loadfile(path, False, current_index)
            else:
                path = tag.get("path")
                if not path:
                    continue
                loaded = editor_tab.loadfile(path, False, current_index)
            if loaded is False:
                continue

            if to_bool(tag.get("locked")):
                editor_tab.writeLock()
            if to_bool(tag.get("active")):
                active_index = current_index
            cp = str(tag.get("cursorPosition", "0,0")).split(',')
            line = int(cp[0])
            first_visible_line = int(tag.get("firstVisibleLine", 0))

            editor = editor_tab.getEditor()
            editor.setCursorPosition(line, 0)
            editor.setFirstVisibleLine(first_visible_line)

            m = tag.get("bookmarks") or ""
            if m != '':
                bookmarks = list(map(int, m.split('-')))
                for bline in bookmarks:
                    editor.toggleBookmark(1, bline)

            folds = tag.get("folds") or ""
            if folds != '':
                fold_list = list(map(int, folds.split('-')))
                editor.setContractedFolds(fold_list)

            current_index += 1
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))

    if editor_tab.count() != 0:
        editor_tab.setCurrentIndex(active_index)
    if editor_tab.count() == 0:
        editor_tab._newPythonFile()

    return restored_backups
