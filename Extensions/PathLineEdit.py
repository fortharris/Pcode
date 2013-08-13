import os
from PyQt4 import QtCore, QtGui


class PathLineEdit(QtGui.QLineEdit):

    def __init__(self, parent=None):
        super(PathLineEdit, self).__init__(parent)

        self.setTextMargins(0, 0, 42, 0)

        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)
        hbox.setMargin(0)
        hbox.setSpacing(0)
        hbox.addStretch(1)

        self.fileButton = QtGui.QToolButton()
        self.fileButton.setToolTip("Insert File Path")
        self.fileButton.setAutoRaise(True)
        self.fileButton.setIcon(QtGui.QIcon("Resources\\images\\page"))
        self.fileButton.clicked.connect(self.insertFilePath)
        hbox.addWidget(self.fileButton)

        self.dirButton = QtGui.QToolButton()
        self.dirButton.setToolTip("Insert Directory Path")
        self.dirButton.setAutoRaise(True)
        self.dirButton.setIcon(QtGui.QIcon("Resources\\images\\folder_closed"))
        self.dirButton.clicked.connect(self.insertDirPath)
        hbox.addWidget(self.dirButton)

    def insertDirPath(self):
        directory = QtGui.QFileDialog.getExistingDirectory(
            self, "c:\\")
        if directory:
            self.setText(os.path.normpath(directory))

    def insertFilePath(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     "File", "c:\\",
                                                     "All Files (*)")
        if fileName:
            self.setText(os.path.normpath(fileName))
