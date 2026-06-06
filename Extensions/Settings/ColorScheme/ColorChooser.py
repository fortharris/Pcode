from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QColorDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget,
)


class ColorChooser(QWidget):

    colorChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        self.colorHexLine = QLineEdit()
        self.colorHexLine.textChanged.connect(self.updateColor)
        hbox.addWidget(self.colorHexLine)

        self.colorButton = QPushButton()
        self.colorButton.clicked.connect(self.chooseColor)
        hbox.addWidget(self.colorButton)

    def updateColor(self):
        self.styleButton()
        self.colorChanged.emit(self.colorHexLine.text())

    def setColor(self, color):
        self.colorHexLine.setText(color)

    def chooseColor(self):
        color = self.colorHexLine.text()
        color = QColorDialog.getColor(QColor(color), self)
        if not color.isValid():
            return
        self.colorHexLine.setText(color.name())

    def styleButton(self):
        colorHex = self.colorHexLine.text()
        color = QColor(colorHex)
        if color.isValid():
            self.colorButton.setAutoFillBackground(True)
            style = ("""background: {0};
                         min-width: 70;
                         max-height: 30;
                         border: 1px solid lightgrey;
                         border-radius: 0px;""".format(colorHex))
            self.colorButton.setStyleSheet(style)
