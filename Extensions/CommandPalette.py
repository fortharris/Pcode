"""A lightweight command palette (Ctrl+Shift+P) action launcher."""

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout,
)


class CommandPalette(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.resize(560, 360)

        self._commands = []

        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.searchLine = QLineEdit()
        self.searchLine.setPlaceholderText("Type a command\u2026")
        self.searchLine.setClearButtonEnabled(True)
        self.searchLine.textChanged.connect(self._refilter)
        self.searchLine.installEventFilter(self)
        layout.addWidget(self.searchLine)

        self.listWidget = QListWidget()
        self.listWidget.itemActivated.connect(self._activate)
        layout.addWidget(self.listWidget)

    def setCommands(self, commands):
        """commands: iterable of (label, callback)."""
        self._commands = list(commands)

    def launch(self):
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
        text = text.strip().lower()
        self.listWidget.clear()
        for label, callback in self._commands:
            if self._matches(text, label.lower()):
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, callback)
                self.listWidget.addItem(item)
        if self.listWidget.count():
            self.listWidget.setCurrentRow(0)

    @staticmethod
    def _matches(query, label):
        if not query:
            return True
        pos = 0
        for ch in query:
            pos = label.find(ch, pos)
            if pos == -1:
                return False
            pos += 1
        return True

    def _activate(self, item):
        callback = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        if callable(callback):
            callback()

    def _moveSelection(self, delta):
        count = self.listWidget.count()
        if not count:
            return
        row = self.listWidget.currentRow()
        row = max(0, min(count - 1, row + delta))
        self.listWidget.setCurrentRow(row)

    def eventFilter(self, obj, event):
        if obj is self.searchLine and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Down:
                self._moveSelection(1)
                return True
            if key == Qt.Key.Key_Up:
                self._moveSelection(-1)
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                item = self.listWidget.currentItem()
                if item is not None:
                    self._activate(item)
                return True
            if key == Qt.Key.Key_Escape:
                self.reject()
                return True
        return QDialog.eventFilter(self, obj, event)
