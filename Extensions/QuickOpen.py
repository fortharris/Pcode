"""Quick Open: fuzzy project file finder (Ctrl+P)."""

from __future__ import annotations

import os

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout,
)

_SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "venv", ".pcode-venv",
    "node_modules", ".tox", ".mypy_cache", ".pytest_cache",
    "Rope", "Build",
}
_SKIP_SUFFIXES = (".pyc", ".pyo", ".pyd", ".exe", ".dll", ".so")
_MAX_FILES = 5000


def fuzzy_matches(query, label):
    """Subsequence match used by Quick Open and tests."""
    if not query:
        return True
    tokens = query.split()
    if not tokens:
        return True
    for token in tokens:
        pos = 0
        for ch in token:
            pos = label.find(ch, pos)
            if pos == -1:
                return False
            pos += 1
    return True


def index_project_files(root, max_files=_MAX_FILES):
    """Return list of (relative_path, absolute_path) under root."""
    results = []
    if not root or not os.path.isdir(root):
        return results
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in _SKIP_DIRS and not d.startswith(".")
        ]
        for name in filenames:
            if name.startswith("."):
                continue
            if name.endswith(_SKIP_SUFFIXES):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            results.append((rel.replace("\\", "/"), full))
            if len(results) >= max_files:
                return results
    return results


class QuickOpen(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.resize(560, 400)
        self.setAccessibleName("Quick Open")

        self._files = []
        self._on_open = None

        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.searchLine = QLineEdit()
        self.searchLine.setPlaceholderText("Go to file\u2026")
        self.searchLine.setClearButtonEnabled(True)
        self.searchLine.setAccessibleName("Quick Open search")
        self.searchLine.textChanged.connect(self._refilter)
        self.searchLine.installEventFilter(self)
        layout.addWidget(self.searchLine)

        self.listWidget = QListWidget()
        self.listWidget.setAccessibleName("Quick Open results")
        self.listWidget.itemActivated.connect(self._activate)
        layout.addWidget(self.listWidget)

    def launch(self, files, on_open):
        """files: iterable of (rel, abs). on_open(abs_path)."""
        self._files = list(files)
        self._on_open = on_open
        self.searchLine.clear()
        self._refilter("")
        if self.parent() is not None:
            geo = self.parent().geometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + max(40, geo.height() // 6)
            self.move(x, y)
        self.searchLine.setFocus()
        self.show()
        self.raise_()

    def _refilter(self, text):
        query = text.strip().lower()
        self.listWidget.clear()
        count = 0
        for rel, full in self._files:
            if fuzzy_matches(query, rel.lower()):
                item = QListWidgetItem(rel)
                item.setData(Qt.ItemDataRole.UserRole, full)
                item.setToolTip(full)
                self.listWidget.addItem(item)
                count += 1
                if count >= 200:
                    break
        if self.listWidget.count():
            self.listWidget.setCurrentRow(0)

    def _activate(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.hide()
        if path and self._on_open is not None:
            self._on_open(path)

    def eventFilter(self, obj, event):
        if obj is self.searchLine and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                row = self.listWidget.currentRow()
                if key == Qt.Key.Key_Down:
                    row = min(row + 1, self.listWidget.count() - 1)
                else:
                    row = max(row - 1, 0)
                self.listWidget.setCurrentRow(row)
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                item = self.listWidget.currentItem()
                if item is not None:
                    self._activate(item)
                return True
            if key == Qt.Key.Key_Escape:
                self.hide()
                return True
        return QDialog.eventFilter(self, obj, event)
