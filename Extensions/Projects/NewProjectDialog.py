from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

import os

from Extensions import StyleSheet


class GetPathLine(QWidget):

    textChanged = pyqtSignal(str)

    def __init__(self, useData, defaultText=None, parent=None):
        QWidget.__init__(self, parent)

        self.useData = useData

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.locationLine = QLineEdit()
        if defaultText is not None:
            self.locationLine.setText(defaultText)
        self.locationLine.textChanged.connect(self.textChanged.emit)
        mainLayout.addWidget(self.locationLine)

        self.browseButton = QPushButton('...')
        self.browseButton.clicked.connect(self.browsePath)
        mainLayout.addWidget(self.browseButton)

    def browsePath(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Folder",
            self.useData.getLastOpenedDir())
        if directory:
            self.useData.saveLastOpenedDir(directory)
            self.locationLine.setText(os.path.normpath(directory))

    def text(self):
        return self.locationLine.text()


class NewProjectDialog(QDialog):

    projectDataReady = pyqtSignal(dict)

    def __init__(self, useData, parent=None):
        QDialog.__init__(
            self, parent,
            Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle('New Project')
        self.resize(520, 180)

        self.useData = useData

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(12, 12, 12, 12)
        mainLayout.setSpacing(8)
        self.setLayout(mainLayout)

        form = QFormLayout()
        form.setSpacing(8)

        self.nameLine = QLineEdit()
        self.nameLine.setText("PythonApp")
        self.nameLine.setAccessibleName("Project name")
        self.nameLine.textChanged.connect(self.validateFields)
        form.addRow("Name:", self.nameLine)

        self.typeBox = QComboBox()
        self.typeBox.setAccessibleName("Project type")
        self.typeBox.addItem("Desktop Application")
        self.typeBox.addItem("Python Package")
        self.typeBox.currentIndexChanged.connect(self.showWindowTypeBox)
        form.addRow("Type:", self.typeBox)

        self.windowTypeBox = QComboBox()
        self.windowTypeBox.setAccessibleName("Window type")
        self.windowTypeBox.addItem("GUI")
        self.windowTypeBox.addItem("Console")
        form.addRow("Window:", self.windowTypeBox)

        self.destinationBox = GetPathLine(
            self.useData, self.useData.appPathDict["projectsdir"])
        self.destinationBox.locationLine.setAccessibleName(
            "Project destination")
        self.destinationBox.textChanged.connect(self.validateFields)
        form.addRow("Destination:", self.destinationBox)

        self.sourcesLine = GetPathLine(self.useData)
        self.sourcesLine.locationLine.setAccessibleName("Import sources")
        self.sourcesLine.locationLine.setPlaceholderText(
            "Optional — copy files from an existing folder")
        self.sourcesLine.textChanged.connect(self.validateFields)
        form.addRow("Import Sources:", self.sourcesLine)

        mainLayout.addLayout(form)

        self.errorLabel = QLabel()
        self.errorLabel.setWordWrap(True)
        warn = StyleSheet.CURRENT_PALETTE.get("warning", "#C06000")
        self.errorLabel.setStyleSheet("color: {0};".format(warn))
        self.errorLabel.setAccessibleName("Project validation message")
        mainLayout.addWidget(self.errorLabel)

        mainLayout.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        self.okButton = QPushButton("Ok")
        self.okButton.clicked.connect(self.sendData)
        hbox.addWidget(self.okButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        hbox.addWidget(self.cancelButton)

        self.helpButton = QPushButton("Help")
        self.helpButton.setAccessibleName("New project help")
        self.helpButton.clicked.connect(self.showHelp)
        hbox.addWidget(self.helpButton)

        mainLayout.addLayout(hbox)

        self.validateFields()

    def showHelp(self):
        QMessageBox.information(
            self, "New Project",
            "Name — folder name under Destination (letters, digits, "
            "underscore, hyphen).\n\n"
            "Type — Desktop Application creates a main .py script; "
            "Python Package creates an __init__.py package.\n\n"
            "Import Sources — optional folder whose files are copied into "
            "the new project. Leave blank to start empty.")

    def showWindowTypeBox(self):
        if self.typeBox.currentText() == "Desktop Application":
            self.windowTypeBox.show()
        else:
            self.windowTypeBox.hide()

    def validateFields(self):
        self.projectName = self.nameLine.text().strip()
        self.projectLocation = self.destinationBox.text().strip()
        self.importPath = self.sourcesLine.text().strip()
        error = ""
        if self.projectName == '':
            error = "Enter a project name."
        elif any(ch in self.projectName for ch in '\\/:*?"<>|'):
            error = "Project name cannot contain path or reserved characters."
        elif self.projectLocation == '':
            error = "Choose a destination folder."
        elif not os.path.exists(self.projectLocation):
            error = "Destination folder does not exist."
        elif not os.path.isdir(self.projectLocation):
            error = "Destination must be a folder."
        elif self.importPath and not os.path.exists(self.importPath):
            error = "Import Sources path does not exist."
        elif os.path.exists(
                os.path.join(self.projectLocation, self.projectName)):
            error = "A project with that name already exists here."
        self.errorLabel.setText(error)
        self.okButton.setDisabled(bool(error))

    def sendData(self):
        self.validateFields()
        if not self.okButton.isEnabled():
            return
        if self.typeBox.currentText() == "Desktop Application":
            mainScript = self.nameLine.text() + '.py'
        elif self.typeBox.currentText() == "Python Package":
            mainScript = "__init__.py"
        data = {
            "mainscript": mainScript,
            "name": self.projectName,
            "type": self.typeBox.currentText(),
            "windowtype": self.windowTypeBox.currentText(),
            "location": self.projectLocation,
            "importdir": self.importPath
            }
        self.close()
        self.projectDataReady.emit(data)
