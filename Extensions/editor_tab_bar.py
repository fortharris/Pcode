"""Tab bar context menu and shortcuts for EditorTabWidget."""

import ctypes
import os

from Extensions.qt_bindings import QtGui


class EditorTabBar(QtGui.QTabBar):

    def __init__(self, app, renameFileAct, moduleToPackageAct, parent):
        QtGui.QTabBar.__init__(self, parent)

        self.setExpanding(True)
        self.setDrawBase(False)

        self.editorTabWidget = parent
        self.app = app
        self.renameFileAct = renameFileAct
        self.moduleToPackageAct = moduleToPackageAct

        self.createActions()

    def setKeymap(self):
        shortcuts = self.editorTabWidget.useData.CUSTOM_SHORTCUTS

        self.shortSplitFileReload = QtGui.QShortcut(
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
        self.closeTabAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "cross_")),
            "Close", self, statusTip="Close Tab", triggered=self.closeTab)

        self.copyPathAct = QtGui.QAction(
            "Copy File Path", self, statusTip="Copy File Path",
            triggered=self.copyPath)

        self.openFileLocationAct = QtGui.QAction(
            "Open File Location", self, statusTip="Open File Location",
            triggered=self.openFileLocation)

        self.cloneTabAct = QtGui.QAction(
            "Clone", self, statusTip="Create a copy of current tab",
            triggered=self.cloneTab)

        self.reloadTabAct = QtGui.QAction(
            "Reload", self, statusTip="Reload", triggered=self.reload)

        self.favouritesAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "plus")),
            "Add to Favourites", self, statusTip="Add to Favourites",
            triggered=self.editorTabWidget.addToFavourites)

        self.menu = QtGui.QMenu(self)
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
        reply = QtGui.QMessageBox.warning(
            self, "Reload", "Do you really want to reload?",
            QtGui.QMessageBox.StandardButton.Yes
            | QtGui.QMessageBox.StandardButton.No,
            QtGui.QMessageBox.StandardButton.No)
        if reply == QtGui.QMessageBox.StandardButton.Yes:
            self.editorTabWidget.reloadModules()

    def closeTab(self):
        index = self.currentIndex()
        self.editorTabWidget.closeEditorTab(index)

    def copyPath(self):
        filePath = self.editorTabWidget.getEditorData('filePath')
        self.app.clipboard().setText(filePath)

    def openFileLocation(self):
        filePath = self.editorTabWidget.getEditorData('filePath')
        ctypes.windll.shell32.ShellExecuteW(
            None, 'open', 'explorer.exe', '/n,/select, ' + filePath, None, 1)

    def cloneTab(self):
        index = self.currentIndex()
        name = self.tabText(index)
        new_index = index + 1
        sub_stack = self.editorTabWidget.newEditor(new_index, name)
        self.editorTabWidget.setCurrentIndex(new_index)
        self.editorTabWidget.updateTabName(new_index)
        editor = sub_stack.widget(0).widget(0)
        editor.setText(self.editorTabWidget.getEditor(index).text())
