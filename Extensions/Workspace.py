import sys
import os
import zipfile
from PyQt4 import QtCore, QtGui


class CreateWorkSpaceThread(QtCore.QThread):

    def run(self):
        self.errors = None
        try:
            zip = zipfile.ZipFile("Resources\\PcodeProjects.zip", 'r')
            zip.extractall(self.path)
        except Exception as err:
            self.errors = str(err)

    def createWorkspace(self, path):
        self.path = path

        self.start()


class GetPathLine(QtGui.QWidget):

    textChanged = QtCore.pyqtSignal(str)

    def __init__(self, defaultText=None, parent=None):
        QtGui.QWidget.__init__(self, parent)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        self.locationLine = QtGui.QLineEdit()
        self.locationLine.textChanged.connect(self.textChanged.emit)
        if defaultText != None:
            self.locationLine.setText(defaultText)
        mainLayout.addWidget(self.locationLine)

        homePath = QtCore.QDir().homePath()

        if sys.platform == 'win32':
            path = os.path.join(homePath,
                                "My Documents\\PcodeProjects")
        elif sys.platform == 'darwin':
            path = os.path.join(homePath,
                                "My Documents\\PcodeProjects")
        else:
            path = os.path.join(homePath,
                                "My Documents\\PcodeProjects")
        path = os.path.normpath(path)
        self.locationLine.setText(path)

        self.browseButton = QtGui.QPushButton('...')
        self.browseButton.clicked.connect(self.browsePath)
        mainLayout.addWidget(self.browseButton)

    def browsePath(self):
        homePath = QtCore.QDir().homePath()
        directory = QtGui.QFileDialog.getExistingDirectory(
            self, "Select Folder",
            homePath)
        if directory:
            self.locationLine.setText(os.path.normpath(directory))

    def text(self):
        return self.locationLine.text()


class WorkSpace(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Workspace")
        self.setWindowIcon(QtGui.QIcon("Resources\\images\\Icon"))
        self.setFixedSize(500, 130)

        self.createWorkSpaceThread = CreateWorkSpaceThread()
        self.createWorkSpaceThread.finished.connect(self.completeWorkspace)

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addWidget(
            QtGui.QLabel("Choose the location of your Workspace:"))

        self.choiceBox = QtGui.QComboBox()
        self.choiceBox.addItem("Choose an existing one")
        self.choiceBox.addItem("Create new")
        mainLayout.addWidget(self.choiceBox)

        self.getPathLine = GetPathLine()
        mainLayout.addWidget(self.getPathLine)

        mainLayout.addStretch(1)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.statusLabel = QtGui.QLabel()
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.okButton = QtGui.QPushButton("Done")
        self.okButton.clicked.connect(self.accept)
        hbox.addWidget(self.okButton)

        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)
        hbox.addWidget(self.cancelButton)

        self.created = False

        self.exec_()

    def completeWorkspace(self):
        QtGui.QApplication.restoreOverrideCursor()
        if self.createWorkSpaceThread.errors == None:
            self.path = os.path.join(
                self.createWorkSpaceThread.path, "PcodeProjects")
            self.created = True
            self.close()
        else:
            self.statusLabel.clear()
            message = QtGui.QMessageBox.warning(
                self, "Workspace", "Error creating workspace:\n\n{0}".format(self.createWorkSpaceThread.errors))
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
                    message = QtGui.QMessageBox.warning(
                        self, "Workspace", "The workspace is not valid!")
                    return
            else:
                self.okButton.setDisabled(True)
                self.cancelButton.setDisabled(True)
                self.getPathLine.setDisabled(True)
                self.choiceBox.setDisabled(True)
                self.statusLabel.setText("Creating workspace...")
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

                self.createWorkSpaceThread.createWorkspace(path)
        else:
            message = QtGui.QMessageBox.warning(
                self, "Workspace", "Path does not exist.")

    def cancel(self):
        self.created = False
        self.close()
