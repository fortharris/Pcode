import os
from PyQt4 import QtCore, QtGui

from Extensions import Global
from Extensions.PathLineEdit import PathLineEdit


class ExternalLauncher(QtGui.QLabel):

    showMe = QtCore.pyqtSignal()

    def __init__(self, externalLaunchList, parent=None):
        super(ExternalLauncher, self).__init__(parent)

        self.externalLaunchList = externalLaunchList

        self.setMinimumSize(600, 230)

        self.setBackgroundRole(QtGui.QPalette.Background)
        self.setAutoFillBackground(True)

        mainLayout = QtGui.QVBoxLayout()

        label = QtGui.QLabel("Manage Launchers")
        label.setStyleSheet("font: 14px; color: grey;")
        mainLayout.addWidget(label)

        self.listWidget = QtGui.QListWidget()
        mainLayout.addWidget(self.listWidget)

        formLayout = QtGui.QFormLayout()
        mainLayout.addLayout(formLayout)

        self.pathLine = PathLineEdit()
        formLayout.addRow("Path:", self.pathLine)

        self.parametersLine = QtGui.QLineEdit()
        formLayout.addRow("Parameters:", self.parametersLine)

        hbox = QtGui.QHBoxLayout()

        self.removeButton = QtGui.QPushButton("Remove")
        self.removeButton.clicked.connect(self.removeLauncher)
        hbox.addWidget(self.removeButton)

        self.addButton = QtGui.QPushButton("Add")
        self.addButton.clicked.connect(self.addLauncher)
        hbox.addWidget(self.addButton)

        hbox.addStretch(1)

        self.closeButton = QtGui.QPushButton("Close")
        self.closeButton.clicked.connect(self.hide)
        hbox.addWidget(self.closeButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.manageLauncherAct = \
            QtGui.QAction(QtGui.QIcon(os.path.join("Resources", "images", "settings")),
                          "Manage Launchers", self, statusTip="Manage Launchers",
                          triggered=self.showMe.emit)

        self.launcherMenu = QtGui.QMenu("Launch External...")
        self.loadExternalLaunchers()

    def removeLauncher(self):
        path = self.listWidget.currentItem().text()
        del self.externalLaunchList[path]
        self.loadExternalLaunchers()

    def addLauncher(self):
        path = self.pathLine.text().strip()
        if path != '':
            if os.path.exists(path):
                if path not in self.externalLaunchList:
                    self.externalLaunchList[
                        path] = self.parametersLine.text().strip()
                    self.loadExternalLaunchers()
                else:
                    message = QtGui.QMessageBox.warning(
                        self, "Add Launcher", "Path already exists in launchers!")
            else:
                message = QtGui.QMessageBox.warning(
                    self, "Add Launcher", "Path does not exists!")
        else:
            message = QtGui.QMessageBox.warning(
                self, "Add Launcher", "Path cannot be empty!")

    def loadExternalLaunchers(self):
        self.launcherMenu.clear()
        self.listWidget.clear()
        if len(self.externalLaunchList) > 0:
            self.actionGroup = QtGui.QActionGroup(self)
            self.actionGroup.triggered.connect(
                self.launcherActivated)
            for path, param in self.externalLaunchList.items():
                action = QtGui.QAction(Global.iconFromPath(path), path, self)
                self.actionGroup.addAction(action)
                self.launcherMenu.addAction(action)

                item = QtGui.QListWidgetItem(Global.iconFromPath(path), path)
                item.setToolTip(path)
                self.listWidget.addItem(item)

            self.launcherMenu.addSeparator()
            self.launcherMenu.addAction(self.manageLauncherAct)
        else:
            self.launcherMenu.addAction(self.manageLauncherAct)

        if len(self.externalLaunchList) == 0:
            self.removeButton.setDisabled(True)
        else:
            self.removeButton.setDisabled(False)

    def launcherActivated(self, action):
        path = action.text()
        param = self.externalLaunchList[path]
        if os.path.exists(path):
            if os.path.isdir(path):
                os.startfile(path)
            else:
                if param == '':
                    os.startfile(path)
                else:
                    process = QtCore.QProcess(self)
                    process.startDetached(path, [param])
        else:
            message = QtGui.QMessageBox.warning(self, "Launch",
                                                "Path is not available.")
