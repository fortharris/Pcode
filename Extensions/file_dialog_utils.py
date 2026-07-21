"""Normalize PyQt6 QFileDialog return values (tuple in Qt6, str in PyQt4)."""

import os
import subprocess
import sys


def reveal_in_file_manager(path):
    """Reveal a file or folder in the system file manager (cross-platform)."""
    if not path:
        return False
    path = os.path.normpath(path)
    try:
        if sys.platform == "win32":
            if os.path.isdir(path):
                os.startfile(path)  # noqa: S606 — intentional shell open
            elif os.path.isfile(path):
                subprocess.Popen(
                    ["explorer", "/n,/select,", path],
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            else:
                parent = os.path.dirname(path)
                if os.path.isdir(parent):
                    os.startfile(parent)  # noqa: S606
                else:
                    return False
            return True
        if sys.platform == "darwin":
            if os.path.isfile(path):
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["open", path])
            return True
        # Linux / other Unix
        target = path if os.path.exists(path) else os.path.dirname(path)
        if not target:
            return False
        subprocess.Popen(["xdg-open", target])
        return True
    except Exception:
        return False


def file_dialog_path(result):
    """Return a single path from getOpenFileName / getSaveFileName / getExistingDirectory."""
    if result is None:
        return None
    if isinstance(result, (tuple, list)):
        if not result or not result[0]:
            return None
        return result[0]
    if isinstance(result, str) and not result:
        return None
    return result


def file_dialog_paths(result):
    """Return a list of paths from getOpenFileNames."""
    if result is None:
        return []
    if isinstance(result, (tuple, list)):
        if len(result) >= 1 and isinstance(result[0], (list, tuple)):
            return [p for p in result[0] if p]
        if len(result) >= 1 and isinstance(result[0], str):
            return [result[0]] if result[0] else []
        return [p for p in result if isinstance(p, str) and p]
    return [result] if result else []
