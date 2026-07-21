"""Tab bar context menu and shortcuts for EditorTabWidget."""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QShortcut
from PyQt6.QtWidgets import QMenu, QMessageBox, QTabBar

from Extensions.file_dialog_utils import reveal_in_file_manager


class EditorTabBar(QTabBar):

    def __init__(self, app, renameFileAct, moduleToPackageAct, parent):
        QTabBar.__init__(self, parent)

        self.setExpanding(False)
        self.setDrawBase(False)
        self.setObjectName("editorTabBar")
        self.setElideMode(Qt.TextElideMode.ElideRight)

        self.editorTabWidget = parent
        self.app = app
        self.renameFileAct = renameFileAct
        self.moduleToPackageAct = moduleToPackageAct

        self.createActions()

    def setKeymap(self):
        shortcuts = self.editorTabWidget.useData.CUSTOM_SHORTCUTS

        self.shortSplitFileReload = QShortcut(
            shortcuts["Ide"]["Reload-File"], self)
        self.shortSplitFileReload.activated.connect(self.reload)
        self.reloadTabAct.setShortcut(shortcuts["Ide"]["Reload-File"])

    def contextMenuEvent(self, event):
        filePath = self.editorTabWidget.getEditorData('filePath')
        isProjectFile = self.editorTabWidget.isProjectFile(filePath)

        isPyFile = (self.editorTabWidget.getEditorData("fileType") == "python")
        self.cloneTabAct.setEnabled(isPyFile)
        if isProjectFile:
            self.moduleToPackageAct.setEnabled(isPyFile)
            self.renameFileAct.setEnabled(isPyFile)
        else:
            self.moduleToPackageAct.setEnabled(False)
            self.renameFileAct.setEnabled(False)

        state = (filePath is not None)
        self.copyPathAct.setEnabled(state)
        self.openFileLocationAct.setEnabled(state)
        self.favouritesAct.setEnabled(state)
        self.reloadTabAct.setEnabled(state)

        self.menu.exec(event.globalPos())

    def createActions(self):
        self.closeTabAct = QAction(
            QIcon(os.path.join("Resources", "images", "cross_")),
            "Close", self, statusTip="Close Tab", triggered=self.closeTab)

        self.copyPathAct = QAction(
            "Copy File Path", self, statusTip="Copy File Path",
            triggered=self.copyPath)

        self.openFileLocationAct = QAction(
            "Open File Location", self, statusTip="Open File Location",
            triggered=self.openFileLocation)

        self.cloneTabAct = QAction(
            "Clone", self, statusTip="Create a copy of current tab",
            triggered=self.cloneTab)

        self.reloadTabAct = QAction(
            "Reload", self, statusTip="Reload", triggered=self.reload)

        self.favouritesAct = QAction(
            QIcon(os.path.join("Resources", "images", "plus")),
            "Add to Favourites", self, statusTip="Add to Favourites",
            triggered=self.editorTabWidget.addToFavourites)

        self.menu = QMenu(self)
        self.menu.addAction(self.closeTabAct)
        self.menu.addSeparator()
        self.menu.addAction(self.cloneTabAct)
        self.menu.addAction(self.editorTabWidget.writeLockAct)
        self.moduleToPackageAct = self.moduleToPackageAct
        self.menu.addAction(self.moduleToPackageAct)
        self.renameFileAct = self.renameFileAct
        self.menu.addAction(self.reloadTabAct)
        self.menu.addAction(self.renameFileAct)
        self.menu.addSeparator()
        self.menu.addAction(self.copyPathAct)
        self.menu.addAction(self.openFileLocationAct)
        self.menu.addSeparator()
        self.menu.addAction(self.favouritesAct)

    def reload(self):
        reply = QMessageBox.warning(
            self, "Reload", "Do you really want to reload?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.editorTabWidget.reloadModules()

    def closeTab(self):
        index = self.currentIndex()
        self.editorTabWidget.closeEditorTab(index)

    def copyPath(self):
        filePath = self.editorTabWidget.getEditorData('filePath')
        self.app.clipboard().setText(filePath)

    def openFileLocation(self):
        filePath = self.editorTabWidget.getEditorData('filePath')
        if not reveal_in_file_manager(filePath):
            QMessageBox.warning(
                self, "Reveal",
                "Could not open the file location.")

    def cloneTab(self):
        index = self.currentIndex()
        name = self.tabText(index)
        new_index = index + 1
        sub_stack = self.editorTabWidget.newEditor(new_index, name)
        self.editorTabWidget.setCurrentIndex(new_index)
        self.editorTabWidget.updateTabName(new_index)
        editor = sub_stack.widget(0).widget(0)
        editor.setText(self.editorTabWidget.getEditor(index).text())
