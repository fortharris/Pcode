from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla

from Extensions.BaseScintilla import BaseScintilla
from Extensions.ZoomWidget import ZoomWidget
from Extensions import Global
from Extensions.Notification import Notification
from Extensions import StyleSheet


class TextEditor(BaseScintilla):

    def __init__(self, useData,  DATA, colorScheme, editorTabWidget,
                 encoding=None, parent=None):
        super(TextEditor, self).__init__(parent)

        self.useData = useData
        self.encoding = encoding
        self.DATA = DATA
        self.colorScheme = colorScheme
        self.editorTabWidget = editorTabWidget

        self.setFont(Global.getDefaultFont())
        self.setWrapMode(QsciScintilla.WrapWord)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        #

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(0, 0, 20, 0)
        mainLayout.addLayout(hbox)

        self.zoomWidget = ZoomWidget(self.useData, self)
        hbox.addWidget(self.zoomWidget)
        hbox.addStretch(1)

        #

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(5, 0, 20, 20)
        mainLayout.addLayout(hbox)

        self.notify = Notification()
        hbox.addWidget(self.notify)
        self.notify.hide()

        #

        self.createContextMenu()

        self.setStyleSheet(StyleSheet.editorStyle)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # setup
        # define the font to use
        self.font = Global.getDefaultFont()
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)
        # the font metrics here will help
        # building the margin width later
        self.fontMetrics = QtGui.QFontMetrics(self.font)

        # Line numbers
        # conventionnaly, margin 0 is for line numbers
        self.setMarginWidth(0, self.fontMetrics.width("0000") + 5)

        if self.encoding is None:
            self.setUtf8(True)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)

        # Braces matching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        self.setAutoCompletionReplaceWord(True)
        # minimum number of letters to be typed before list is displayed
        self.setAutoCompletionThreshold(2)

        self.setEdgeMode(QsciScintilla.EdgeNone)
        self.setCaretLineVisible(False)
        self.showWhiteSpaces()

        # Margins colors
        # line numbers margin
        self.setMarginsBackgroundColor(QtGui.QColor("#FFFFFF"))
        self.setMarginsForegroundColor(QtGui.QColor("#666666"))

        # define markers
        # the background markers will not show until the editor has focus
        self.currentline = self.markerDefine(QsciScintilla.Background)
        self.breakpointLine = self.markerDefine(QsciScintilla.Background)

        self.setMarkerForegroundColor(QtGui.QColor("#000000"),
                                      self.currentline)
        self.setMarkerBackgroundColor(QtGui.QColor("#0099CC"),
                                      self.currentline)
        self.setMarkerForegroundColor(QtGui.QColor("#000000"),
                                      self.breakpointLine)
        self.setMarkerBackgroundColor(QtGui.QColor("#ffe1e1"),
                                      self.breakpointLine)

        self.markerDefine(QtGui.QPixmap(
            "Resources\\images\\ui-button-navigation"), 8)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"), 8)

        self.markerDefine(QtGui.QPixmap("Resources\\images\\err_mark"), 9)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"), 9)

        self.markerDefine(QtGui.QPixmap("Resources\\images\\brk_point"), 10)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"), 10)

        self.showLineNumbers()
        self.setAutoCompletionSource(QsciScintilla.AcsDocument)

        self.setEolMode(QsciScintilla.EolUnix)

        self.matchIndicator = self.indicatorDefine(QsciScintilla.INDIC_BOX, 9)
        self.setIndicatorForegroundColor(
            QtGui.QColor("#FFCC00"), self.matchIndicator)
        self.setIndicatorDrawUnder(True, self.matchIndicator)

        self.searchIndicator = self.indicatorDefine(
            QsciScintilla.INDIC_ROUNDBOX, 10)
        self.setIndicatorForegroundColor(
            QtGui.QColor("#FFDB4A"), self.searchIndicator)
        self.setIndicatorDrawUnder(True, self.searchIndicator)
        
        self.setAutoCompletionSource(QsciScintilla.AcsDocument)
        
        self.copyAvailableTimer = QtCore.QTimer()
        self.copyAvailableTimer.setSingleShot(True)
        self.copyAvailableTimer.setInterval(0)
        self.copyAvailableTimer.timeout.connect(self.copyActModifier)
        
        self.copyAvailable.connect(self.copyAvailableTimer.start)
        
        self.textChangedTimer = QtCore.QTimer()
        self.textChangedTimer.setSingleShot(True)
        self.textChangedTimer.setInterval(0)
        self.textChangedTimer.timeout.connect(self.undoActModifier)
        self.textChangedTimer.timeout.connect(self.redoActModifier)

        self.textChanged.connect(self.textChangedTimer.start)
        self.linesChanged.connect(self.updateLineCount)
        self.marginClicked.connect(self.toggleBookmark)

        self.lexer = self.colorScheme.styleEditor(self)

        self.install_shortcuts()

    def updateLexer(self, lexer):
        self.lexer = lexer
        self.setLexer(lexer)

    def createContextMenu(self):
        self.cutAct = QtGui.QAction(
            "Cut", self, shortcut=QtGui.QKeySequence.Cut,
            statusTip="Cut selected text", triggered=self.cut)

        self.copyAct = QtGui.QAction(
            "Copy", self, shortcut=QtGui.QKeySequence.Copy,
            statusTip="Copy selected text", triggered=self.copy)

        self.pasteAct = QtGui.QAction(
            "Paste", self, shortcut=QtGui.QKeySequence.Paste,
            statusTip="Paste text from clipboard",
            triggered=self.paste)

        self.deleteAct = QtGui.QAction(
            "Delete", self, shortcut=QtGui.QKeySequence.Delete,
            statusTip="Delete Selection",
            triggered=self.removeSelectedText)

        self.selectAllAct = QtGui.QAction("Select All", self,
                                          shortcut=QtGui.QKeySequence.SelectAll,
                                          statusTip="Select All",
                                          triggered=self.selectAllText)

        self.selectToMatchingBraceAct = \
            QtGui.QAction(QtGui.QIcon("Resources\\images\\text_select"),
                          "Select to Matching Brace", self,
                          statusTip="Select to Matching Brace",
                          triggered=self.selectToMatchingBrace)

        self.zoomAct = QtGui.QAction(QtGui.QIcon("Resources\\images\\zoom"),
                                     "Zoom", self,
                                     statusTip="Zoom", triggered=self.showZoomWidget)

        self.contextMenu = QtGui.QMenu()
        self.contextMenu.addAction(self.cutAct)
        self.contextMenu.addAction(self.copyAct)
        self.contextMenu.addAction(self.pasteAct)
        self.contextMenu.addAction(self.deleteAct)
        self.contextMenu.addAction(self.selectAllAct)
        self.contextMenu.addAction(self.selectToMatchingBraceAct)
        self.contextMenu.addSeparator()
        self.viewMenu = self.contextMenu.addMenu("View")
        self.viewMenu.addAction(self.editorTabWidget.vSplitEditorAct)
        self.viewMenu.addAction(self.editorTabWidget.hSplitEditorAct)
        self.viewMenu.addAction(self.editorTabWidget.noSplitEditorAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.zoomAct)

    def contextMenuEvent(self, event):
        state = self.hasSelectedText()

        self.copyAct.setEnabled(state)
        self.cutAct.setEnabled(state)
        self.deleteAct.setEnabled(state)

        self.contextMenu.exec_(event.globalPos())

    def undoActModifier(self):
        state = self.isUndoAvailable()
        self.editorTabWidget.undoAct.setEnabled(state)

    def redoActModifier(self):
        state = self.isRedoAvailable()
        self.editorTabWidget.redoAct.setEnabled(state)

    def copyActModifier(self):
        state = self.hasSelectedText()
        self.editorTabWidget.copyAct.setEnabled(state)
        self.editorTabWidget.cutAct.setEnabled(state)

    def updateLineCount(self):
        lines = self.lines()
        self.editorTabWidget.updateLinesCount.emit(lines)

    def selectAllText(self):
        self.selectAll()

    def showZoomWidget(self):
        self.zoomWidget.show()

    def showLine(self, lineNum, highlight=True):
        if highlight == True:
            self.setSelection(
                lineNum, 0, lineNum, self.lineLength(lineNum) - 1)
        self.ensureLineVisible(lineNum)

    def showWhiteSpaces(self):
        if self.useData.SETTINGS["ShowWhiteSpaces"] == 'True':
            self.setWhitespaceVisibility(QsciScintilla.WsVisible)
        else:
            self.setWhitespaceVisibility(QsciScintilla.WsInvisible)

    def findMarkerDown(self):
        lineNum = self.markerFindNext(self.getCursorPosition()[0] + 1, 256)
        if lineNum == -1:
            lineNum = self.markerFindNext(0, 256)
        self.setSelection(lineNum, 0, lineNum, self.lineLength(lineNum) - 1)
        self.ensureLineVisible(lineNum)

    def findMarkerUp(self):
        lineNum = self.markerFindPrevious(self.getCursorPosition()[0] - 1, 256)
        if lineNum == -1:
            lineNum = self.markerFindPrevious(self.lines(), 256)
        self.setSelection(lineNum, 0, lineNum, self.lineLength(lineNum) - 1)
        self.ensureLineVisible(lineNum)

    def removeMarkers(self):
        self.markerDeleteAll(8)

    def increaseIndent(self):
        if self.hasSelectedText() == False:
            pos = self.getCursorPosition()
            line = pos[0]
            self.indent(line)
        else:
            self.SendScintilla(QsciScintilla.SCI_TAB)

    def decreaseIndent(self):
        if self.hasSelectedText() == False:
            pos = self.getCursorPosition()
            line = pos[0]
            self.unindent(line)
        else:
            self.SendScintilla(QsciScintilla.SCI_BACKTAB)

    def findNextBookmark(self):
        cursorLine = self.getCursorPosition()[0]
        lineNum = self.markerFindNext(cursorLine + 1, 256)
        if lineNum == -1:
            lineNum = self.markerFindNext(0, 256)
            if lineNum == -1:
                return
        self.showLine(lineNum)

    def findPreviousBookmark(self):
        cursorLine = self.getCursorPosition()[0]
        lineNum = self.markerFindPrevious(cursorLine - 1, 256)
        if lineNum == -1:
            lineNum = self.markerFindPrevious(self.lines(), 256)
            if lineNum == -1:
                return
        self.showLine(lineNum)

    def toggleBookmark(self, nmargin, nline, modifiers=None):
        if self.markersAtLine(nline) == 0:
            handle = self.markerAdd(nline, 8)
            self.DATA["bookmarkList"].append(handle)
        else:
            for handle in self.DATA["bookmarkList"]:
                if self.markerLine(handle) == nline:
                    self.DATA["bookmarkList"].remove(handle)
                    self.markerDeleteHandle(handle)

        markersExist = self.bookmarksExist()
        self.editorTabWidget.enableBookmarkButtons(markersExist)

    def bookmarksExist(self):
        markersExist = (len(self.DATA["bookmarkList"]) > 0)
        return markersExist

    def getBookmarks(self):
        bookmarkLines = []
        for handle in self.DATA["bookmarkList"]:
            line = self.markerLine(handle)
            bookmarkLines.append(line)

        return bookmarkLines

    def removeBookmarks(self):
        if len(self.DATA["bookmarkList"]) > 0:
            self.DATA["bookmarkList"] = []
            self.markerDeleteAll(8)

    def notify(self, mess):
        self.infoBar.showMessage(mess)

    def install_shortcuts(self):
        shortcuts = self.useData.CUSTOM_DEFAULT_SHORTCUTS
