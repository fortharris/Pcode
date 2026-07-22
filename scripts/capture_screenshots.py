"""Capture release screenshots into docs/screens/{1,2,3}.png.

Runs with QT_QPA_PLATFORM=offscreen (widget.grab still works).
"""

from __future__ import annotations

import os
import shutil
import sys
import warnings

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import Extensions.qscintilla_compat  # noqa: E402, F401

from PyQt6.QtCore import QSize  # noqa: E402
from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

DEFAULT_SIZE = QSize(1280, 800)

QMessageBox.warning = staticmethod(lambda *a, **k: None)
QMessageBox.critical = staticmethod(lambda *a, **k: None)
QMessageBox.information = staticmethod(lambda *a, **k: None)
QMessageBox.question = staticmethod(lambda *a, **k: None)


def _ensure_app():
    instance = QApplication.instance()
    if instance is None:
        return QApplication(sys.argv)
    return instance


app = _ensure_app()

from Pcode import Pcode  # noqa: E402
from Extensions.Projects.Projects import CreateProjectThread  # noqa: E402


def make_project(projects_dir):
    proj_path = os.path.join(projects_dir, "ScreenshotDemo")
    if os.path.exists(proj_path):
        shutil.rmtree(proj_path)
    thread = CreateProjectThread()
    thread.projDataDict = {
        "location": projects_dir,
        "name": "ScreenshotDemo",
        "type": "Desktop Application",
        "windowtype": "Console",
        "mainscript": "main.py",
        "importdir": "",
    }
    thread.run()
    if thread.error:
        raise RuntimeError("project creation failed: %s" % thread.error)
    main_script = os.path.join(proj_path, "src", "main.py")
    with open(main_script, "w", encoding="utf-8") as f:
        f.write(
            '"""Demo for screenshots."""\n\n'
            "def greet(name: str) -> str:\n"
            "    return f'Hello, {name}!'\n\n"
            "if __name__ == '__main__':\n"
            "    print(greet('Pcode'))\n"
        )
    return proj_path


def save_grab(widget, path, size=None):
    if size is None:
        size = DEFAULT_SIZE
    widget.resize(size)
    widget.show()
    app.processEvents()
    pix = widget.grab()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not pix.save(path, "PNG"):
        raise RuntimeError("failed to save %s" % path)
    print("wrote", path, pix.width(), "x", pix.height())


def main():
    out_dir = os.path.join(ROOT, "docs", "screens")
    win = Pcode()
    win.resize(DEFAULT_SIZE)
    win.show()
    app.processEvents()

    # 1: start / home
    save_grab(win, os.path.join(out_dir, "1.png"))

    projects_dir = os.path.abspath(win.useData.appPathDict["projectsdir"])
    os.makedirs(projects_dir, exist_ok=True)
    proj_path = make_project(projects_dir)
    win.loadProject(proj_path, show=True, new=True)
    app.processEvents()

    # 2: editor with project open
    save_grab(win, os.path.join(out_dir, "2.png"))

    # 3: settings dialog when available
    settings = getattr(win, "settingsWidget", None) or getattr(win, "settings", None)
    if settings is None and hasattr(win, "showSettings"):
        try:
            win.showSettings()
            app.processEvents()
            settings = getattr(win, "settingsWidget", None)
        except Exception:
            settings = None

    if settings is not None:
        settings.resize(QSize(900, 640))
        settings.show()
        app.processEvents()
        save_grab(settings, os.path.join(out_dir, "3.png"), QSize(900, 640))
    else:
        save_grab(win, os.path.join(out_dir, "3.png"))

    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
