import os
from PyQt4 import QtCore, QtGui


class GetPathLine(QtGui.QWidget):

    textChanged = QtCore.pyqtSignal(str)

    def __init__(self, useData, defaultText=None, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.useData = useData

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        self.locationLine = QtGui.QLineEdit()
        if defaultText is not None:
            self.locationLine.setText(defaultText)
        self.locationLine.textChanged.connect(self.textChanged.emit)
        mainLayout.addWidget(self.locationLine)

        self.browseButton = QtGui.QPushButton('...')
        self.browseButton.clicked.connect(self.browsePath)
        mainLayout.addWidget(self.browseButton)

    def browsePath(self):
        directory = QtGui.QFileDialog.getExistingDirectory(
            self, "Select Folder",
            self.useData.getLastOpenedDir())
        if directory:
            self.useData.saveLastOpenedDir(directory)
            self.locationLine.setText(os.path.normpath(directory))

    def text(self):
        return self.locationLine.text()


class NewProjectDialog(QtGui.QDialog):

    projectDataReady = QtCore.pyqtSignal(dict)

    def __init__(self, useData, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle('New Project')
        self.resize(500, 100)

        self.useData = useData

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        form = QtGui.QFormLayout()

        self.nameLine = QtGui.QLineEdit()
        self.nameLine.setText("PythonApp")
        self.nameLine.textChanged.connect(self.validateFields)
        form.addRow("Name: ", self.nameLine)

        self.typeBox = QtGui.QComboBox()
        self.typeBox.addItem("Desktop Application")
        self.typeBox.addItem("Python Package")
        form.addRow("Type: ", self.typeBox)

        self.destinationBox = GetPathLine(
            self.useData, self.useData.appPathDict["projectsdir"])
        self.destinationBox.textChanged.connect(self.validateFields)
        form.addRow("Destination: ", self.destinationBox)

        self.sourcesLine = GetPathLine(self.useData)
        self.sourcesLine.textChanged.connect(self.validateFields)
        form.addRow("Import Sources: ", self.sourcesLine)

        mainLayout.addLayout(form)
        mainLayout.addStretch(1)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)

        self.okButton = QtGui.QPushButton("Ok")
        self.okButton.clicked.connect(self.sendData)
        hbox.addWidget(self.okButton)

        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        hbox.addWidget(self.cancelButton)

        self.helpButton = QtGui.QPushButton("Help")
        hbox.addWidget(self.helpButton)

        mainLayout.addLayout(hbox)

        self.validateFields()

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
            "location": self.projectLocation,
            "importdir": self.importPath
        }
        self.close()
        self.projectDataReady.emit(data)
