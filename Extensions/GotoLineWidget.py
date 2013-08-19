from PyQt4 import QtGui
import os.path


class GotoLineWidget(QtGui.QLabel):
    def __init__(self, editorTabWidget, parent=None):
        QtGui.QLabel.__init__(self, parent=None)

        self.editorTabWidget = editorTabWidget

        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)

        self.gotoLineAct = \
            QtGui.QAction(QtGui.QIcon(os.path.join("Resources","images","mail_check")),
                          "Goto Line", self, statusTip="Goto Line",
                          triggered=self.gotoLine)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.setMargin(3)
        mainLayout.setSpacing(2)
        self.setLayout(mainLayout)

        self.hideButton = QtGui.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(QtGui.QIcon(os.path.join("Resources","images","exit")))
        self.hideButton.clicked.connect(self.hide)
        mainLayout.addWidget(self.hideButton)

        self.lineNumberLine = QtGui.QSpinBox()
        self.lineNumberLine.setMinimum(1)
        self.lineNumberLine.setMaximum(100000000)
        self.lineNumberLine.valueChanged.connect(self.gotoLine)
        mainLayout.addWidget(self.lineNumberLine)

        self.goButton = QtGui.QToolButton()
        self.goButton.setAutoRaise(True)
        self.goButton.setDefaultAction(self.gotoLineAct)
        mainLayout.addWidget(self.goButton)

        mainLayout.setStretch(1, 1)

        self.setStyleSheet("""
                            QLabel {
                                background: rgba(138, 201, 255, 200);
                                border-radius: 0px;
                            }
                             """)

    def gotoLine(self, lineno):
        if lineno == False:
            lineno = self.lineNumberLine.value()
        self.editorTabWidget.focusedEditor().showLine(lineno - 1)
