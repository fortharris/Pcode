import os

from PyQt6.QtCore import QProcess, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPalette
from PyQt6.QtWidgets import (
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMenu, QMessageBox, QPushButton, QToolButton, QVBoxLayout,
)

from Extensions import Global, StyleSheet
from Extensions.PathLineEdit import PathLineEdit


class ExternalLauncher(QLabel):

    showMe = pyqtSignal()

    def __init__(self, externalLaunchList, parent=None):
        super(ExternalLauncher, self).__init__(parent)

        self.externalLaunchList = externalLaunchList

        self.setMinimumSize(600, 230)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.setBackgroundRole(QPalette.ColorRole.Window)
        self.setAutoFillBackground(True)

        mainLayout = QVBoxLayout()

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QLabel("Manage Launchers")
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)

        hbox.addStretch(1)

        self.hideButton = QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.listWidget = QListWidget()
        mainLayout.addWidget(self.listWidget)

        formLayout = QFormLayout()
        mainLayout.addLayout(formLayout)

        self.pathLine = PathLineEdit()
        formLayout.addRow("Path:", self.pathLine)

        self.parametersLine = QLineEdit()
        formLayout.addRow("Parameters:", self.parametersLine)

        hbox = QHBoxLayout()
        formLayout.addRow('', hbox)

        self.removeButton = QPushButton("Remove")
        self.removeButton.clicked.connect(self.removeLauncher)
        hbox.addWidget(self.removeButton)

        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(self.addLauncher)
        hbox.addWidget(self.addButton)

        hbox.addStretch(1)

        self.setLayout(mainLayout)

        self.manageLauncherAct = QAction(
            QIcon(os.path.join("Resources", "images", "settings")),
            "Manage Launchers", self, statusTip="Manage Launchers",
            triggered=self.showMe.emit)

        self.launcherMenu = QMenu("Launch External...")
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
                    QMessageBox.warning(
                        self, "Add Launcher", "Path already exists in launchers!")
            else:
                QMessageBox.warning(
                    self, "Add Launcher", "Path does not exists!")
        else:
            QMessageBox.warning(
                self, "Add Launcher", "Path cannot be empty!")

    def loadExternalLaunchers(self):
        self.launcherMenu.clear()
        self.listWidget.clear()
        if len(self.externalLaunchList) > 0:
            self.actionGroup = QActionGroup(self)
            self.actionGroup.triggered.connect(self.launcherActivated)
            for path, param in self.externalLaunchList.items():
                action = QAction(Global.iconFromPath(path), path, self)
                self.actionGroup.addAction(action)
                self.launcherMenu.addAction(action)

                item = QListWidgetItem(Global.iconFromPath(path), path)
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
                    process = QProcess(self)
                    process.startDetached(path, [param])
        else:
            QMessageBox.warning(self, "Launch", "Path is not available.")
