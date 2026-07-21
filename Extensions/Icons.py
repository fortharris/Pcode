"""Chrome icon helpers — tint PNGs to match the active UI palette."""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap


def image_path(name):
    """Resolve a Resources/images basename (with or without extension)."""
    if os.path.isabs(name) or os.path.sep in name or "/" in name:
        base = name
    else:
        base = os.path.join("Resources", "images", name)
    if os.path.isfile(base):
        return base
    for ext in (".png", ".ico", ".svg"):
        candidate = base if base.endswith(ext) else base + ext
        if os.path.isfile(candidate):
            return candidate
        if not base.endswith(ext) and os.path.isfile(base + ext):
            return base + ext
    return base


def tinted_icon(name, color=None, size=16):
    """Return a monochrome-tinted QIcon for toolbar/chrome use.

    Alpha from the source PNG is preserved; RGB is replaced with ``color``
    (defaults to the current theme text token).
    """
    path = image_path(name)
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return QIcon(path)

    if color is None:
        try:
            from Extensions import StyleSheet
            color = StyleSheet.CURRENT_PALETTE.get("text", "#E8E8E8")
        except Exception:
            color = "#E8E8E8"
    if not isinstance(color, QColor):
        color = QColor(color)

    if size and (pixmap.width() != size or pixmap.height() != size):
        pixmap = pixmap.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.GlobalColor.transparent)
    painter = QPainter(tinted)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), color)
    painter.end()
    return QIcon(tinted)
