#!/usr/bin/env python3
"""Remove duplicate peel-script import blocks from file headers."""

import re
import sys

PEEL_HEADER = re.compile(
    r"^from PyQt6 import QtCore\n"
    r"from PyQt6\.QtGui import .+\n"
    r"from PyQt6\.QtWidgets import .+\n\n?",
    re.MULTILINE,
)


def cleanup(path):
    text = open(path, encoding="utf-8").read()
    text = PEEL_HEADER.sub("", text, count=1)
    text = text.replace(
        "QMessageBox, QPrintDialog, QPrinter, QPushButton",
        "QMessageBox, QPushButton",
    )
    text = text.replace(
        "from PyQt6.QtCore import QDateTime, QEvent, QFileInfo, QFileSystemWatcher, "
        "QPoint, QPointF, Qt, QThread, QTimer, pyqtSignal\n",
        "from PyQt6.QtCore import QDateTime, QDir, QEvent, QFileInfo, "
        "QFileSystemWatcher, QMimeData, QPoint, QPointF, Qt, QThread, QTimer, "
        "QUrl, pyqtSignal\n",
    )
    text = text.replace(
        "QFontDialog, QFormLayout, QGroupBox, QHBoxLayout",
        "QFontDialog, QFormLayout, QFrame, QGroupBox, QHBoxLayout",
    )
    text = text.replace(
        "QListWidgetItem, QMenu, QMessageBox, QPushButton",
        "QListWidgetItem, QMainWindow, QMenu, QMessageBox, QPlainTextEdit, "
        "QProgressBar, QPushButton",
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("cleaned", path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        cleanup(p)
