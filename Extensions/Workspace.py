import os
import sys
import zipfile

from PyQt6.QtCore import QDir, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)


def looks_like_workspace(path):
    """True if path is a Pcode workspace root."""
    if not path or not os.path.isdir(path):
        return False
    if os.path.basename(path) == "PcodeProjects":
        return True
    return (
        os.path.isdir(os.path.join(path, "Projects"))
        and os.path.isdir(os.path.join(path, "Settings")))


def ensure_workspace_dirs(path):
    """Create the minimum Projects/Settings layout if missing."""
    os.makedirs(os.path.join(path, "Projects"), exist_ok=True)
    os.makedirs(os.path.join(path, "Settings"), exist_ok=True)


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
        self.destinationLine.setAccessibleName("Workspace path")
        self.destinationLine.textChanged.connect(self.textChanged.emit)
        mainLayout.addWidget(self.destinationLine)

        home_path = QDir().homePath()
        if sys.platform == 'win32':
            path = os.path.join(home_path, "My Documents", "PcodeProjects")
        else:
            path = os.path.join(home_path, "Documents", "PcodeProjects")
        self.destinationLine.setText(os.path.normpath(path))

        self.browseButton = QPushButton('...')
        self.browseButton.setAccessibleName("Browse for workspace folder")
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
        self.setFixedSize(520, 160)

        self.createWorkSpaceThread = CreateWorkSpaceThread()
        self.createWorkSpaceThread.finished.connect(self.completeWorkspace)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(12, 12, 12, 12)
        mainLayout.setSpacing(8)
        self.setLayout(mainLayout)

        mainLayout.addWidget(QLabel(
            "Choose a folder for your Pcode workspace "
            "(projects and settings live here):"))

        self.choiceBox = QComboBox()
        self.choiceBox.setAccessibleName("Workspace mode")
        self.choiceBox.addItem("Use an existing folder")
        self.choiceBox.addItem("Create new workspace")
        mainLayout.addWidget(self.choiceBox)

        self.getPathLine = GetPathLine()
        mainLayout.addWidget(self.getPathLine)

        mainLayout.addStretch(1)

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.statusLabel = QLabel()
        self.statusLabel.setWordWrap(True)
        hbox.addWidget(self.statusLabel, 1)

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
            candidate = os.path.join(
                self.createWorkSpaceThread.path, "PcodeProjects")
            if os.path.isdir(candidate):
                self.path = candidate
            else:
                self.path = self.createWorkSpaceThread.path
                ensure_workspace_dirs(self.path)
            self.created = True
            self.close()
        else:
            self.statusLabel.clear()
            QMessageBox.warning(
                self, "Workspace",
                "Could not create the workspace:\n\n{0}".format(
                    self.createWorkSpaceThread.errors))
            self.okButton.setDisabled(False)
            self.cancelButton.setDisabled(False)
            self.getPathLine.setDisabled(False)
            self.choiceBox.setDisabled(False)

    def accept(self):
        path = self.getPathLine.text().strip()
        if not path:
            QMessageBox.warning(
                self, "Workspace", "Enter a folder path for the workspace.")
            return
        if not os.path.exists(path):
            QMessageBox.warning(
                self, "Workspace",
                "That folder does not exist yet.\n\n"
                "Create the folder in your file manager, or choose "
                "“Create new workspace” after picking a parent folder.")
            return
        if not os.path.isdir(path):
            QMessageBox.warning(
                self, "Workspace", "The path must be a folder.")
            return

        if self.choiceBox.currentIndex() == 0:
            if looks_like_workspace(path):
                ensure_workspace_dirs(path)
                self.path = path
                self.created = True
                self.close()
                return
            reply = QMessageBox.question(
                self, "Workspace",
                "This folder does not look like a Pcode workspace yet "
                "(expected a PcodeProjects folder, or Projects/ and "
                "Settings/ inside).\n\n"
                "Use it anyway and create the layout?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if reply != QMessageBox.StandardButton.Yes:
                return
            try:
                ensure_workspace_dirs(path)
            except OSError as err:
                QMessageBox.warning(
                    self, "Workspace",
                    "Could not prepare the folder:\n\n{0}".format(err))
                return
            self.path = path
            self.created = True
            self.close()
            return

        self.okButton.setDisabled(True)
        self.cancelButton.setDisabled(True)
        self.getPathLine.setDisabled(True)
        self.choiceBox.setDisabled(True)
        self.statusLabel.setText("Creating workspace\u2026")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.createWorkSpaceThread.createWorkspace(path)

    def cancel(self):
        self.created = False
        self.close()
