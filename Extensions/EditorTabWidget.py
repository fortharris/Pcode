import os
import sys
import time
import tempfile
import traceback
import logging

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import QFileSystemWatcher, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QShortcut
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QHBoxLayout, QMenu, QMessageBox,
    QStackedWidget, QTabWidget, QToolButton, QVBoxLayout,
)

from Extensions.file_dialog_utils import file_dialog_path
from Extensions.settings_utils import to_bool
from Extensions.Diff import DiffWindow
from Extensions.CodeEditor import CodeEditor
from Extensions.TextEditor import TextEditor
from Extensions.ViewSwitcher import ViewSwitcher
from Extensions.TextSnapshot import TextSnapshot
from Extensions.CodeSnapshot import CodeSnapshot
from Extensions.GotoLineWidget import GotoLineWidget
from Extensions.EditorSplitter import EditorSplitter
from Extensions.editor_tab_bar import EditorTabBar
from Extensions import Global
from Extensions.Refactor.Refactor import Refactor
from Extensions.BottomWidgets.RunWidget import SetRunParameters
from Extensions.Projects.ProjectManager.ConfigureProject import ConfigureProject
from Extensions import StyleSheet


class EditorTabWidget(QTabWidget):

    currentEditorTextChanged = pyqtSignal()
    bookmarksChanged = pyqtSignal()
    updateLinesCount = pyqtSignal(int)
    updateRecentFilesList = pyqtSignal(str)
    updateWindowTitle = pyqtSignal(str)
    updateEncodingLabel = pyqtSignal(str)
    cursorPositionChanged = pyqtSignal()

    def __init__(
        self, useData, projectPathDict, projectSettings, messagesWidget, colorScheme, busyWidget, bookmarkToolbar,
            app, manageFavourites, externalLauncher, editorWindow, parent=None):
        QTabWidget.__init__(self, parent)

        self.setElideMode(Qt.TextElideMode.ElideRight)

        self.useData = useData
        self.projectPathDict = projectPathDict
        # Unique per-instance scratch file for the style-guide (pep8/autopep8)
        # round-trip, so concurrent editor windows don't clobber each other.
        fd, self.pep8TempPath = tempfile.mkstemp(prefix="pcode-pep8-", suffix=".py")
        os.close(fd)
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

        self.backupTimer = QTimer()
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

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)
        self._customUiMargins = StyleSheet.uses_themed_chrome(self.useData.SETTINGS)
        self.adjustToStyleSheet(self._customUiMargins)

        self.topVBox = QVBoxLayout()
        self.topVBox.setContentsMargins(0, 0, 0, 0)
        self.topVBox.setSpacing(0)
        self.mainLayout.addLayout(self.topVBox)

        self.mainLayout.addStretch(1)

        self.addToolWidget(self.configDialog)
        self.addToolWidget(self.externalLauncher)
        self.addToolWidget(self.manageFavourites)
        self.addToolWidget(self.setRunParameters)
        self.addToolWidget(self.viewSwitcher)
        self.addToolWidget(self.gotoLineWidget)

        self.filesWatch = QFileSystemWatcher()
        self.filesWatch.fileChanged.connect(self.fileChanged)

        self.createActions()

        self.tabBar = EditorTabBar(self.app,
                                   self.refactor.renameModuleAct,
                                   self.refactor.moduleToPackageAct, self)
        self.tabBar.setMovable(True)
        self.tabBar.setTabsClosable(True)

        self.openedTabsMenu = QMenu()

        self.tabSelectButton = QToolButton()
        self.tabSelectButton.setAutoRaise(True)
        self.tabSelectButton.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)
        self.tabSelectButton.setIcon(
            QIcon(os.path.join("Resources", "images", "tile")))
        self.tabSelectButton.setMenu(self.openedTabsMenu)

        self.setTabBar(self.tabBar)
        # Re-measure top margin now that the real tab bar exists.
        self.adjustToStyleSheet(self._customUiMargins)
        self.setAcceptDrops(True)
        self.setUsesScrollButtons(True)
        self.setCornerWidget(self.tabSelectButton)
        self.currentChanged.connect(self.editorTabChanged)
        self.tabCloseRequested.connect(self.closeEditorTab)

        self.setKeymap()
        self.backupTimer.start()

        self.newFileMenu = QMenu("New File")
        self.newFileMenu.addAction(self.newPythonFileAct)
        self.newFileMenu.addAction(self.newXmlFileAct)
        self.newFileMenu.addAction(self.newHtmlFileAct)
        self.newFileMenu.addAction(self.newCssFileAct)

    def showEvent(self, event):
        QTabWidget.showEvent(self, event)
        # Tab bar height can settle after first show; keep sheets flush.
        self.adjustToStyleSheet(getattr(self, "_customUiMargins", True))

    def resizeView(self, hview, vview):
        self.editorWindow.resizeView(hview, vview)

    def _tab_bar_height(self):
        # Instance attribute ``self.tabBar`` shadows QTabWidget.tabBar().
        bar = self.__dict__.get("tabBar")
        if bar is None:
            bar = QTabWidget.tabBar(self)
        if bar is None:
            return 0
        if bar.height() > 0:
            return bar.height()
        return max(0, bar.sizeHint().height())

    def adjustToStyleSheet(self, adjust):
        self._customUiMargins = bool(adjust)
        top = self._tab_bar_height()
        if adjust:
            self.mainLayout.setContentsMargins(0, top, 14, 12)
        else:
            self.mainLayout.setContentsMargins(0, top, 25, 12)

    def refreshChromeStyles(self, custom=True):
        """Apply or clear tool-overlay and editor chrome stylesheets."""
        self.manageFavourites.setStyleSheet(
            StyleSheet.chrome_style("toolWidgetStyle", custom))
        self.externalLauncher.setStyleSheet(
            StyleSheet.chrome_style("toolWidgetStyle", custom))
        self.setRunParameters.setStyleSheet(
            StyleSheet.chrome_style("toolWidgetStyle", custom))
        self.viewSwitcher.setStyleSheet(
            StyleSheet.chrome_style("viewSwitcherStyle", custom))
        if hasattr(self, "configDialog"):
            self.configDialog.setStyleSheet(
                StyleSheet.chrome_style("toolWidgetStyle", custom))
        for i in range(self.count()):
            try:
                editor = self.getEditor(i)
                if editor is not None:
                    editor.setStyleSheet(
                        StyleSheet.chrome_style("editorStyle", custom))
                clone = self.getCloneEditor(i)
                if clone is not None:
                    clone.setStyleSheet(
                        StyleSheet.chrome_style("editorStyle", custom))
            except Exception:
                pass

    def addToolWidget(self, widget):
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addStretch(1)
        hbox.addWidget(widget)
        self.topVBox.addLayout(hbox)

        self.toolWidgetList.append(widget)
        widget.hide()

    def createActions(self):
        self.undoAct = QAction(
            QIcon(os.path.join("Resources", "images", "undo")),
            "Undo", self,
            statusTip="Undo last edit action",
            triggered=self.undoAction)

        self.redoAct = QAction(
            QIcon(os.path.join("Resources", "images", "redo")),
            "Redo", self,
            statusTip="Redo last edit action",
            triggered=self.redoAction)

        self.cutAct = QAction(
            QIcon(os.path.join("Resources", "images", "cut")),
            "Cut", self,
            statusTip="Cut selected text", triggered=self.cutItem)

        self.copyAct = QAction(
            QIcon(os.path.join("Resources", "images", "copy")),
            "Copy", self,
            statusTip="Copy selected text", triggered=self.copyItem)

        self.pasteAct = QAction(
            QIcon(os.path.join("Resources", "images", "paste")),
            "Paste", self,
            statusTip="Paste text from clipboard",
            triggered=self.pasteFromClipboard)

        #----------------------------------------------------------------------

        self.indentAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "increase_indent")),
                "Indent", self,
                statusTip="Indent Region",
                triggered=self.increaseIndent)

        self.dedentAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "decrease_indent")),
                "Unindent", self,
                statusTip="Unindent Region",
                triggered=self.decreaseIndent)

        self.writeLockAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "block")),
                "Write Lock", self,
                statusTip="Write Lock",
                          triggered=self.writeLock)

        self.findNextBookmarkAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "Arrow2-down")),
                "Next Bookmark", self, statusTip="Next Bookmark",
                triggered=self.findNextBookmark)

        self.findPrevBookmarkAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "Arrow2-up")),
                "Previous Bookmark", self, statusTip="Previous Bookmark",
                triggered=self.findPreviousBookmark)

        self.removeBookmarksAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "block__")),
                "Remove Bookmarks", self, statusTip="Remove Bookmarks",
                triggered=self.removeBookmarks)
        #---------------------------------------------------------------------
        self.newPythonFileAct = QAction(
            QIcon(os.path.join("Resources", "images", "new")),
            "New Python File", self,
            statusTip="Create a new python file",
            triggered=self._newPythonFile)

        self.newXmlFileAct = QAction(
            QIcon(os.path.join("Resources", "images", "new")),
            "Xml", self,
            statusTip="Create a new Xml file",
            triggered=self._newXmlFile)

        self.newHtmlFileAct = QAction(
            QIcon(os.path.join("Resources", "images", "new")),
            "Html", self,
            statusTip="Create a new Html file",
            triggered=self._newHtmlFile)

        self.newCssFileAct = QAction(
            QIcon(os.path.join("Resources", "images", "new")),
            "Css", self,
            statusTip="Create a new Css file",
            triggered=self._newCssFile)

        self.openFileAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "open_file")),
                "Open File...", self,
                statusTip="Open python file",
                          triggered=self.openFile)

        self.saveAct = QAction(
            QIcon(os.path.join("Resources", "images", "save_")),
            "Save", self,
            statusTip="Save", triggered=self._save)

        self.saveAllAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "disks-black")),
                "Save All", self,
                statusTip="Save All",
                          triggered=self.saveAll)

        self.saveAsAct = QAction("Save As...", self, statusTip="Save",
                                       triggered=self.saveAs)

        self.saveCopyAsAct = QAction("Save Copy As...",
                                           self, statusTip="Save Copy As",
                                           triggered=self.saveCopyAs)

        self.printAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "_0013_Printer")),
                "Print", self,
                statusTip="Print", triggered=self.printCode)
        #----------------------------------------------------------------------

        self.vSplitEditorAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "border-horizontal")),
                "Split Vertical", self,
                statusTip="Split Vertical", triggered=self.splitVertical)

        self.hSplitEditorAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "border-vertical")),
                "Split Horizontal", self,
                statusTip="Split Horizontal", triggered=self.splitHorizontal)

        self.noSplitEditorAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "border")),
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
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.widget(1).show()

    def splitHorizontal(self):
        splitter = self.currentWidget().widget(0)
        splitter.setOrientation(Qt.Orientation.Horizontal)
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
            except Exception:
                pass

    def createBackup(self):
        for i in range(self.count()):
            key = self.getEditorData("backupKey", i)
            editor = self.getEditor(i)

            savePath = os.path.join(self.projectPathDict["backupdir"], key)

            with open(savePath, 'w') as file:
                file.write(editor.text())
        self.saveSession(True)

    def saveSession(self, backup=False):
        from Extensions.SessionData import save as save_session
        from Extensions.session_restore import capture_entries
        save_session(self.projectPathDict, capture_entries(self, backup=backup),
                     backup=backup)

    def restoreSession(self):
        from Extensions.SessionData import load as load_session
        backup = not to_bool(self.projectSettings.get("LastCloseSuccessful"), True)

        if backup:
            pass
        else:
            self.clearBackups()

        entries = load_session(self.projectPathDict, backup=backup)
        if not entries and backup:
            entries = load_session(self.projectPathDict, backup=False)

        from Extensions.session_restore import restore_entries
        restoredBackups = restore_entries(self, entries, backup=backup)

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
        self.openedTabsActionGroup = QActionGroup(self)
        self.openedTabsActionGroup.setExclusive(True)
        self.openedTabsActionGroup.triggered.connect(self.makeCurrentTab)
        self.openedTabsMenu.clear()
        for i in range(self.count()):
            name = self.tabText(i)
            action = QAction(name, self)
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
        widget.updateGeometry()
        self.topVBox.activate()

    def showProjectConfiguration(self):
        self.showMe(self.configDialog)

    def showGotoLineWidget(self):
        self.showMe(self.gotoLineWidget)
        self.gotoLineWidget.lineNumberLine.setFocus()

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
                            QIcon(os.path.join("Resources", "images", "locked_script")))
        else:
            self.focusedEditor().setReadOnly(False)
            if self.getEditorData("fileType") == "python":
                if self.focusedEditor().isModified():
                    self.setTabIcon(self.currentIndex(),
                                    QIcon(os.path.join("Resources", "images", "script_grey")))
                else:
                    self.setTabIcon(self.currentIndex(),
                                    QIcon(os.path.join("Resources", "images", "script")))
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
        reply = QMessageBox.warning(self, "Remove Bookmarks",
                                          "Do you really want to remove all bookmarks?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
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
        except Exception:
            pass

    def requestSaveMess(self, tabIndex):
        mess = "Save changes to '{0}'?".format(self.tabText(tabIndex))
        reply = QMessageBox.information(self, "Save", mess,
                                              QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard |
                                              QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Save:
            self.save()
        elif reply == QMessageBox.StandardButton.Discard:
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
                from Extensions.tab_io import write_editor_to_path
                editor = self.getEditor(index)
                encoding = self.getEditorData("codingFormat", index) or "utf-8"
                ok, used = write_editor_to_path(editor, savePath, encoding)
                if ok:
                    if used != encoding:
                        self.updateEditorData("codingFormat", used, index)
                        self.updateEncodingLabel.emit(
                            "Coding: {0}".format(used))
                    return True
                self.saveErrorMess("Failed to write file.")
                return False
            except Exception as err:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(repr(traceback.format_exception(exc_type, exc_value,
                             exc_traceback)))
                self.saveErrorMess(str(err))

                return False

    def saveToTemp(self, type, index=None):
        if index is None:
            index = self.currentIndex()
        try:
            if type == 'pep8':
                editor = self.getEditor(index)
                with open(self.pep8TempPath, "w") as file:
                    file.write(editor.text())
                return True
            return False
        except Exception:
            return False

    def saveAs(self, index=None, copyOnly=False):
        filter = self.getFilter()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save As",
            os.path.join(self.useData.getLastOpenedDir(), self.getTabName()),
            filter)
        if fileName:
            self.useData.saveLastOpenedDir(os.path.dirname(fileName))
            try:
                if index is None:
                    index = self.currentIndex()
                fileName = os.path.normpath(fileName)
                editor = self.getEditor(index)
                encoding = self.getEditorData("codingFormat", index) or "utf-8"
                from Extensions.tab_io import write_editor_to_path
                ok, used = write_editor_to_path(editor, fileName, encoding)
                if not ok:
                    self.saveErrorMess("Failed to write file.")
                    return False
                if used != encoding:
                    self.updateEditorData("codingFormat", used)
                    self.updateEncodingLabel.emit("Coding: {0}".format(used))
                self.updateTabName(index)
                if not copyOnly:
                    self.updateEditorData("filePath", fileName)
                self.filesWatch.addPath(fileName)
                return True
            except Exception as err:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(repr(traceback.format_exception(exc_type, exc_value,
                             exc_traceback)))
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
        self.projectPathDict["sourcedir"]
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

        QMessageBox.critical(self,
                                             "Save", "Error saving file!\n\n" + mess)

    def printCode(self):
        document = self.currentEditor.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        document.print_(printer)

    def openFile(self):
        fileName = file_dialog_path(QFileDialog.getOpenFileName(
            self,
            "Select File", self.useData.getLastOpenedDir(),
            "All Files (*);;Console (*.py);;No Console (*.pyw);;Xml (*.xml);;Html (*.html);;Css (*.css)",
        ))
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
        subStack = QStackedWidget()
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
            icon = QIcon(os.path.join("Resources", "images", "script"))
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

    def reloadModules(self, pathList=None):
        if pathList is None:
            pathList = []
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
        from Extensions.tab_io import open_file_in_tab
        return open_file_in_tab(self, filePath, showError, index)

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

    def setKeymap(self):
        self.tabBar.setKeymap()
        shortcuts = self.useData.CUSTOM_SHORTCUTS

        self.shortSplitVertical = QShortcut(
            shortcuts["Ide"]["Split-Vertical"], self)
        self.shortSplitVertical.activatedAmbiguously.connect(
            self.splitVertical)
        self.vSplitEditorAct.setShortcut(shortcuts["Ide"]["Split-Vertical"])

        self.shortSplitHorizontal = QShortcut(
            shortcuts["Ide"]["Split-Horizontal"], self)
        self.shortSplitHorizontal.activatedAmbiguously.connect(
            self.splitHorizontal)
        self.hSplitEditorAct.setShortcut(
            shortcuts["Ide"]["Split-Horizontal"])

        self.shortRemoveSplit = QShortcut(
            shortcuts["Ide"]["Remove-Split"], self)
        self.shortRemoveSplit.activatedAmbiguously.connect(self.removeSplit)
        self.noSplitEditorAct.setShortcut(shortcuts["Ide"]["Remove-Split"])

        self.shortChangeTab = QShortcut(
            shortcuts["Ide"]["Change-Tab"], self)
        self.shortChangeTab.activated.connect(self.changeTab)

        self.shortReverseTab = QShortcut(
            shortcuts["Ide"]["Change-Tab-Reverse"], self)
        self.shortReverseTab.activated.connect(self.reverseTab)

        self.shortChangeSplitFocus = QShortcut(
            shortcuts["Ide"]["Change-Split-Focus"], self)
        self.shortChangeSplitFocus.activated.connect(self.changeSplitFocus)

        self.shortNewFile = QShortcut(
            shortcuts["Ide"]["New-File"], self)
        self.shortNewFile.activatedAmbiguously.connect(self._newPythonFile)
        self.newPythonFileAct.setShortcut(shortcuts["Ide"]["New-File"])

        self.shortOpenFile = QShortcut(
            shortcuts["Ide"]["Open-File"], self)
        self.shortOpenFile.activatedAmbiguously.connect(self.openFile)
        self.openFileAct.setShortcut(shortcuts["Ide"]["New-File"])

        self.shortSaveFile = QShortcut(
            shortcuts["Ide"]["Save-File"], self)
        self.shortSaveFile.activatedAmbiguously.connect(self._save)
        self.saveAct.setShortcut(shortcuts["Ide"]["Save-File"])

        self.shortSaveAll = QShortcut(
            shortcuts["Ide"]["Save-All"], self)
        self.shortSaveAll.activatedAmbiguously.connect(self.saveAll)
        self.saveAllAct.setShortcut(shortcuts["Ide"]["Save-All"])

        self.shortPrint = QShortcut(shortcuts["Ide"]["Print"], self)
        self.shortPrint.activatedAmbiguously.connect(self.printCode)
        self.printAct.setShortcut(shortcuts["Ide"]["Print"])
