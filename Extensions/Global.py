import sys

from PyQt6.QtCore import QFileInfo
from PyQt6.QtGui import QFileIconProvider, QFont


def getDefaultFont():
    if sys.platform == 'win32':
        font = 'Lucida Console'
        font_size = 9
    elif sys.platform == 'darwin':
        font = 'Monaco'
        font_size = 10
    else:
        font = 'Bitstream Vera Sans Mono'
        font_size = 10

    return QFont(font, font_size)


def iconFromPath(path):
    fileInfo = QFileInfo(path)
    iconProvider = QFileIconProvider()
    return iconProvider.icon(fileInfo)
