from PyQt4 import QtCore, QtGui


class ColorChooser(QtGui.QWidget):

    colorChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(0)
        self.setLayout(hbox)

        self.colorHexLine = QtGui.QLineEdit()
        self.colorHexLine.textChanged.connect(self.updateColor)
        hbox.addWidget(self.colorHexLine)

        self.colorButton = QtGui.QPushButton()
        self.colorButton.clicked.connect(self.chooseColor)
        hbox.addWidget(self.colorButton)

    def updateColor(self):
        self.styleButton()
        self.colorChanged.emit(self.colorHexLine.text())

    def setColor(self, color):
        self.colorHexLine.setText(color)

    def chooseColor(self):
        color = self.colorHexLine.text()
        color = QtGui.QColorDialog.getColor(QtGui.QColor(color), self)
        if not color.isValid():
            return
        self.colorHexLine.setText(color.name())

    def styleButton(self):
        color = self.colorHexLine.text()
        self.colorButton.setAutoFillBackground(True)
        style = ("""background: {0};
                     min-width: 70;
                     max-height: 30;
                     border: 1px solid lightgrey;
                     border-radius: 0px;""".format(color))
        self.colorButton.setStyleSheet(style)
