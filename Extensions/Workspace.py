import os
import sys
import zipfile

from PyQt6.QtCore import QDir, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)


class CreateWorkSpaceThread(QThread):

    def run(self):
        self.errors = None
        try:
            archive = zipfile.ZipFile(
                os.path.join("Resources", "PcodeProjects.zip"), 'r')
            archive.extractall(self.path)
        except Exception as err:
            self.errors = str(err)

    def createWorkspace(self, path):
        self.path = path
        self.start()


class GetPathLine(QWidget):

    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.destinationLine = QLineEdit(self)
        self.destinationLine.textChanged.connect(self.textChanged.emit)
        mainLayout.addWidget(self.destinationLine)

        home_path = QDir().homePath()
        if sys.platform == 'win32':
            path = os.path.join(home_path, "My Documents", "PcodeProjects")
        else:
            path = os.path.join(home_path, "Documents", "PcodeProjects")
        self.destinationLine.setText(os.path.normpath(path))

        self.browseButton = QPushButton('...')
        self.browseButton.clicked.connect(self.browsePath)
        mainLayout.addWidget(self.browseButton)

    def browsePath(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Folder", QDir().homePath())
        if directory:
            self.destinationLine.setText(os.path.normpath(directory))

    def text(self):
        return self.destinationLine.text()


class Workspace(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(
            self, parent,
            Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("Workspace")
        self.setWindowIcon(QIcon(os.path.join("Resources", "images", "Icon")))
        self.setFixedSize(500, 130)

        self.createWorkSpaceThread = CreateWorkSpaceThread()
        self.createWorkSpaceThread.finished.connect(self.completeWorkspace)

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(QLabel("Choose the location of your Workspace:"))

        self.choiceBox = QComboBox()
        self.choiceBox.addItem("Choose an existing one")
        self.choiceBox.addItem("Create new")
        mainLayout.addWidget(self.choiceBox)

        self.getPathLine = GetPathLine()
        mainLayout.addWidget(self.getPathLine)

        mainLayout.addStretch(1)

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.statusLabel = QLabel()
        hbox.addWidget(self.statusLabel)
        hbox.addStretch(1)

        self.okButton = QPushButton("Done")
        self.okButton.clicked.connect(self.accept)
        hbox.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)
        hbox.addWidget(self.cancelButton)

        self.created = False
        self.exec()

    def completeWorkspace(self):
        QApplication.restoreOverrideCursor()
        if self.createWorkSpaceThread.errors is None:
            self.path = os.path.join(
                self.createWorkSpaceThread.path, "PcodeProjects")
            self.created = True
            self.close()
        else:
            self.statusLabel.clear()
            QMessageBox.warning(
                self, "Workspace",
                "Error creating workspace:\n\n{0}".format(
                    self.createWorkSpaceThread.errors))
            self.okButton.setDisabled(False)
            self.cancelButton.setDisabled(False)
            self.getPathLine.setDisabled(False)
            self.choiceBox.setDisabled(False)

    def accept(self):
        path = self.getPathLine.text()
        if os.path.exists(path):
            if self.choiceBox.currentIndex() == 0:
                if os.path.basename(path) == "PcodeProjects":
                    self.path = path
                    self.created = True
                    self.close()
                else:
                    QMessageBox.warning(
                        self, "Workspace", "The workspace is not valid!")
            else:
                self.okButton.setDisabled(True)
                self.cancelButton.setDisabled(True)
                self.getPathLine.setDisabled(True)
                self.choiceBox.setDisabled(True)
                self.statusLabel.setText("Creating workspace...")
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                self.createWorkSpaceThread.createWorkspace(path)
        else:
            QMessageBox.warning(self, "Workspace", "Path does not exist.")

    def cancel(self):
        self.created = False
        self.close()
