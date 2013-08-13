from PyQt4 import QtCore, QtGui


class ZoomWidget(QtGui.QLabel):

    def __init__(self, useData, editor, parent=None):
        QtGui.QLabel.__init__(self, parent=None)

        self.useData = useData
        self.editor = editor
        self.prevValue = 0

        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        self.setMinimumWidth(180)
        self.setMaximumWidth(180)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMargin(2)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(0)
        mainLayout.addLayout(hbox)

        self.decreaseButton = QtGui.QToolButton()
        self.decreaseButton.setMaximumWidth(25)
        self.decreaseButton.setText('-')
        self.decreaseButton.setMaximumHeight(25)
        self.decreaseButton.clicked.connect(self.zoomOut)
        hbox.addWidget(self.decreaseButton)

        self.zoomBox = QtGui.QSpinBox()
        self.zoomBox.setMinimum(0)
        self.zoomBox.setReadOnly(True)
        self.zoomBox.setAlignment(QtCore.Qt.AlignHCenter)
        self.zoomBox.setButtonSymbols(2)
        self.zoomBox.setMaximum(100)
        self.zoomBox.setSingleStep(10)
        self.zoomBox.setSuffix("%")
        self.zoomBox.valueChanged.connect(self.changePosition)
        hbox.addWidget(self.zoomBox)

        self.increaseButton = QtGui.QToolButton()
        self.increaseButton.setMaximumWidth(25)
        self.increaseButton.setText('+')
        self.increaseButton.setMaximumHeight(25)
        self.increaseButton.clicked.connect(self.zoomIn)
        hbox.addWidget(self.increaseButton)

        self.hideButton = QtGui.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(QtGui.QIcon("Resources\\images\\exit"))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.setLayout(mainLayout)

        self.hide()

        self.setStyleSheet("""
                        QLabel {
                            background: rgba(138, 201, 255, 200);
                            border-radius: 0px;
                        }

                         """)

    def changePosition(self, value):
        if self.prevValue > value:
            self.editor.zoomOut()
        elif self.prevValue < value:
            self.editor.zoomIn()
        else:
            self.editor.zoomOut()
        self.prevValue = value

    def zoomIn(self):
        self.zoomBox.setValue(self.zoomBox.value() + 10)

    def zoomOut(self):
        self.zoomBox.setValue(self.zoomBox.value() - 10)
