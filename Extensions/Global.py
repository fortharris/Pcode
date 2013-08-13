import sys
from PyQt4 import QtGui, QtCore


def getDefaultFont():
    # Platform specific fonts
    if sys.platform == 'win32':
        font = 'Courier New'
        font_size = 10
    elif sys.platform == 'darwin':
        font = 'Monaco'
        font_size = 12
    else:
        font = 'Bitstream Vera Sans Mono'
        font_size = 10

    return QtGui.QFont(font, font_size)


def iconFromPath(path):
    fileInfo = QtCore.QFileInfo(path)
    iconProvider = QtGui.QFileIconProvider()
    icon = iconProvider.icon(fileInfo)

    return icon
