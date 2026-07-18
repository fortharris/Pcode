import logging
import os
import shlex

from PyQt6.QtCore import QProcess, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPalette
from PyQt6.QtWidgets import (
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMenu, QMessageBox, QPushButton, QToolButton, QVBoxLayout,
)

from Extensions import Global, StyleSheet
from Extensions.PathLineEdit import PathLineEdit


def _split_params(param):
    """Split launcher parameters without invoking a shell."""
    text = (param or "").strip()
    if not text:
        return []
    try:
        # POSIX rules so quoted args work the same on Windows and Unix.
        return shlex.split(text, posix=True)
    except ValueError:
        return text.split()


def _is_safe_launcher_path(path):
    """Reject empty/relative-sneaky paths; require an existing absolute path."""
    if not path or not path.strip():
        return False, "Path cannot be empty."
    normalized = os.path.normpath(os.path.expanduser(path.strip()))
    if not os.path.isabs(normalized):
        return False, "Launcher path must be absolute."
    if not os.path.exists(normalized):
        return False, "Path does not exist."
    # Block obvious shell metacharacters in the executable path itself.
    if any(ch in normalized for ch in ("|", "&", ";", "`", "$", "\n", "\r")):
        return False, "Path contains disallowed characters."
    return True, normalized


class ExternalLauncher(QLabel):

    showMe = pyqtSignal()

    def __init__(self, externalLaunchList, parent=None):
        super(ExternalLauncher, self).__init__(parent)

        self.externalLaunchList = externalLaunchList

        self.setMinimumSize(600, 260)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)
        self.setAccessibleName("External launchers")

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
        self.hideButton.setAccessibleName("Close launchers")
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        trust = QLabel(
            "Launchers run programs you configure with argument lists "
            "(not a shell). Only add trusted absolute paths.")
        trust.setWordWrap(True)
        trust.setObjectName("toolWidgetSectionLabel")
        mainLayout.addWidget(trust)

        self.listWidget = QListWidget()
        self.listWidget.setAccessibleName("Launcher list")
        mainLayout.addWidget(self.listWidget)

        formLayout = QFormLayout()
        mainLayout.addLayout(formLayout)

        self.pathLine = PathLineEdit()
        self.pathLine.setAccessibleName("Launcher path")
        formLayout.addRow("Path:", self.pathLine)

        self.parametersLine = QLineEdit()
        self.parametersLine.setAccessibleName("Launcher parameters")
        self.parametersLine.setPlaceholderText('Optional args, e.g. --help "my file"')
        formLayout.addRow("Parameters:", self.parametersLine)

        hbox = QHBoxLayout()
        formLayout.addRow('', hbox)

        self.removeButton = QPushButton("Remove")
        self.removeButton.setAccessibleName("Remove launcher")
        self.removeButton.clicked.connect(self.removeLauncher)
        hbox.addWidget(self.removeButton)

        self.addButton = QPushButton("Add")
        self.addButton.setAccessibleName("Add launcher")
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
        item = self.listWidget.currentItem()
        if item is None:
            return
        path = item.text()
        if path in self.externalLaunchList:
            del self.externalLaunchList[path]
        self.loadExternalLaunchers()

    def addLauncher(self):
        ok, result = _is_safe_launcher_path(self.pathLine.text())
        if not ok:
            QMessageBox.warning(self, "Add Launcher", result)
            return
        path = result
        if path in self.externalLaunchList:
            QMessageBox.warning(
                self, "Add Launcher", "Path already exists in launchers!")
            return
        self.externalLaunchList[path] = self.parametersLine.text().strip()
        self.loadExternalLaunchers()

    def loadExternalLaunchers(self):
        self.launcherMenu.clear()
        self.listWidget.clear()
        if len(self.externalLaunchList) > 0:
            self.actionGroup = QActionGroup(self)
            self.actionGroup.triggered.connect(self.launcherActivated)
            for path, _param in self.externalLaunchList.items():
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
        param = self.externalLaunchList.get(path, "")
        ok, normalized = _is_safe_launcher_path(path)
        if not ok:
            QMessageBox.warning(self, "Launch", normalized)
            return
        path = normalized
        if os.path.isdir(path):
            try:
                os.startfile(path)
            except Exception as err:
                logging.warning("Failed to open directory launcher: %s", err)
                QMessageBox.warning(self, "Launch", str(err))
            return

        args = _split_params(param)
        if not args:
            try:
                os.startfile(path)
            except Exception as err:
                logging.warning("Failed to start launcher: %s", err)
                QMessageBox.warning(self, "Launch", str(err))
            return

        process = QProcess(self)
        if not process.startDetached(path, args):
            QMessageBox.warning(
                self, "Launch",
                "Failed to start:\n{0}\n{1}".format(path, " ".join(args)))
