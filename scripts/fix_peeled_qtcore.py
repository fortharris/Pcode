#!/usr/bin/env python3
"""Post-process files after peel_pyqt6_file.py when PyQt6.Qsci blocked import insertion."""

import re
import sys

REPLACEMENTS = [
    (r"\bQtCore\.Signal\b", "pyqtSignal"),
    (r"\bQtCore\.QThread\b", "QThread"),
    (r"\bQtCore\.QTimer\b", "QTimer"),
    (r"\bQtCore\.QFileSystemWatcher\b", "QFileSystemWatcher"),
    (r"\bQtCore\.QPointF\b", "QPointF"),
    (r"\bQtCore\.QPoint\b", "QPoint"),
    (r"\bQtCore\.QDateTime\b", "QDateTime"),
    (r"\bQtCore\.QFileInfo\b", "QFileInfo"),
    (r"\bQtCore\.QEvent\.Type\.", "QEvent.Type."),
    (r"\bQtCore\.QEvent\.KeyPress\b", "QEvent.Type.KeyPress"),
    (r"\bQtCore\.Qt\.TextElideMode\.ElideRight\b", "Qt.TextElideMode.ElideRight"),
    (r"\bQtCore\.Qt\.Vertical\b", "Qt.Orientation.Vertical"),
    (r"\bQtCore\.Qt\.Horizontal\b", "Qt.Orientation.Horizontal"),
    (r"\bQtCore\.Qt\.WindowCloseButtonHint\b", "Qt.WindowType.WindowCloseButtonHint"),
    (r"\bQtCore\.Qt\.Window\b", "Qt.WindowType.Window"),
    (r"\bQtCore\.Qt\.WaitCursor\b", "Qt.CursorShape.WaitCursor"),
    (r"\bQtCore\.Qt\.CopyAction\b", "Qt.DropAction.CopyAction"),
    (r"\bQtCore\.Qt\.MatchCaseSensitive\b", "Qt.MatchFlag.MatchCaseSensitive"),
    (r"\bQtCore\.Qt\.AscendingOrder\b", "Qt.SortOrder.AscendingOrder"),
    (r"\bQtCore\.Qt\.ItemIsEditable\b", "Qt.ItemFlag.ItemIsEditable"),
    (r"\bQtCore\.Qt\.ItemIsSelectable\b", "Qt.ItemFlag.ItemIsSelectable"),
    (r"\bQtCore\.Qt\.ItemIsEnabled\b", "Qt.ItemFlag.ItemIsEnabled"),
    (r"\bQtCore\.Qt\.Key_Control\b", "Qt.Key.Key_Control"),
    (r"\bQtCore\.Qt\.Key_Meta\b", "Qt.Key.Key_Meta"),
    (r"\bQtCore\.Qt\.Key_Shift\b", "Qt.Key.Key_Shift"),
    (r"\bQtCore\.Qt\.Key_Alt\b", "Qt.Key.Key_Alt"),
    (r"\bQtCore\.Qt\.Key_Menu\b", "Qt.Key.Key_Menu"),
    (r"\bQtCore\.Qt\.Key_Backtab\b", "Qt.Key.Key_Backtab"),
    (r"\bQtCore\.Qt\.Key_Tab\b", "Qt.Key.Key_Tab"),
    (r"\bQtCore\.Qt\.ShiftModifier\b", "Qt.KeyboardModifier.ShiftModifier"),
    (r"\bQtCore\.Qt\.ControlModifier\b", "Qt.KeyboardModifier.ControlModifier"),
    (r"\bQtCore\.Qt\.AltModifier\b", "Qt.KeyboardModifier.AltModifier"),
    (r"\bQtCore\.Qt\.MetaModifier\b", "Qt.KeyboardModifier.MetaModifier"),
    (r"\bQtCore\.Qt\.SHIFT\b", "int(Qt.KeyboardModifier.ShiftModifier)"),
    (r"\bQtCore\.Qt\.CTRL\b", "int(Qt.KeyboardModifier.ControlModifier)"),
    (r"\bQtCore\.Qt\.ALT\b", "int(Qt.KeyboardModifier.AltModifier)"),
    (r"\bQtCore\.Qt\.META\b", "int(Qt.KeyboardModifier.MetaModifier)"),
    (r"\bQtCore\.Qt\.MidButton\b", "Qt.MouseButton.MiddleButton"),
    (r"\bQtCore\.Qt\.MiddleButton\b", "Qt.MouseButton.MiddleButton"),
    (r"\bQtGui\.QFont\b", "QFont"),
    (r"\bQtGui\.QFontMetrics\b", "QFontMetrics"),
    (r"\bQtGui\.QToolTip\b", "QToolTip"),
    (r"\bQtGui\.QTextEdit\b", "QTextEdit"),
    (r"\bQtGui\.QGroupBox\b", "QGroupBox"),
    (r"\bQtGui\.QSpinBox\b", "QSpinBox"),
    (r"\bQtGui\.QButtonGroup\b", "QButtonGroup"),
    (r"\bQtGui\.QRadioButton\b", "QRadioButton"),
    (r"\bQtGui\.QStackedLayout\b", "QStackedLayout"),
    (r"\bQtGui\.QFontDialog\b", "QFontDialog"),
    (r"\bQtGui\.QFileIconProvider\b", "QFileIconProvider"),
    (r"\bQMessageBox\.Yes\b", "QMessageBox.StandardButton.Yes"),
    (r"\bQMessageBox\.No\b", "QMessageBox.StandardButton.No"),
    (r"\bQMessageBox\.Save\b", "QMessageBox.StandardButton.Save"),
    (r"\bQMessageBox\.Discard\b", "QMessageBox.StandardButton.Discard"),
    (r"\bQMessageBox\.Cancel\b", "QMessageBox.StandardButton.Cancel"),
    (r"\bQDialog\.Accepted\b", "QDialog.DialogCode.Accepted"),
    (r"from Extensions\.qt_bindings import QtCore, QtGui, QtXml\n", ""),
    (r"from Extensions\.qt_bindings import QtCore, QtGui\n", ""),
    (r"from Extensions\.qt_bindings import QtGui, QtCore\n", ""),
    (r"from Extensions\.qt_bindings import QtGui\n", ""),
    (r"from Extensions\.qt_bindings import font_metrics_width,\s*QtCore, QtGui\n",
     "from Extensions.qt_bindings import font_metrics_width\n"),
    (r"from Extensions\.qt_bindings import font_metrics_width, QtGui, QtCore\n",
     "from Extensions.qt_bindings import font_metrics_width\n"),
    (r"from Extensions\.qt_bindings import QtGui, QtCore, QtXml\n", ""),
    (r"from Extensions\.qt_bindings import QtCore, QtGui, QtXml\n", ""),
    (r"\bQtXml\.QDomDocument\b", "QDomDocument"),
    (r"\bQtCore\.QDir\b", "QDir"),
    (r"\bQtCore\.QUrl\b", "QUrl"),
    (r"\bQtCore\.QMimeData\b", "QMimeData"),
    (r"\bQtGui\.QFrame\b", "QFrame"),
    (r"\bQtGui\.QMainWindow\b", "QMainWindow"),
    (r"\bQtGui\.QPlainTextEdit\b", "QPlainTextEdit"),
    (r"\bQtGui\.QProgressBar\b", "QProgressBar"),
    (r"\bQtCore\.Qt\.ToolButtonTextBesideIcon\b",
     "Qt.ToolButtonStyle.ToolButtonTextBesideIcon"),
    (r"\bQtCore\.Qt\.MatchStartsWith\b", "Qt.MatchFlag.MatchStartsWith"),
    (r"\bQtCore\.Qt\.MatchRecursive\b", "Qt.MatchFlag.MatchRecursive"),
    (r"\bQtCore\.Qt\.Key_Up\b", "Qt.Key.Key_Up"),
    (r"\bQtCore\.Qt\.Key_Down\b", "Qt.Key.Key_Down"),
    (r"\bQtCore\.Qt\.NoItemFlags\b", "Qt.ItemFlag.NoItemFlags"),
    (r"\bQtGui\.QFrame\.HLine\b", "QFrame.Shape.HLine"),
    (r"\bQtGui\.QFrame\.Sunken\b", "QFrame.Shadow.Sunken"),
]

CORE_IMPORT = (
    "from PyQt6.QtCore import "
    "QDateTime, QDir, QEvent, QFileInfo, QFileSystemWatcher, QMimeData, "
    "QPoint, QPointF, Qt, QThread, QTimer, QUrl, pyqtSignal\n"
)
GUI_IMPORT = (
    "from PyQt6.QtGui import "
    "QAction, QActionGroup, QBrush, QColor, QFont, QFontMetrics, "
    "QIcon, QKeySequence, QFileIconProvider, QShortcut, QToolTip\n"
)
WIDGETS_IMPORT = (
    "from PyQt6.QtWidgets import QApplication, QButtonGroup, QCheckBox, "
    "QComboBox, QDialog, QFileDialog, QFontDialog, QFormLayout, QFrame, "
    "QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, "
    "QMainWindow, QMenu, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, "
    "QRadioButton, QSpinBox, QStackedLayout, QStackedWidget, QTabWidget, "
    "QTextEdit, QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget\n"
)
XML_IMPORT = "from PyQt6.QtXml import QDomDocument\n"


def needs_qt_imports(text):
    return (
        "pyqtSignal" in text or "QThread" in text or "QTabWidget" in text
        or "QMessageBox" in text or "QFont(" in text
    )


def insert_imports(text):
    if "from PyQt6.QtCore import" in text and "pyqtSignal" in text:
        return text
    if not needs_qt_imports(text):
        return text
    block = CORE_IMPORT + GUI_IMPORT
    if any(x in text for x in ("QTabWidget", "QMessageBox", "QDialog", "QTreeWidget")):
        block += WIDGETS_IMPORT
    if "QDomDocument" in text or "QtXml" in text:
        block += XML_IMPORT
    lines = text.splitlines(keepends=True)
    idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            idx = i + 1
    lines.insert(idx, block)
    return "".join(lines)


def fix(path):
    text = open(path, encoding="utf-8").read()
    for pattern, repl in REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    if "QtCore." in text or "QtGui." in text:
        text = insert_imports(text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("fixed", path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        fix(p)
