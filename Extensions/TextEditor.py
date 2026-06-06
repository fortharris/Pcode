import os

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import (
    QAction, QColor, QFontMetrics, QIcon, QKeySequence, QPixmap, QShortcut,
)
from PyQt6.QtWidgets import QHBoxLayout, QMenu, QVBoxLayout

from Extensions.font_metrics import font_metrics_width

from Extensions.BaseScintilla import BaseScintilla
from Extensions.ZoomWidget import ZoomWidget
from Extensions import Global
from Extensions.Notification import Notification
from Extensions import StyleSheet


class TextEditor(BaseScintilla):

    def __init__(self, useData, DATA, colorScheme, editorTabWidget,
                 encoding=None, parent=None):
        BaseScintilla.__init__(self, parent)

        self.useData = useData
        self.encoding = encoding
        self.DATA = DATA
        self.colorScheme = colorScheme
        self.editorTabWidget = editorTabWidget

        self.setObjectName("editor")
        self.enableMarkOccurrence(useData)

        self.setFont(Global.getDefaultFont())
        self.setWrapMode(QsciScintilla.WrapWord)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        #

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(0, 0, 20, 0)
        mainLayout.addLayout(hbox)

        self.zoomWidget = ZoomWidget(self.useData, self)
        hbox.addWidget(self.zoomWidget)

        #

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(5, 0, 20, 20)
        mainLayout.addLayout(hbox)

        self.notification = Notification()
        hbox.addWidget(self.notification)
        self.notification.hide()

        #

        self.createContextMenu()

        # setup
        # define the font to use
        self.font = Global.getDefaultFont()
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)
        # the font metrics here will help
        # building the margin width later
        self.fontMetrics = QFontMetrics(self.font)

        # Line numbers
        # conventionnaly, margin 0 is for line numbers
        self.setMarginWidth(0, font_metrics_width(self.fontMetrics, "0000") + 5)

        self.setUtf8(True)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)

        # Braces matching
        if self.useData.setting_bool("MatchBraces"):
            self.setBraceMatching(QsciScintilla.StrictBraceMatch)

        if self.DATA["fileType"] in self.useData.supportedFileTypes:
            if self.useData.setting_bool("ShowCaretLine"):
                self.setCaretLineVisible(True)

        self.setAutoCompletionReplaceWord(True)
        # minimum number of letters to be typed before list is displayed
        self.setAutoCompletionThreshold(2)

        self.setEdgeMode(QsciScintilla.EdgeNone)
        self.showWhiteSpaces()

        # Margins colors
        # line numbers margin
        self.setMarginsBackgroundColor(QColor("#FFFFFF"))
        self.setMarginsForegroundColor(QColor("#666666"))

        # define markers

        self.markerDefine(QPixmap(
            os.path.join("Resources", "images", "ui-button-navigation")), 8)
        self.setMarkerBackgroundColor(QColor("#ee1111"), 8)

        self.markerDefine(
            QPixmap(os.path.join("Resources", "images", "err_mark")), 9)
        self.setMarkerBackgroundColor(QColor("#ee1111"), 9)

        self.markerDefine(
            QPixmap(os.path.join("Resources", "images", "brk_point")), 10)
        self.setMarkerBackgroundColor(QColor("#ee1111"), 10)

        self.showLineNumbers()
        self.setAutoCompletionSource(QsciScintilla.AcsDocument)

        self.setEolMode(QsciScintilla.EolUnix)

        self.searchIndicator = self.indicatorDefine(
            QsciScintilla.IndicatorStyle.RoundBoxIndicator, 10)
        self.setIndicatorForegroundColor(
            QColor("#FFDB4A"), self.searchIndicator)
        self.setIndicatorDrawUnder(True, self.searchIndicator)

        self.setAutoCompletion()

        self.copyAvailableTimer = QTimer()
        self.copyAvailableTimer.setSingleShot(True)
        self.copyAvailableTimer.setInterval(0)
        self.copyAvailableTimer.timeout.connect(self.copyActModifier)

        self.copyAvailable.connect(self.copyAvailableTimer.start)

        self.textChangedTimer = QTimer()
        self.textChangedTimer.setSingleShot(True)
        self.textChangedTimer.setInterval(0)
        self.textChangedTimer.timeout.connect(self.undoActModifier)
        self.textChangedTimer.timeout.connect(self.redoActModifier)

        self.textChanged.connect(self.textChangedTimer.start)
        self.linesChanged.connect(self.updateLineCount)
        self.marginClicked.connect(self.toggleBookmark)

        self.lexer = self.colorScheme.styleEditor(self)
        self.setStyleSheet(StyleSheet.editorStyle)

        self.setKeymap()

    def updateLexer(self, lexer):
        self.lexer = lexer
        self.setLexer(lexer)

    def createContextMenu(self):
        self.cutAct = QAction(
            "Cut", self, shortcut=QKeySequence.StandardKey.Cut,
            statusTip="Cut selected text", triggered=self.cut)

        self.copyAct = QAction(
            "Copy", self, shortcut=QKeySequence.StandardKey.Copy,
            statusTip="Copy selected text", triggered=self.copy)

        self.pasteAct = QAction(
            "Paste", self, shortcut=QKeySequence.StandardKey.Paste,
            statusTip="Paste text from clipboard",
            triggered=self.paste)

        self.deleteAct = QAction(
            "Delete", self, shortcut=QKeySequence.StandardKey.Delete,
            statusTip="Delete Selection",
            triggered=self.removeSelectedText)

        self.selectAllAct = QAction("Select All", self,
                                          shortcut=QKeySequence.StandardKey.SelectAll,
                                          statusTip="Select All",
                                          triggered=self.selectAllText)

        self.selectToMatchingBraceAct = \
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "text_select")),
                "Select to Matching Brace", self,
                statusTip="Select to Matching Brace",
                          triggered=self.selectToMatchingBrace)

        self.zoomAct = QAction(
            QIcon(os.path.join("Resources", "images", "zoom")),
            "Zoom", self,
            statusTip="Zoom", triggered=self.showZoomWidget)

        self.contextMenu = QMenu()
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

    def setAutoCompletion(self):
        if self.useData.setting_bool("EnableAutoCompletion"):
            self.setAutoCompletionSource(QsciScintilla.AcsDocument)
        else:
            self.setAutoCompletionSource(QsciScintilla.AcsNone)

    def contextMenuEvent(self, event):
        state = self.hasSelectedText()

        self.copyAct.setEnabled(state)
        self.cutAct.setEnabled(state)
        self.deleteAct.setEnabled(state)

        self.contextMenu.exec(event.globalPos())

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
        if highlight:
            self.setSelection(
                lineNum, 0, lineNum, self.lineLength(lineNum) - 1)
        self.ensureLineVisible(lineNum)

    def showWhiteSpaces(self):
        if self.useData.setting_bool("ShowWhiteSpaces"):
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

    def setKeymap(self):
        self.updateKeymap(self.useData)

        shortcuts = self.useData.CUSTOM_SHORTCUTS

        self.cutAct.setShortcut(shortcuts["Editor"]["Cut-Selection"][0])
        self.copyAct.setShortcut(shortcuts["Editor"]["Copy-Selection"][0])
        self.pasteAct.setShortcut(shortcuts["Editor"]["Paste"][0])

        self.shortNextBookmark = QShortcut(
            shortcuts["Ide"]["Next-Bookmark"], self)
        self.shortNextBookmark.activated.connect(self.findNextBookmark)

        self.shortPreviousBookmark = QShortcut(
            shortcuts["Ide"]["Previous-Bookmark"], self)
        self.shortPreviousBookmark.activated.connect(self.findPreviousBookmark)

        self.shortZoomIn = QShortcut(
            shortcuts["Editor"]["Zoom-In"][0], self)
        self.shortZoomIn.activated.connect(self.zoomWidget.zoomIn)

        self.shortZoomOut = QShortcut(
            shortcuts["Editor"]["Zoom-Out"][0], self)
        self.shortZoomOut.activated.connect(self.zoomWidget.zoomOut)
