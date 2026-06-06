import os

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QToolButton


class PathLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super(PathLineEdit, self).__init__(parent)

        self.setTextMargins(0, 0, 42, 0)

        hbox = QHBoxLayout()
        self.setLayout(hbox)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addStretch(1)

        self.fileButton = QToolButton()
        self.fileButton.setToolTip("Insert File Path")
        self.fileButton.setAutoRaise(True)
        self.fileButton.setIcon(QIcon(os.path.join("Resources", "images", "page")))
        self.fileButton.clicked.connect(self.insertFilePath)
        hbox.addWidget(self.fileButton)

        self.dirButton = QToolButton()
        self.dirButton.setToolTip("Insert Directory Path")
        self.dirButton.setAutoRaise(True)
        self.dirButton.setIcon(QIcon(os.path.join("Resources", "images", "folder_closed")))
        self.dirButton.clicked.connect(self.insertDirPath)
        hbox.addWidget(self.dirButton)

    def insertDirPath(self):
        directory = QFileDialog.getExistingDirectory(self, "", QDir.homePath())
        if directory:
            self.setText(os.path.normpath(directory))

    def insertFilePath(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "File", QDir.homePath(), "All Files (*)")
        if fileName:
            self.setText(os.path.normpath(fileName))
