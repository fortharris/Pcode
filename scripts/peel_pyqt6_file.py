#!/usr/bin/env python3
"""One-off helper: replace qt_bindings QtGui widget refs with direct PyQt6 imports."""

import re
import sys

WIDGETS = [
    "QWidget", "QVBoxLayout", "QHBoxLayout", "QSplitter", "QStackedWidget",
    "QToolBar", "QTabWidget", "QMenu", "QStatusBar", "QToolButton", "QLabel",
    "QMessageBox", "QApplication", "QFileDialog", "QComboBox", "QDialog",
    "QFormLayout", "QLineEdit", "QPushButton", "QCheckBox", "QTreeWidget",
    "QTreeWidgetItem", "QListWidget", "QListWidgetItem", "QTreeView",
    "QFileSystemModel", "QStyledItemDelegate", "QPrintDialog", "QPrinter",
]

GUI = [
    "QAction", "QActionGroup", "QIcon", "QDesktopServices", "QPalette",
    "QBrush", "QColor", "QPixmap", "QKeySequence", "QShortcut",
]

IMPORT_WIDGETS = sorted(set(WIDGETS))
IMPORT_GUI = sorted(set(GUI))


def peel(path):
    text = open(path, encoding="utf-8").read()
    text = re.sub(
        r"from Extensions\.qt_bindings import QtCore, QtGui\n", "", text)
    text = re.sub(
        r"from Extensions\.qt_bindings import QtGui, QtCore\n", "", text)

    for name in WIDGETS:
        text = text.replace(f"QtGui.{name}", name)
    for name in GUI:
        text = text.replace(f"QtGui.{name}", name)

    if "from PyQt6" not in text:
        header = (
            "from PyQt6 import QtCore\n"
            "from PyQt6.QtGui import {gui}\n"
            "from PyQt6.QtWidgets import {widgets}\n\n"
        ).format(gui=", ".join(IMPORT_GUI), widgets=", ".join(IMPORT_WIDGETS))
        # insert after module docstring / first imports
        lines = text.splitlines(keepends=True)
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i
                break
            if line.strip() and not line.startswith('"""') and '"""' not in line:
                insert_at = i
                break
        lines.insert(insert_at, header)
        text = "".join(lines)

    open(path, "w", encoding="utf-8").write(text)
    print("peeled", path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        peel(p)
