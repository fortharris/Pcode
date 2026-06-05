from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

import os


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

    projectDataReady = QtCore.Signal(dict)

    def __init__(self, useData, parent=None):
        QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle('New Project')
        self.resize(500, 100)

        self.useData = useData

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        form = QFormLayout()

        self.nameLine = QLineEdit()
        self.nameLine.setText("PythonApp")
        self.nameLine.textChanged.connect(self.validateFields)
        form.addRow("Name: ", self.nameLine)

        self.typeBox = QComboBox()
        self.typeBox.addItem("Desktop Application")
        self.typeBox.addItem("Python Package")
        self.typeBox.currentIndexChanged.connect(self.showWindowTypeBox)
        form.addRow("Type: ", self.typeBox)

        self.windowTypeBox = QComboBox()
        self.windowTypeBox.addItem("GUI")
        self.windowTypeBox.addItem("Console")
        form.addRow('', self.windowTypeBox)

        self.destinationBox = GetPathLine(
            self.useData, self.useData.appPathDict["projectsdir"])
        self.destinationBox.textChanged.connect(self.validateFields)
        form.addRow("Destination: ", self.destinationBox)

        self.sourcesLine = GetPathLine(self.useData)
        self.sourcesLine.textChanged.connect(self.validateFields)
        form.addRow("Import Sources: ", self.sourcesLine)

        mainLayout.addLayout(form)
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
        hbox.addWidget(self.helpButton)

        mainLayout.addLayout(hbox)

        self.validateFields()

    def showWindowTypeBox(self):
        if self.typeBox.currentText() == "Desktop Application":
            self.windowTypeBox.show()
        else:
            self.windowTypeBox.hide()

    def validateFields(self):
        self.projectName = self.nameLine.text().strip()
        self.projectLocation = self.destinationBox.text().strip()
        self.importPath = self.sourcesLine.text().strip()
        if self.projectName == '':
            self.okButton.setDisabled(True)
            return
        elif self.projectLocation == '':
            self.okButton.setDisabled(True)
            return
        if os.path.exists(self.projectLocation) is False:
            self.okButton.setDisabled(True)
            return
        if self.importPath != '':
            if os.path.exists(self.importPath) is False:
                self.okButton.setDisabled(True)
                return
        if os.path.exists(os.path.join(self.projectLocation, self.projectName)):
            self.okButton.setDisabled(True)
            return
        self.okButton.setDisabled(False)

    def sendData(self):
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
