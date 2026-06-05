"""Small Qt screen helpers (extracted from qt_bindings)."""

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication


def primary_screen_geometry(app=None):
    """Replacement for QDesktopWidget().screenGeometry()."""
    if app is None:
        app = QApplication.instance()
    if app is None:
        return QRect(0, 0, 1024, 768)
    screen = app.primaryScreen()
    if screen is None:
        return QRect(0, 0, 1024, 768)
    return screen.geometry()
