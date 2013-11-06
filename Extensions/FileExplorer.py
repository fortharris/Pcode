import os
import ctypes
from PyQt4 import QtCore, QtGui

from Extensions import StyleSheet


class ManageShortcuts(QtGui.QLabel):

    updateShortcuts = QtCore.pyqtSignal()

    def __init__(self, useData, FILE_EXPLORER_SHORTCUTS, parent=None):
        super(ManageShortcuts, self).__init__(parent)

        self.setMinimumSize(600, 230)

        self.setBackgroundRole(QtGui.QPalette.Background)
        self.setAutoFillBackground(True)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.useData = useData
        self.FILE_EXPLORER_SHORTCUTS = FILE_EXPLORER_SHORTCUTS

        mainLayout = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QtGui.QLabel("Manage Shortcuts")
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)

        hbox.addStretch(1)

        self.hideButton = QtGui.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.shortcutsWidget = QtGui.QListWidget()
        self.shortcutsWidget.itemSelectionChanged.connect(
            self.setButtonsVisibility)
        mainLayout.addWidget(self.shortcutsWidget)

        hbox = QtGui.QHBoxLayout()

        self.removeShortcutButton = QtGui.QToolButton()
        self.removeShortcutButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "minus")))
        self.removeShortcutButton.clicked.connect(self.removeShorcut)
        hbox.addWidget(self.removeShortcutButton)

        self.addShortcutButton = QtGui.QToolButton()
        self.addShortcutButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "add")))
        self.addShortcutButton.clicked.connect(self.addShortcut)
        hbox.addWidget(self.addShortcutButton)

        hbox.addStretch(1)

        self.moveDownButton = QtGui.QToolButton()
        self.moveDownButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "down")))
        self.moveDownButton.clicked.connect(self.moveDown)
        hbox.addWidget(self.moveDownButton)

        self.moveUpButton = QtGui.QToolButton()
        self.moveUpButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "up")))
        self.moveUpButton.clicked.connect(self.moveUp)
        hbox.addWidget(self.moveUpButton)

        hbox.addStretch(1)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.loadShortcuts()

    def loadShortcuts(self):
        self.shortcutsWidget.clear()
        for i in self.FILE_EXPLORER_SHORTCUTS:
            s = i.strip()
            item = QtGui.QListWidgetItem(s)
            item.setToolTip(s)
            self.shortcutsWidget.addItem(item)
        self.updateShortcuts.emit()

    def removeShorcut(self):
        text = self.shortcutsWidget.currentItem().text()
        self.FILE_EXPLORER_SHORTCUTS.remove(text)
        self.loadShortcuts()

    def addShortcut(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Select directory", self.useData.getLastOpenedDir(), options)
        if directory:
            directory = os.path.normpath(directory)
            if directory in self.FILE_EXPLORER_SHORTCUTS:
                pass
            else:
                # save shortcut
                self.FILE_EXPLORER_SHORTCUTS.append(directory)
                self.useData.saveLastOpenedDir(directory)
                self.loadShortcuts()

    def moveUp(self):
        row = self.shortcutsWidget.currentRow()
        if row == 0:
            pass
        else:
            text = self.shortcutsWidget.currentItem().text()
            self.FILE_EXPLORER_SHORTCUTS.remove(text)
            self.FILE_EXPLORER_SHORTCUTS.insert(row - 1, text)
            self.loadShortcuts()
            self.shortcutsWidget.setCurrentRow(row - 1)

    def moveDown(self):
        row = self.shortcutsWidget.currentRow()
        if (row + 1) == self.shortcutsWidget.count():
            return
        text = self.shortcutsWidget.currentItem().text()
        self.FILE_EXPLORER_SHORTCUTS.remove(text)
        self.FILE_EXPLORER_SHORTCUTS.insert(row + 1, text)
        self.loadShortcuts()
        self.shortcutsWidget.setCurrentRow(row + 1)

    def setButtonsVisibility(self):
        if len(self.shortcutsWidget.selectedItems()) == 0:
            self.removeShortcutButton.setDisabled(True)
            self.moveUpButton.setDisabled(True)
            self.moveDownButton.setDisabled(True)
        else:
            self.removeShortcutButton.setDisabled(False)
            self.moveUpButton.setDisabled(False)
            self.moveDownButton.setDisabled(False)


class FileExplorer(QtGui.QTreeView):

    fileActivated = QtCore.pyqtSignal(str)

    def __init__(self, useData, FILE_EXPLORER_SHORTCUTS, messagesWidget, editorTabWidget, parent=None):
        QtGui.QTreeView.__init__(self, parent)

        self.setAcceptDrops(True)

        self.setAnimated(True)
        self.setAutoScroll(True)
        self.activated.connect(self.treeItemActivated)
        self.setObjectName("sidebarItem")

        self.fileSystemModel = QtGui.QFileSystemModel()
        self.fileSystemModel.setRootPath(QtCore.QDir.rootPath())
        self.fileSystemModel.setNameFilterDisables(False)
        self.setModel(self.fileSystemModel)
        self.setColumnWidth(0, 300)

        self.useData = useData
        self.FILE_EXPLORER_SHORTCUTS = FILE_EXPLORER_SHORTCUTS
        self.messagesWidget = messagesWidget
        self.editorTabWidget = editorTabWidget

        self.manageShortcuts = ManageShortcuts(
            useData, self.FILE_EXPLORER_SHORTCUTS, self)
        self.manageShortcuts.updateShortcuts.connect(
            self.updateShortcutsActionGroup)
        editorTabWidget.addToolWidget(self.manageShortcuts)

        self.createActions()
        self.shortcutsMenu = QtGui.QMenu("Shortcuts")
        self.updateShortcutsActionGroup()

    def contextMenuEvent(self, event):
        self.contextMenu = QtGui.QMenu()

        self.contextMenu.addAction(self.homeAct)
        self.contextMenu.addAction(self.showAllFilesAct)
        self.contextMenu.addAction(self.collapseAllAct)
        indexList = self.selectedIndexes()
        if len(indexList) != 0:
            self.contextMenu.addAction(self.createShortcutAct)
            self.contextMenu.addAction(self.locateAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addMenu(self.shortcutsMenu)
        self.contextMenu.addAction(self.manageShortcutsAct)

        self.contextMenu.exec_(event.globalPos())

    def createActions(self):
        self.homeAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "home")),
            "Home", self,
            statusTip="Home", triggered=self.refreshFileSytemModel)

        self.collapseAllAct = \
            QtGui.QAction(
                "Collapse All", self,
                statusTip="Collapse Tree", triggered=self.collapseAll)

        self.showAllFilesAct = \
            QtGui.QAction(
                "Show All Files", self, statusTip="Show All Files",
                toggled=self.showAllFiles)
        self.showAllFilesAct.setCheckable(True)
        self.showAllFilesAct.setChecked(True)

        self.locateAct = \
            QtGui.QAction("Locate", self, statusTip="Locate",
                          triggered=self.locate)

        self.createShortcutAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "brainstorming")),
                "Create Shortcut", self, statusTip="Create Shortcut",
                triggered=self.createShortcut)

        self.manageShortcutsAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "settings")),
                "Manage Shortcuts", self, statusTip="Manage Shortcuts",
                triggered=self.showManageShortcuts)

    def showManageShortcuts(self):
        self.editorTabWidget.showMe(self.manageShortcuts)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if os.path.isdir(urls[0].toLocalFile()):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            urls = event.mimeData().urls()
            dirname = urls[0].toLocalFile()
            self.loadShortcut(dirname)
        else:
            pass
        event.acceptProposedAction()

    def updateShortcutsActionGroup(self):
        if len(self.FILE_EXPLORER_SHORTCUTS) > 0:
            self.shortcuts_actionGroup = QtGui.QActionGroup(self)
            self.shortcuts_actionGroup.triggered.connect(
                self.shortcutActivated)
            self.shortcutsMenu.clear()
            for i in self.FILE_EXPLORER_SHORTCUTS:
                action = QtGui.QAction(i, self)
                self.shortcuts_actionGroup.addAction(action)
                self.shortcutsMenu.addAction(action)
            self.shortcutsMenu.addSeparator()
        else:
            self.shortcutsMenu.addAction("No Shortcuts")
        # TODO findInFiles.updateShortcutsList()

    def shortcutActivated(self, action):
        path = action.text()
        self.loadShortcut(path)

    def loadShortcut(self, path):
        if os.path.exists(path):
            self.setRootIndex(self.fileSystemModel.index(path))
        else:
            message = QtGui.QMessageBox.warning(self, "Open",
                                                "Directory is not available.")

    def showAllFiles(self):
        if self.showAllFilesAct.isChecked():
            self.fileSystemModel.setNameFilters([])
        else:
            self.fileSystemModel.setNameFilters(['*.py', '*.pyw'])

    def refreshFileSytemModel(self):
        self.fileSystemModel = QtGui.QFileSystemModel()
        self.fileSystemModel.setRootPath(QtCore.QDir.rootPath())
        if self.showAllFilesAct.isChecked():
            self.fileSystemModel.setNameFilters(['*.py', '*.pyw'])
        self.fileSystemModel.setNameFilterDisables(False)
        self.setModel(self.fileSystemModel)
        self.setColumnWidth(0, 300)

    def treeItemActivated(self, modelIndex):
        if self.fileSystemModel.isDir(modelIndex) is False:
            filePath = os.path.normpath(
                self.fileSystemModel.filePath(modelIndex))
            self.fileActivated.emit(filePath)
        else:
            if self.isExpanded(modelIndex):
                self.collapse(modelIndex)
            else:
                self.expand(modelIndex)

    def createShortcut(self):
        indexList = self.selectedIndexes()
        if len(indexList) == 0:
            path_index = self.rootIndex()
        else:
            path_index = indexList[0]
        path = os.path.normpath(self.fileSystemModel.filePath(path_index))
        if os.path.isfile(path):
            # save in parent directory
            path = os.path.normpath(
                self.fileSystemModel.filePath(path_index.parent()))
        else:
            pass
        mess = 'Create shortcut to "{0}"?'.format(path)
        reply = QtGui.QMessageBox.information(self, "Create Shortcut",
                                              mess, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            # save shortcut
            if path in self.FILE_EXPLORER_SHORTCUTS:
                return
            self.FILE_EXPLORER_SHORTCUTS.append(path)
            self.updateShortcutsActionGroup()
            self.messagesWidget.addMessage(0, "Shortcuts",
                                           ["'{0}' added!".format(path)])

    def locate(self):
        indexList = self.selectedIndexes()
        if len(indexList) == 0:
            path_index = self.rootIndex()
            file_path = \
                os.path.normpath(self.fileSystemModel.filePath(path_index))
        else:
            path_index = indexList[0]
            file_path = \
                os.path.normpath(self.fileSystemModel.filePath(path_index))
        ctypes.windll.shell32.ShellExecuteW(None, 'open', 'explorer.exe',
                                            '/n,/select, ' + file_path, None, 1)
