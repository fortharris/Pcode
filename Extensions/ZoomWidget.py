import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QAbstractSpinBox, QLabel, QSpinBox, QToolButton, QVBoxLayout,
)


class ZoomWidget(QLabel):

    def __init__(self, useData, editor, parent=None):
        QLabel.__init__(self, parent=None)

        self.useData = useData
        self.editor = editor
        self.prevValue = 0

        self.setMinimumHeight(130)
        self.setMaximumHeight(130)
        self.setMinimumWidth(38)
        self.setMaximumWidth(38)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(1, 1, 1, 1)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.increaseButton = QToolButton()
        self.increaseButton.setMaximumWidth(36)
        self.increaseButton.setText('+')
        self.increaseButton.setMaximumHeight(36)
        self.increaseButton.clicked.connect(self.zoomIn)
        mainLayout.addWidget(self.increaseButton)

        self.zoomBox = QSpinBox()
        self.zoomBox.setMinimum(0)
        self.zoomBox.setReadOnly(True)
        self.zoomBox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.zoomBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.zoomBox.setMaximum(100)
        self.zoomBox.setSingleStep(10)
        self.zoomBox.setSuffix("%")
        self.zoomBox.valueChanged.connect(self.changePosition)
        mainLayout.addWidget(self.zoomBox)

        self.decreaseButton = QToolButton()
        self.decreaseButton.setMaximumWidth(36)
        self.decreaseButton.setText('-')
        self.decreaseButton.setMaximumHeight(36)
        self.decreaseButton.clicked.connect(self.zoomOut)
        mainLayout.addWidget(self.decreaseButton)

        self.hideButton = QToolButton()
        self.hideButton.setMaximumWidth(36)
        self.hideButton.setMaximumHeight(36)
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "exit")))
        self.hideButton.clicked.connect(self.hide)
        mainLayout.addWidget(self.hideButton)

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
