import os

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QSpinBox, QToolButton,
)


class GotoLineWidget(QLabel):

    def __init__(self, editorTabWidget, parent=None):
        QLabel.__init__(self, parent=None)

        self.editorTabWidget = editorTabWidget

        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)

        self.gotoLineAct = QAction(
            QIcon(os.path.join("Resources", "images", "mail_check")),
            "Goto Line", self, statusTip="Goto Line",
            triggered=self.gotoLine)

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(3, 3, 3, 3)
        mainLayout.setSpacing(2)
        self.setLayout(mainLayout)

        self.hideButton = QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "exit")))
        self.hideButton.clicked.connect(self.hide)
        mainLayout.addWidget(self.hideButton)

        self.lineNumberLine = QSpinBox()
        self.lineNumberLine.setMinimumHeight(25)
        self.lineNumberLine.setMinimum(1)
        self.lineNumberLine.setMaximum(100000000)
        self.lineNumberLine.valueChanged.connect(self.gotoLine)
        mainLayout.addWidget(self.lineNumberLine)

        self.hide()

    def gotoLine(self):
        line = self.lineNumberLine.value() - 1
        self.editorTabWidget.showLine(line)
