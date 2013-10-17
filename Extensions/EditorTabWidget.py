import os
import ctypes
import time

from PyQt4 import QtCore, QtGui, QtXml
from PyQt4.Qsci import QsciScintilla

from Extensions.Diff import DiffWindow
from Extensions.CodeEditor import CodeEditor
from Extensions.TextEditor import TextEditor
from Extensions.ViewSwitcher import ViewSwitcher
from Extensions.TextSnapshot import TextSnapshot
from Extensions.CodeSnapshot import CodeSnapshot
from Extensions.GotoLineWidget import GotoLineWidget
from Extensions.EditorSplitter import EditorSplitter
from Extensions import Global
from Extensions.Refactor.Refactor import Refactor
from Extensions.RunWidget import SetRunParameters
from Extensions.Projects.ProjectManager.ConfigureProject import ConfigureProject
from Extensions import StyleSheet


class EditorTabBar(QtGui.QTabBar):

    def __init__(self, app, renameFileAct,
                 moduleToPackageAct, parent):
        QtGui.QTabBar.__init__(self, parent)

        self.setExpanding(True)
        self.setDrawBase(False)

        self.editorTabWidget = parent
        self.app = app
        self.renameFileAct = renameFileAct
        self.moduleToPackageAct = moduleToPackageAct

        self.createActions()

    def setShortcuts(self):
        shortcuts = self.editorTabWidget.useData.CUSTOM_SHORTCUTS

        self.shortSplitFileReload = QtGui.QShortcut(
            shortcuts["Ide"]["Reload-File"], self)
        self.shortSplitFileReload.activated.connect(
            self.reload)
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

        self.menu.exec_(event.globalPos())

    def createActions(self):
        self.closeTabAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "cross_")),
            "Close", self, statusTip="Close Tab", triggered=self.closeTab)

        self.copyPathAct = QtGui.QAction("Copy File Path", self,
                                         statusTip="Copy File Path", triggered=self.copyPath)

        self.openFileLocationAct = \
            QtGui.QAction(
                "Open File Location", self, statusTip="Open File Location",
                triggered=self.openFileLocation)

        self.cloneTabAct = \
            QtGui.QAction(
                "Clone", self, statusTip="Create a copy of current tab",
                triggered=self.cloneTab)

        self.reloadTabAct = \
            QtGui.QAction(
                "Reload", self, statusTip="Reload",
                triggered=self.reload)

        self.favouritesAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "plus")),
                "Add to Favourites", self,
                statusTip="Add to Favourites",
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
        reply = QtGui.QMessageBox.warning(self, "Reload",
                                          "Do you really want to reload?",
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.editorTabWidget.reloadModules()
        else:
            return

    def closeTab(self):
        index = self.currentIndex()
        self.editorTabWidget.closeEditorTab(index)

    def copyPath(self):
        filePath = self.editorTabWidget.getEditorData('filePath')
        cb = self.app.clipboard()
        cb.setText(filePath)

    def openFileLocation(self):
        filePath = self.editorTabWidget.getEditorData('filePath')
        ctypes.windll.shell32.ShellExecuteW(None, 'open', 'explorer.exe',
                                            '/n,/select, ' + filePath, None, 1)

    def cloneTab(self):
        index = self.currentIndex()
        name = self.tabText(index)
        new_index = index + 1
        subStack = self.editorTabWidget.newEditor(new_index, name)
        self.editorTabWidget.setCurrentIndex(new_index)
        self.editorTabWidget.updateTabName(new_index)
        editor = subStack.widget(0).widget(0)
        editor.setText(self.editorTabWidget.getEditor(index).text())


class EditorTabWidget(QtGui.QTabWidget):

    currentEditorTextChanged = QtCore.pyqtSignal()
    bookmarksChanged = QtCore.pyqtSignal()
    updateLinesCount = QtCore.pyqtSignal(int)
    updateRecentFilesList = QtCore.pyqtSignal(str)
    updateWindowTitle = QtCore.pyqtSignal(str)
    updateEncodingLabel = QtCore.pyqtSignal(str)
    cursorPositionChanged = QtCore.pyqtSignal()

    def __init__(
        self, useData, projectPathDict, projectSettings, messagesWidget, colorScheme, busyWidget, bookmarkToolbar,
            app, manageFavourites, externalLauncher, editorWindow, parent=None):
        QtGui.QTabWidget.__init__(self, parent)

        self.setElideMode(1)

        self.useData = useData
        self.projectPathDict = projectPathDict
        self.colorScheme = colorScheme
        self.messagesWidget = messagesWidget
        self.app = app
        self.busyWidget = busyWidget
        self.projectSettings = projectSettings
        self.bookmarkToolbar = bookmarkToolbar
        self.editorWindow = editorWindow

        self.toolWidgetList = []
        # backup keys are generated from the system time, but sometimes
        # tabs are loaded so fast they end up having same backup keys.
        # this variable is an int that will will be incremented for every
        # backup kry that is generated and will be used to prevent key
        # collision
        self.backupKeyDiferentiator = 0

        self.backupTimer = QtCore.QTimer()
        self.backupTimer.setSingleShot(False)
        self.backupTimer.setInterval(60000)
        self.backupTimer.timeout.connect(self.createBackup)

        self.configDialog = ConfigureProject(
            projectPathDict, projectSettings, useData, self)

        self.manageFavourites = manageFavourites
        self.manageFavourites.showMe.connect(self.showFavouritesManager)

        self.externalLauncher = externalLauncher
        self.externalLauncher.showMe.connect(self.showExternalLauncher)

        self.setRunParameters = SetRunParameters(
            self.projectSettings, self.projectPathDict, self.useData)

        self.refactor = Refactor(
            self, self.busyWidget, self)

        self.viewSwitcher = ViewSwitcher(self)
        self.gotoLineWidget = GotoLineWidget(self)

        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        if self.useData.SETTINGS["UI"] == "Custom":
            self.adjustToStyleSheet(True)
        else:
            self.adjustToStyleSheet(False)

        self.topVBox = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.topVBox)

        self.mainLayout.addStretch(1)

        self.addToolWidget(self.configDialog)
        self.addToolWidget(self.externalLauncher)
        self.addToolWidget(self.manageFavourites)
        self.addToolWidget(self.setRunParameters)
        self.addToolWidget(self.viewSwitcher)
        self.addToolWidget(self.gotoLineWidget)

        self.filesWatch = QtCore.QFileSystemWatcher()
        self.filesWatch.fileChanged.connect(self.fileChanged)

        self.createActions()

        self.tabBar = EditorTabBar(self.app,
                                   self.refactor.renameModuleAct,
                                   self.refactor.moduleToPackageAct, self)
        self.tabBar.setMovable(True)
        self.tabBar.setTabsClosable(True)

        self.openedTabsMenu = QtGui.QMenu()

        self.tabSelectButton = QtGui.QToolButton()
        self.tabSelectButton.setAutoRaise(True)
        self.tabSelectButton.setPopupMode(2)
        self.tabSelectButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "tile")))
        self.tabSelectButton.setMenu(self.openedTabsMenu)

        self.setTabBar(self.tabBar)
        self.setAcceptDrops(True)
        self.setUsesScrollButtons(True)
        self.setCornerWidget(self.tabSelectButton)
        self.currentChanged.connect(self.editorTabChanged)
        self.tabCloseRequested.connect(self.closeEditorTab)

        self.setShortcuts()
        self.backupTimer.start()

        self.newFileMenu = QtGui.QMenu("New File")
        self.newFileMenu.addAction(self.newPythonFileAct)
        self.newFileMenu.addAction(self.newXmlFileAct)
        self.newFileMenu.addAction(self.newHtmlFileAct)
        self.newFileMenu.addAction(self.newCssFileAct)

    def resizeView(self, hview, vview):
        self.editorWindow.resizeView(hview, vview)

    def adjustToStyleSheet(self, adjust):
        if adjust:
            self.mainLayout.setContentsMargins(0, 22, 14, 12)
        else:
            self.mainLayout.setContentsMargins(0, 24, 25, 12)

    def addToolWidget(self, widget):
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(widget)
        self.topVBox.addLayout(hbox)

        self.toolWidgetList.append(widget)
        widget.hide()

    def createActions(self):
        self.undoAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "undo")),
            "Undo", self,
            statusTip="Undo last edit action",
            triggered=self.undoAction)

        self.redoAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "redo")),
            "Redo", self,
            statusTip="Redo last edit action",
            triggered=self.redoAction)

        self.cutAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "cut")),
            "Cut", self,
            statusTip="Cut selected text", triggered=self.cutItem)

        self.copyAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "copy")),
            "Copy", self,
            statusTip="Copy selected text", triggered=self.copyItem)

        self.pasteAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "paste")),
            "Paste", self,
            statusTip="Paste text from clipboard",
            triggered=self.pasteFromClipboard)

        #----------------------------------------------------------------------

        self.indentAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "increase_indent")),
                "Indent", self,
                statusTip="Indent Region",
                triggered=self.increaseIndent)

        self.dedentAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "decrease_indent")),
                "Unindent", self,
                statusTip="Unindent Region",
                triggered=self.decreaseIndent)

        self.writeLockAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "block")),
                "Write Lock", self,
                statusTip="Write Lock",
                          triggered=self.writeLock)

        self.findNextBookmarkAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "Arrow2-down")),
                "Next Bookmark", self, statusTip="Next Bookmark",
                triggered=self.findNextBookmark)

        self.findPrevBookmarkAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "Arrow2-up")),
                "Previous Bookmark", self, statusTip="Previous Bookmark",
                triggered=self.findPreviousBookmark)

        self.removeBookmarksAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "block__")),
                "Remove Bookmarks", self, statusTip="Remove Bookmarks",
                triggered=self.removeBookmarks)
        #---------------------------------------------------------------------
        self.newPythonFileAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "new")),
            "New Python File", self,
            statusTip="Create a new python file",
            triggered=self._newPythonFile)

        self.newXmlFileAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "new")),
            "Xml", self,
            statusTip="Create a new Xml file",
            triggered=self._newXmlFile)

        self.newHtmlFileAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "new")),
            "Html", self,
            statusTip="Create a new Html file",
            triggered=self._newHtmlFile)

        self.newCssFileAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "new")),
            "Css", self,
            statusTip="Create a new Css file",
            triggered=self._newCssFile)

        self.openFileAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "open_file")),
                "Open File...", self,
                statusTip="Open python file",
                          triggered=self.openFile)

        self.saveAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "save_")),
            "Save", self,
            statusTip="Save", triggered=self._save)

        self.saveAllAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "disks-black")),
                "Save All", self,
                statusTip="Save All",
                          triggered=self.saveAll)

        self.saveAsAct = QtGui.QAction("Save As...", self, statusTip="Save",
                                       triggered=self.saveAs)

        self.saveCopyAsAct = QtGui.QAction("Save Copy As...",
                                           self, statusTip="Save Copy As",
                                           triggered=self.saveCopyAs)

        self.printAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "_0013_Printer")),
                "Print", self,
                statusTip="Print", triggered=self.printCode)
        #----------------------------------------------------------------------

        self.vSplitEditorAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "border-horizontal")),
                "Split Vertical", self,
                statusTip="Split Vertical", triggered=self.splitVertical)

        self.hSplitEditorAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "border-vertical")),
                "Split Horizontal", self,
                statusTip="Split Horizontal", triggered=self.splitHorizontal)

        self.noSplitEditorAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "border")),
                "Remove Split", self,
                statusTip="Remove Split", triggered=self.removeSplit)

    def addToFavourites(self):
        path = self.getEditorData("filePath")
        self.manageFavourites.addToFavourites(path)

    def fileChanged(self, file):
        if os.path.exists(file):
            pass
        else:
            for i in range(self.count()):
                path = self.getEditorData("filePath", i)
                if path == file:
                    self.updateEditorData("filePath", None, i)
                    self.showNotification(
                        "File renamed or moved.", i)
                    break

    def focusedEditor(self, index=None):
        if index is None:
            index = self.currentIndex()
        subStack = self.widget(index)
        return subStack.widget(0).getFocusedEditor()

    def getEditor(self, index=None):
        if index is None:
            index = self.currentIndex()
        subStack = self.widget(index)
        return subStack.widget(0).getEditor(0)

    def getCloneEditor(self, index=None):
        if index is None:
            index = self.currentIndex()
        return self.widget(index).widget(0).getEditor(1)

    def getSnapshot(self, index=None):
        if index is None:
            index = self.currentIndex()
        return self.widget(index).widget(1)

    def getUnifiedDiff(self, index=None):
        if index is None:
            index = self.currentIndex()
        return self.widget(index).widget(2)

    def getContextDiff(self, index=None):
        if index is None:
            index = self.currentIndex()
        return self.widget(index).widget(3)

    def clearMarkerAndIndicators(self):
        self.currentEditor.clearMarkerAndIndicators()

    def splitVertical(self):
        splitter = self.currentWidget().widget(0)
        splitter.setOrientation(2)
        splitter.widget(1).show()

    def splitHorizontal(self):
        splitter = self.currentWidget().widget(0)
        splitter.setOrientation(1)
        splitter.widget(1).show()

    def removeSplit(self):
        splitter = self.currentWidget().widget(0)
        splitter.widget(1).hide()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if os.path.isfile(urls[0].toLocalFile()):
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
            fname = urls[0].toLocalFile()
            self.loadfile(os.path.normpath(fname))
        else:
            pass
        event.acceptProposedAction()

    def showNotification(self, message, index=None):
        if index is None:
            index = self.currentIndex()
        self.focusedEditor(index).notification.showMessage(message)

    def undoAction(self):
        self.currentEditor.undo()

    def redoAction(self):
        self.currentEditor.redo()

    def cutItem(self):
        self.currentEditor.cut()

    def copyItem(self):
        self.currentEditor.copy()

    def deleteItem(self):
        self.currentEditor.removeSelectedText()

    def selectAll(self):
        self.currentEditor.selectAll()

    def selectToMatchingBrace(self):
        self.currentEditor.selectToMatchingBrace()

    def clearBackups(self):
        # empty backups
        for i in os.listdir(self.projectPathDict["backupdir"]):
            remPath = os.path.join(self.projectPathDict["backupdir"], i)
            try:
                os.remove(remPath)
            except:
                pass

    def createBackup(self):
        for i in range(self.count()):
            key = self.getEditorData("backupKey", i)
            editor = self.getEditor(i)

            savePath = os.path.join(self.projectPathDict["backupdir"], key)

            file = open(savePath, 'w')
            file.write(editor.text())
            file.close()
        self.saveSession(True)

    def saveSession(self, backup=False):
        dom_document = QtXml.QDomDocument("session")

        session = dom_document.createElement("session")
        dom_document.appendChild(session)

        for i in range(self.count()):
            editor = self.getEditor(i)

            tag = dom_document.createElement("file")
            path = self.getEditorData("filePath", i)
            if not backup:
                if path is None:
                    continue
            tag.setAttribute("path", path)

            path = str(self.getEditorData("filePath", i))
            tag.setAttribute("active", str(
                self.currentEditor == editor))

            locked = editor.isReadOnly()
            tag.setAttribute("locked", str(locked))

            tag.setAttribute("lines", str(editor.lines()))

            line, index = editor.getCursorPosition()
            tag.setAttribute("cursorPosition", str(line) + ',' + str(index))

            firstVisibleLine = editor.firstVisibleLine()
            tag.setAttribute("firstVisibleLine", str(firstVisibleLine))

            bookmarkLines = editor.getBookmarks()
            tag.setAttribute("bookmarks",
                             str(bookmarkLines).replace(', ', '-').strip('[]'))

            folds = editor.contractedFolds()
            tag.setAttribute("folds",
                             str(folds).replace(', ', '-').strip('[]'))

            if backup:
                key = self.getEditorData("backupKey", i)
                tag.setAttribute("backupKey", key)
                tag.setAttribute("baseName", self.tabText(i))

            session.appendChild(tag)

        if backup:
            savePath = self.projectPathDict["backupfile"]
        else:
            savePath = self.projectPathDict["session"]
        file = open(savePath, "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

    def restoreSession(self):
        # TODO: When backup is True and it turns out empty because
        # it previousely loaded from backup, cleared it's backup
        # cache and was instantly shut down again, the previous
        # session must be reloaded.
        backup = self.projectSettings["LastCloseSuccessful"] == "False"

        if backup:
            loadPath = self.projectPathDict["backupfile"]
        else:
            self.clearBackups()
            loadPath = self.projectPathDict["session"]

        file = open(loadPath, "r")
        dom_document = QtXml.QDomDocument()
        dom_document.setContent(file.read())
        file.close()

        elements = dom_document.documentElement()
        node = elements.firstChild()
        activeIndex = 0
        currentIindex = 0
        restoredBackups = 0
        while node.isNull() is False:
            try:
                tag = node.toElement()
                if backup:
                    backupKey = tag.attribute("backupKey")
                    basename = tag.attribute("baseName")
                    backupPath = os.path.join(
                        self.projectPathDict["backupdir"], backupKey)
                    realPath = tag.attribute("path")
                    if realPath == '':
                        file = open(backupPath, 'r')
                        backupText = file.read()
                        file.close()

                        subStack = self.newEditor(currentIindex)
                        editor = subStack.widget(0).widget(0)
                        editor.setText(backupText)
                        editor.setModified(False)
                        editor.setFocus()

                        restoredBackups += 1
                    else:
                        real_mod_time = os.stat(realPath).st_mtime
                        backup_mod_time = os.stat(backupPath).st_mtime
                        if real_mod_time > backup_mod_time:
                            pass
                        else:
                            file = open(backupPath, 'r')
                            backupText = file.read()
                            file.close()

                            file = open(realPath, "w")
                            file.write(backupText)
                            file.close()

                            restoredBackups += 1

                        path = tag.attribute("path")
                        loaded = self.loadfile(path, False, currentIindex)
                else:
                    path = tag.attribute("path")
                    loaded = self.loadfile(path, False, currentIindex)
                if loaded is False:
                    node = node.nextSibling()
                    continue

                locked = tag.attribute("locked")
                if locked == 'True':
                    self.writeLock()
                lines = tag.attribute("lines")
                active = tag.attribute("active")
                if active == 'True':
                    activeIndex = currentIindex
                cp = tag.attribute("cursorPosition").split(',')
                line = int(cp[0])
                index = int(cp[1])

                firstVisibleLine = int(tag.attribute("firstVisibleLine"))

                editor = self.getEditor()
                editor.setCursorPosition(line, 0)
                editor.setFirstVisibleLine(firstVisibleLine)

                m = tag.attribute("bookmarks")
                if m != '':
                    bookmarks = list(map(int, m.split('-')))
                    for line in bookmarks:
                        editor.toggleBookmark(1, line)

                folds = tag.attribute("folds")
                if folds != '':
                    folds = list(map(int, folds.split('-')))
                    editor.setContractedFolds(folds)

                currentIindex += 1
                node = node.nextSibling()
            except Exception:
                node = node.nextSibling()
        if self.count() != 0:
            self.setCurrentIndex(activeIndex)
        if self.count() == 0:
            self._newPythonFile()

        self.clearBackups()
        if restoredBackups > 0:
            self.messagesWidget.addMessage(
                0, "Restored", [str(restoredBackups) + ' file(s) restored from previous crash.'])

    def getSource(self, index=None):
        if index is None:
            return self.getEditor().text()
        else:
            return self.getEditor(index).text()

    def getSelection(self):
        return self.currentEditor.selectedText()

    def closeEditorTab(self, index):
        if self.getEditor(index).isModified():
            self.requestSaveMess(index)
        else:
            if self.count() == 1:
                self._newPythonFile()
            self.removeTabBackup(index)
            path = self.getEditorData('filePath')
            if path is None:
                self.filesWatch.removePath(path)
            self.removeTab(index)
            self.updateOpenedTabsMenu()

    def editorTabChanged(self, index):
        self.currentEditor = self.getEditor()
        self.cloneEditor = self.getCloneEditor()
        self.currentEditor.undoActModifier()
        self.currentEditor.redoActModifier()
        self.currentEditor.copyActModifier()

        if self.getEditorData("filePath") is None:
            self.updateWindowTitle.emit("Unsaved")
            self.updateEncodingLabel.emit("Coding: {0}".format(
                self.getEditorData("codingFormat")))
        else:
            self.updateWindowTitle.emit(self.getEditorData("filePath"))
            self.updateEncodingLabel.emit("Coding: {0}".format(
                self.getEditorData("codingFormat")))

        self.enableBookmarkButtons(self.currentEditor.bookmarksExist())
        self.currentEditor.updateLineCount()
        self.cursorPositionChanged.emit()
        self.updateOpenedTabsMenu()

    def enableBookmarkButtons(self, enable):
        self.bookmarkToolbar.setEnabled(enable)
        self.bookmarksChanged.emit()

    def makeCurrentTab(self, action):
        self.setCurrentIndex(action.data())

    def updateOpenedTabsMenu(self):
        self.openedTabsActionGroup = QtGui.QActionGroup(self)
        self.openedTabsActionGroup.setExclusive(True)
        self.openedTabsActionGroup.triggered.connect(self.makeCurrentTab)
        self.openedTabsMenu.clear()
        for i in range(self.count()):
            name = self.tabText(i)
            action = QtGui.QAction(name, self)
            action.setCheckable(True)
            if self.currentIndex() == i:
                action.setChecked(True)
            action.setData(i)
            self.openedTabsActionGroup.addAction(action)
            self.openedTabsMenu.addAction(action)

    def pasteFromClipboard(self):
        self.focusedEditor().paste()

    def increaseIndent(self):
        self.focusedEditor().increaseIndent()

    def decreaseIndent(self):
        self.focusedEditor().decreaseIndent()

    def showMe(self, widget):
        for toolWidget in self.toolWidgetList:
            toolWidget.hide()
        widget.show()

    def showProjectConfiguration(self):
        self.showMe(self.configDialog)

    def showGotoLineWidget(self):
        self.showMe(self.gotoLineWidget)
        self.gotoLineWidget.lineNumberLine.setFocus(True)

    def showSnapShotSwitcher(self):
        self.showMe(self.viewSwitcher)

    def showSetRunParameters(self):
        if self.setRunParameters.isVisible():
            self.setRunParameters.hide()
        else:
            self.showMe(self.setRunParameters)

    def showFavouritesManager(self):
        self.showMe(self.manageFavourites)

    def showExternalLauncher(self):
        self.showMe(self.externalLauncher)

    def showLine(self, lineNum, highlight=True):
        self.focusedEditor().showLine(lineNum, highlight)

    def writeLock(self):
        if self.focusedEditor().isReadOnly() is False:
            self.focusedEditor().setReadOnly(True)
            self.setTabIcon(self.currentIndex(),
                            QtGui.QIcon(os.path.join("Resources", "images", "locked_script")))
        else:
            self.focusedEditor().setReadOnly(False)
            if self.getEditorData("fileType") == "python":
                if self.focusedEditor().isModified():
                    self.setTabIcon(self.currentIndex(),
                                    QtGui.QIcon(os.path.join("Resources", "images", "script_grey")))
                else:
                    self.setTabIcon(self.currentIndex(),
                                    QtGui.QIcon(os.path.join("Resources", "images", "script")))
            else:
                self.setTabIcon(self.currentIndex(),
                                Global.iconFromPath(self.getEditorData("filePath")))

    def findNextBookmark(self):
        editor = self.focusedEditor()
        editor.findNextBookmark()

    def findPreviousBookmark(self):
        editor = self.focusedEditor()
        editor.findPreviousBookmark()

    def removeBookmarks(self):
        reply = QtGui.QMessageBox.warning(self, "Remove Bookmarks",
                                          "Do you really want to remove all bookmarks?",
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            pass
        else:
            return
        self.currentEditor.removeBookmarks()
        self.enableBookmarkButtons(False)

    def goToCursorPosition(self):
        line, index = self.focusedEditor().getCursorPosition()
        self.focusedEditor().showLine(line, False)

    def comment(self):
        self.focusedEditor().comment()

    def unComment(self):
        self.focusedEditor().unComment()

    def errorsInProject(self):
        errors = False
        for i in range(self.count()):
            path = self.getEditorData("filePath", i)
            if path is not None:
                if self.isProjectFile(path):
                    if self.getEditorData("fileType", i) == "python":
                        errorLine = self.getEditorData("errorLine", i)
                        if errorLine is not None:
                            errors = True
                            self.setCurrentIndex(i)
                            break
        return errors

    def isProjectFile(self, filePath):
        if filePath is None:
            return False
        return filePath.startswith(self.projectPathDict["sourcedir"])

    def getTabName(self, tabIndex=None):
        if tabIndex is None:
            name = self.tabText(self.currentIndex())
        else:
            name = self.tabText(tabIndex)
        return name

    def getEditorData(self, attrib, tabIndex=None):
        if tabIndex is None:
            tabIndex = self.currentIndex()
        else:
            pass
        data = self.widget(tabIndex).widget(0).DATA[attrib]
        return data

    def updateEditorData(self, attrib, value, tabIndex=None):
        if tabIndex is None:
            tabIndex = self.currentIndex()
        else:
            pass
        self.getEditor(tabIndex).DATA[attrib] = value
        if attrib == "filePath":
            if value is None:
                self.updateWindowTitle.emit("Unsaved")
            else:
                self.setTabText(tabIndex, os.path.basename(value))
                self.updateWindowTitle.emit(value)

    def updateTabName(self, index=None):
        if index is None:
            index = self.currentIndex()
        else:
            pass
        path = self.getEditorData("filePath", index)
        if path is None:
            return
        text = os.path.basename(path)
        editor = self.getEditor(index)
        if editor.isModified():
            text = text + " *"
        self.setTabText(index, text)
        self.setTabToolTip(index, path)

    def removeTabBackup(self, tabIndex):
        key = self.getEditorData("backupKey", tabIndex)
        try:
            os.remove(os.path.join(self.projectPathDict["backupdir"], key))
        except:
            pass

    def requestSaveMess(self, tabIndex):
        mess = "Save changes to '{0}'?".format(self.tabText(tabIndex))
        reply = QtGui.QMessageBox.information(self, "Save", mess,
                                              QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                                              QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Save:
            self.save()
        elif reply == QtGui.QMessageBox.Discard:
            if self.count() == 1:
                self.newFile()
            self.removeTabBackup(tabIndex)
            self.removeTab(tabIndex)

    def _save(self):
        self.save()

    def save(self, index=None):
        if index is None:
            index = self.currentIndex()
        savePath = self.getEditorData("filePath", index)
        if savePath is None:
            saved = self.saveAs(index)
            return saved
        else:
            try:
                file = open(savePath, "w")
                editor = self.getEditor(index)
                file.write(editor.text())
                file.close()
                editor.setModified(False)

                return True
            except Exception as err:
                self.saveErrorMess(str(err))

                return False

    def saveToTemp(self, type, index=None):
        if index is None:
            index = self.currentIndex()
        try:
            if type == 'pep8':
                file = open(os.path.join("temp", "temp8.py"), "w")
            editor = self.getEditor(index)
            file.write(editor.text())
            file.close()
            return True
        except Exception as err:
            return False

    def saveAs(self, index=None, copyOnly=False):
        options = QtGui.QFileDialog.Options()
        filter = self.getFilter()
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Save As", os.path.join(self.useData.getLastOpenedDir(),
                                                                             self.getTabName()), filter, options)
        if fileName:
            self.useData.saveLastOpenedDir(os.path.split(fileName)[0])
            try:
                if index is None:
                    index = self.currentIndex()
                fileName = os.path.normpath(fileName)
                editor = self.getEditor(index)
                file = open(fileName, "w")
                file.write(editor.text())
                file.close()
                editor.setModified(False)
                self.updateTabName(index)
                if not copyOnly:
                    self.updateEditorData("filePath", fileName)
                self.filesWatch.addPath(fileName)
                return True
            except Exception as err:
                self.saveErrorMess(str(err.args[1]))
                return False
        else:
            return False

    def saveCopyAs(self):
        self.saveAs(copyOnly=True)

    def getFilter(self):
        fileType = self.getEditorData("fileType")
        if fileType == "python":
            filter = "Console (*.py);;No Console (*.pyw)"
        elif fileType == ".xml":
            filter = "Xml (*.xml)"
        elif fileType == ".html":
            filter = "Html (*.html)"
        elif fileType == ".css":
            filter = "Css (*.css)"
        else:
            filter = "All Files (*)"
        return filter

    def saveAll(self):
        for i in range(self.count()):
            self.save(i)

    def saveProject(self):
        saved = True
        source_dir = self.projectPathDict["sourcedir"]
        for i in range(self.count()):
            path = self.getEditorData("filePath", i)
            if path is not None:
                if self.isProjectFile(path):
                    # its a project file
                    editor = self.getEditor(i)
                    if editor.isModified():
                        saved = self.save(i)
                        if not saved:
                            break
        return saved

    def saveErrorMess(self, mess):

        message = QtGui.QMessageBox.critical(self,
                                             "Save", "Error saving file!\n\n" + mess)

    def printCode(self):
        document = self.currentEditor.document()
        printer = QtGui.QPrinter()

        dlg = QtGui.QPrintDialog(printer, self)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        document.print_(printer)

    def openFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     "Select File", self.useData.getLastOpenedDir(
                                                     ),
                                                     "All Files (*);;Console (*.py);;No Console (*.pyw);;Xml (*.xml);;Html (*.html);;Css (*.css)")
        if fileName:
            self.useData.saveLastOpenedDir(os.path.split(fileName)[0])
            self.loadfile(os.path.normpath(fileName))

    def _newPythonFile(self):
        self.newEditor()

    def _newXmlFile(self):
        self.newEditor(fileName="Untitled.xml")

    def _newHtmlFile(self):
        self.newEditor(fileName="Untitled.html")

    def _newCssFile(self):
        self.newEditor(fileName="Untitled.css")

    def newEditor(self, index=None, fileName="Untitled.py",
                  filePath=None, encoding=None):
        extension = os.path.splitext(fileName)[1].lower()
        pyFile = extension in [".py", ".pyw"]
        if pyFile:
            extension = "python"

        DATA = {}
        DATA["filePath"] = filePath
        DATA["backupKey"] = str(time.time()) + '.' + str(
            self.backupKeyDiferentiator)
        self.backupKeyDiferentiator += 1
        DATA["bookmarkList"] = []

        if encoding is None:
            DATA["codingFormat"] = "utf-8"
        else:
            DATA["codingFormat"] = encoding
        if pyFile:
            DATA["errorLine"] = None
            DATA["fileType"] = "python"
            editor = CodeEditor(self.useData, self.refactor, self.colorScheme,
                                DATA, self)
            editor2 = CodeEditor(self.useData, self.refactor, self.colorScheme,
                                 DATA, self)
            snapShot = CodeSnapshot(self.useData, self.colorScheme)
        else:
            if extension in [".htm", ".html"]:
                extension = ".html"
            DATA["fileType"] = extension
            editor = TextEditor(self.useData, DATA, self.colorScheme, self,
                                encoding)
            editor2 = TextEditor(self.useData, DATA, self.colorScheme, self,
                                 encoding)
            snapShot = TextSnapshot(self.useData, self.colorScheme, extension)
        mode = QsciScintilla.EolUnix
        editor.setEolMode(mode)
        editor2.setEolMode(mode)
        snapShot.setEolMode(mode)

        snapShot.setReadOnly(True)
        subStack = QtGui.QStackedWidget()
        editorSplitter = EditorSplitter(editor, editor2, DATA, self, subStack)
        editor2.setDocument(editor.document())
        subStack.addWidget(editorSplitter)
        subStack.addWidget(snapShot)
        diffWindow = DiffWindow(editor, snapShot)
        diffWindow.setStyleSheet(StyleSheet.editorStyle)
        subStack.addWidget(diffWindow)
        diffWindow = DiffWindow(editor, snapShot)
        diffWindow.setStyleSheet(StyleSheet.editorStyle)
        subStack.addWidget(diffWindow)

        if extension in self.useData.supportedFileTypes:
            icon = QtGui.QIcon(os.path.join("Resources", "images", "script"))
        else:
            icon = Global.iconFromPath(filePath)
        if index is None:
            index = self.currentIndex()
        self.insertTab(index, subStack, icon, fileName)

        if filePath is None:
            pass
        else:
            self.filesWatch.addPath(filePath)

        editor.textChanged.connect(self.currentEditorTextChanged.emit)
        editor.cursorPositionChanged.connect(self.cursorPositionChanged.emit)
        editor2.cursorPositionChanged.connect(self.cursorPositionChanged.emit)

        self.setCurrentWidget(subStack)

        return subStack

    def reloadModules(self, pathList=[]):
        index_list = []
        currentIndex = self.currentIndex()
        if len(pathList) == 0:
            index_list.append(currentIndex)
        else:
            for i in range(self.count()):
                path = self.getEditorData("filePath", i)
                if path in pathList:
                    index_list.append(i)
        for i in index_list:
            filePath = self.getEditorData("filePath", i)
            editor = self.getEditor(i)
            text, encoding, eolMode = self.useData.readFile(filePath)
            firstLine = editor.firstVisibleLine()
            editor.setText(text)
            editor.convertEols(eolMode)
            editor.setEolMode(eolMode)
            editor.setFirstVisibleLine(firstLine)
            editor.setModified(False)
            if i == currentIndex:
                self.getEditor(i).removeBookmarks()
                self.enableBookmarkButtons(False)

    def alreadyOpened(self, filePath):
        for i in range(self.count()):
            fpath = self.getEditorData("filePath", i)
            if fpath is None:
                pass
            else:
                if os.path.samefile(fpath, filePath):
                    self.setCurrentIndex(i)
                    return True
        return False

    def loadfile(self, filePath, showError=True, index=None):

        filePath = os.path.normpath(filePath)
        # prevent same file from being opened more than once
        if self.alreadyOpened(filePath):
            return True

        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            text, encoding, eolMode = self.useData.readFile(filePath)
            baseName = os.path.basename(filePath)
            subStack = self.newEditor(index, baseName, filePath, encoding)

            editor = subStack.widget(0).widget(0)
            editor.setText(text)
            editor.convertEols(eolMode)
            editor.setEolMode(eolMode)

            snapshotWidget = subStack.widget(1)
            snapshotWidget.setText(text)
            snapshotWidget.convertEols(eolMode)
            snapshotWidget.setEolMode(eolMode)
        except Exception as err:
            QtGui.QApplication.restoreOverrideCursor()
            if showError:
                message = QtGui.QMessageBox.warning(self, "Open", str(err))
            else:
                pass
            return False

        QtGui.QApplication.restoreOverrideCursor()

        editor.setModified(False)
        editor.setFocus()
        self.updateRecentFilesList.emit(filePath)
        self.updateOpenedTabsMenu()

        return True

    def get_current_word(self):
        current_word = self.focusedEditor().get_current_word()
        return current_word

    def getOffset(self):
        offset = self.focusedEditor().getOffset()
        return offset

    def changeTab(self):
        if (self.count() - 1) != self.currentIndex():
            self.setCurrentIndex(self.currentIndex() + 1)
        else:
            self.setCurrentIndex(0)

    def reverseTab(self):
        if self.currentIndex() != 0:
            self.setCurrentIndex(self.currentIndex() - 1)
        else:
            self.setCurrentIndex(self.count() - 1)

    def changeSplitFocus(self):
        splitter = self.currentWidget().widget(0)
        firstEditor = splitter.widget(0)
        if firstEditor.hasFocus():
            splitter.widget(1).setFocus()
        else:
            firstEditor.setFocus()

    def setShortcuts(self):
        self.tabBar.setShortcuts()
        shortcuts = self.useData.CUSTOM_SHORTCUTS

        self.shortSplitVertical = QtGui.QShortcut(
            shortcuts["Ide"]["Split-Vertical"], self)
        self.shortSplitVertical.activatedAmbiguously.connect(
            self.splitVertical)
        self.vSplitEditorAct.setShortcut(shortcuts["Ide"]["Split-Vertical"])

        self.shortSplitHorizontal = QtGui.QShortcut(
            shortcuts["Ide"]["Split-Horizontal"], self)
        self.shortSplitHorizontal.activatedAmbiguously.connect(
            self.splitHorizontal)
        self.hSplitEditorAct.setShortcut(
            shortcuts["Ide"]["Split-Horizontal"])

        self.shortRemoveSplit = QtGui.QShortcut(
            shortcuts["Ide"]["Remove-Split"], self)
        self.shortRemoveSplit.activatedAmbiguously.connect(self.removeSplit)
        self.noSplitEditorAct.setShortcut(shortcuts["Ide"]["Remove-Split"])

        self.shortChangeTab = QtGui.QShortcut(
            shortcuts["Ide"]["Change-Tab"], self)
        self.shortChangeTab.activated.connect(self.changeTab)

        self.shortReverseTab = QtGui.QShortcut(
            shortcuts["Ide"]["Change-Tab-Reverse"], self)
        self.shortReverseTab.activated.connect(self.reverseTab)

        self.shortChangeSplitFocus = QtGui.QShortcut(
            shortcuts["Ide"]["Change-Split-Focus"], self)
        self.shortChangeSplitFocus.activated.connect(self.changeSplitFocus)

        self.shortNewFile = QtGui.QShortcut(
            shortcuts["Ide"]["New-File"], self)
        self.shortNewFile.activatedAmbiguously.connect(self._newPythonFile)
        self.newPythonFileAct.setShortcut(shortcuts["Ide"]["New-File"])

        self.shortOpenFile = QtGui.QShortcut(
            shortcuts["Ide"]["Open-File"], self)
        self.shortOpenFile.activatedAmbiguously.connect(self.openFile)
        self.openFileAct.setShortcut(shortcuts["Ide"]["New-File"])

        self.shortSaveFile = QtGui.QShortcut(
            shortcuts["Ide"]["Save-File"], self)
        self.shortSaveFile.activatedAmbiguously.connect(self._save)
        self.saveAct.setShortcut(shortcuts["Ide"]["Save-File"])

        self.shortSaveAll = QtGui.QShortcut(
            shortcuts["Ide"]["Save-All"], self)
        self.shortSaveAll.activatedAmbiguously.connect(self.saveAll)
        self.saveAllAct.setShortcut(shortcuts["Ide"]["Save-All"])

        self.shortPrint = QtGui.QShortcut(shortcuts["Ide"]["Print"], self)
        self.shortPrint.activatedAmbiguously.connect(self.printCode)
        self.printAct.setShortcut(shortcuts["Ide"]["Print"])
