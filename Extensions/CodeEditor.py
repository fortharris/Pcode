import os
import io
import sys
from zipimport import zipimporter
import tokenize
from io import StringIO

from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla

from Extensions.BaseScintilla import BaseScintilla
from Extensions.ZoomWidget import ZoomWidget
from Extensions.Notification import Notification
from Extensions import StyleSheet

from rope.contrib import codeassist


class TokenizeThread(QtCore.QThread):

    def run(self):
        self.tokenList = []
        try:
            for type, rep, begin, end, expr in \
                    tokenize.generate_tokens(StringIO(self.source).readline):
                if type == tokenize.OP:
                    line = begin[0]
                    if line not in self.tokenList:
                        self.tokenList.append(line - 1)
        except:
            pass

    def tokenize(self, source):
        self.source = source

        self.start()


class DocThread(QtCore.QThread):

    docAvailable = QtCore.pyqtSignal(str, int)

    def run(self):
        try:
            doc = codeassist.get_doc(self.ropeProject,
                                     self.source, self.hoverOffset)
            self.docAvailable.emit(doc, self.hoverOffset)
        except:
            pass

    def doc(self, ropeProject, source, hoverOffset):
        self.ropeProject = ropeProject
        self.source = source
        self.hoverOffset = hoverOffset

        self.start()


class AutoCompletionThread(QtCore.QThread):

    completionsAvailable = QtCore.pyqtSignal(list)

    def run(self):
        completions = self.completions()
        if completions is None:
            return
        self.completionsAvailable.emit(completions)

    def rope_completions(self):
        """
        Returns list of completions based on the current project contents
        """
        try:
            proposals = codeassist.code_assist(self.ropeProject,
                                               self.source, self.offset)
            proposals = codeassist.sorted_proposals(proposals)
            if len(proposals) > 0:
                completions = []
                for i in proposals:
                    completions.append(str(i))

                return completions
            else:
                return []
        except:
            pass

    def completions(self):
        self.completionType = 3
        wordList = self.lineText.split(' ')
        
        if len(wordList) == 1 and wordList[0] == 'from':
            return []

        if len(wordList) == 3 and wordList[0] == 'from':
            # from x i, or from x ''
            if wordList[2].startswith('i') or wordList[2] == '':
                return ['import ']
            else:
                return []

        if len(wordList) < 3 and (wordList[0] == 'from'):
            # from x 
            if len(wordList) == 1:
                # from 
                return self.dirModules()

            return self.pkg_completions(wordList[1])

        if len(wordList) >= 3 and wordList[0] == 'from':
            absolutePath = os.path.join(
                self.sourcedir, wordList[1].replace('.', '//'))
            absolutePath = os.path.normpath(absolutePath)
            
            if wordList[2] == 'import':
                if os.path.isdir(absolutePath):
                    return self.dirModules(absolutePath)
                else:
                    # from x import y
                    completionList = self.module_classes(absolutePath)
                    if '(' in wordList[-1]:
                        wordList = wordList[:-2] + wordList[-1].split('(')
                    if ',' in wordList[-1]:
                        wordList = wordList[:-2] + wordList[-1].split(',')
                    return list(set(filter(lambda x: x.startswith(wordList[-1]), completionList)))
                
        if wordList[0] == 'import':
            if len(wordList) == 2 and wordList[1] == '':
                return self.dirModules()

            if ',' == wordList[-1]:
                return [' ']

            return self.pkg_completions(wordList[-1])

        if self.column != 0:
            if len(self.lineText.strip()) >= 2:  # Autocompletion threshold
                completions = self.rope_completions()
                self.completionType = 2
                return completions

    def dirModules(self, path=None):
        """
        Return list of modules in a directory
        """
        if path is None:
            # return list of modules in the main project directory
            
            modules = []
            modules += self.dirModules(self.sourcedir)

            modules += sys.builtin_module_names

            modules = list(set(modules))
            if '__init__' in modules:
                modules.remove('__init__')
            modules = list(set(modules))

            return sorted(modules)
        else:
            if os.path.isdir(path):
                folderList = os.listdir(path)
            elif path.endswith('.egg'):
                try:
                    folderList = [f for f in zipimporter(path)._files]
                except:
                    folderList = []
            else:
                folderList = []
            moduleList = []
            for p in folderList:
                if os.path.exists(os.path.join(path, p, '__init__.py')) \
                    or p[-3:] in ('.py', '.so') \
                        or p[-4:] in ('.pyc', '.pyo', '.pyd'):
                    if os.path.isdir(os.path.join(path, p)):
                        moduleList.append(p + os.path.sep)
                    else:
                        moduleList.append(os.path.splitext(p)[0])

            return moduleList

    def module_classes(self, absolutePath):
        """
        Return list of classes in a module. 
        """
        completionList = []
        try:
            absolutePath = absolutePath + '.py'

            file = open(absolutePath, "r")
            f = io.StringIO(file.read())
            file.close()

            g = tokenize.generate_tokens(f.readline)
            for tokentype, token, start, _end, _line in g:
                if token == 'class':
                    tokentype, class_name, start = next(g)[0:3]
                    completionList.append(class_name)
        except:
            return []
        return completionList

    def pkg_completions(self, dottedPath):
        # return completions from packages
        pathElements = dottedPath.split('.')
        if len(pathElements) < 2:
            return sorted(list(set(filter(lambda x: x.startswith(pathElements[0]),
                         self.dirModules()))))

        relativePath = '.'.join(pathElements[:-1])
        absolutePath = os.path.join(
            self.sourcedir, relativePath.replace('.', '//'))
        absolutePath = os.path.normpath(absolutePath)
        
        try:
            completionList = []
            
            contents = os.listdir(absolutePath)
            for item in contents:
                path = os.path.join(absolutePath, item)
                if os.path.isfile(path):
                    completionList.append(os.path.splitext(item)[0])
                else:
                    if '__init__.py' in os.listdir(path):
                        completionList.append(item + os.path.sep)
            completionList.remove('__init__')
        except:
            pass

        completionList = list(set(filter(lambda x: x.startswith(pathElements[-1]),
                             completionList)))

        return sorted(completionList)

    def complete(self, sourcedir, ropeProject,
                offset, source, lineText, col):
        self.sourcedir = sourcedir
        self.ropeProject = ropeProject
        self.offset = offset
        self.source = source
        self.lineText = lineText
        self.column = col

        self.start()


class CodeEditor(BaseScintilla):

    def __init__(self, useData, refactor, colorScheme,
                 DATA, editorTabWidget, parent=None):
        BaseScintilla.__init__(self, parent)

        self.useData = useData
        self.refactor = refactor
        self.DATA = DATA
        self.colorScheme = colorScheme
        self.editorTabWidget = editorTabWidget

        self.setObjectName("editor")
        self.enableMarkOccurrence(useData)

        self.setMouseTracking(True)
        self.middleMousePressed = False
        self.mousePosition = QtCore.QPointF()

        self.autoCompletionThread = AutoCompletionThread()
        self.autoCompletionThread.completionsAvailable.connect(self.showCompletions)

        self.docThread = DocThread()
        self.docThread.docAvailable.connect(
            self.showDoc)

        self.docThreadTimer = QtCore.QTimer()
        self.docThreadTimer.setSingleShot(True)
        self.docThreadTimer.timeout.connect(self.getDoc)

        self.tokenizeThread = TokenizeThread()
        self.tokenizeThread.finished.connect(
            self.displayTokenLines)

        self.tokenizeTimer = QtCore.QTimer()
        self.tokenizeTimer.setSingleShot(True)
        self.tokenizeTimer.timeout.connect(self.getOperationTokens)

        self.completionThreadTimer = QtCore.QTimer()
        self.completionThreadTimer.setSingleShot(True)
        self.completionThreadTimer.timeout.connect(self.startCompletion)

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

        #

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(5, 0, 10, 20)
        mainLayout.addLayout(hbox)

        self.notification = Notification()
        hbox.addWidget(self.notification)
        self.notification.hide()

        #

        self.createActions()

        self.setAutoCompletion()

        " Initialises indicators "
        self.syntaxErrorIndicator = self.indicatorDefine(
            QsciScintilla.INDIC_SQUIGGLE, 8)
        self.setIndicatorForegroundColor(QtGui.QColor(
            "#FF0000"), self.syntaxErrorIndicator)
        self.setIndicatorDrawUnder(True, self.syntaxErrorIndicator)

        self.searchIndicator = self.indicatorDefine(
            QsciScintilla.INDIC_ROUNDBOX, 10)
        self.setIndicatorForegroundColor(
            QtGui.QColor("#FFDB4A"), self.searchIndicator)
        self.setIndicatorDrawUnder(True, self.searchIndicator)

        self.userListActivated.connect(self.insertText)

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
        self.textChanged.connect(self.startTokenizeTimer)
        self.textChanged.connect(self.startCompletionTimer)

        self.linesChanged.connect(self.updateLineCount)
        self.marginClicked.connect(self.toggleBookmark)

        # define the font to use
        font = QtGui.QFont("Courier New")
        font.setFixedPitch(True)
        font.setPointSize(10)
        # the font metrics here will help
        # building the margin width later
        self.fontMetrics = QtGui.QFontMetrics(font)

        self.setUtf8(True)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)
        self.setIndentationWidth(4)
        self.setTabWidth(4)
#        self.setAnnotationDisplay(QsciScintilla.AnnotationStandard)

        # Line numbers
        # conventionnaly, margin 0 is for line numbers
        self.setMarginWidth(0, self.fontMetrics.width("0000") + 5)

        self.setAutoCompletionReplaceWord(True)
        # minimum number of letters to be typed before list is displayed
        self.setAutoCompletionThreshold(2)

        if self.useData.SETTINGS["EnableFolding"] == "True":
            self.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)

        # Braces matching
        # TODO: Causes flicker when selecting text. I suspect it has
        # the layout and widgets placed on top of it
        if self.useData.SETTINGS["MatchBraces"] == "True":
            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        if self.useData.SETTINGS["ShowEdgeLine"] == 'True':
            if self.useData.SETTINGS["EdgeMode"] == 'Line':
                self.setEdgeMode(QsciScintilla.EdgeLine)
            elif self.useData.SETTINGS["EdgeMode"] == 'Background':
                self.setEdgeMode(QsciScintilla.EdgeBackground)
                
        if self.useData.SETTINGS["LineWrap"] == 'True':
            if self.useData.SETTINGS["WrapMode"] == 'Word':
                self.setWrapMode(QsciScintilla.WrapWord)
            elif self.useData.SETTINGS["WrapMode"] == 'Character':
                self.setWrapMode(QsciScintilla.WrapCharacter)
            elif self.useData.SETTINGS["WrapMode"] == 'Whitespace':
                self.setWrapMode(QsciScintilla.WrapWhitespace)

        if self.useData.SETTINGS["ShowCaretLine"] == 'True':
            self.setCaretLineVisible(True)

        self.showWhiteSpaces()
        # set annotation display
        # the annotation font can be changed by changing the default lexer font
        self.setAnnotationDisplay(QsciScintilla.AnnotationBoxed)

        # Edge Mode shows a vetical bar at specific number of chars
        if self.useData.SETTINGS["ShowEdgeLine"] == 'True':
            if self.useData.SETTINGS['EdgeMode'] == "Line":
                self.setEdgeMode(QsciScintilla.EdgeLine)
            else:
                self.setEdgeMode(QsciScintilla.EdgeBackground)
        self.setEdgeColumn(int(self.useData.SETTINGS["EdgeColumn"]))

        # define markers
        # the background markers will not show until the editor has focus
        self.breakpointMarker = self.markerDefine(QsciScintilla.Background)
        self.setMarkerForegroundColor(QtGui.QColor("#000000"),
                                      self.breakpointMarker)
        self.setMarkerBackgroundColor(QtGui.QColor("#ffe1e1"),
                                      self.breakpointMarker)

        self.markerDefine(QtGui.QPixmap(
            os.path.join("Resources", "images", "ui-button-navigation")), 8)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"), 8)

        self.markerDefine(
            QtGui.QPixmap(os.path.join("Resources", "images", "err_mark")), 9)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"), 9)

        self.markerDefine(
            QtGui.QPixmap(os.path.join("Resources", "images", "brk_point")), 10)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"), 10)

        self.markerDefine(QsciScintilla.VerticalLine, 11)
        self.setMarkerBackgroundColor(QtGui.QColor("#EEEE11"), 11)
        self.setMarkerForegroundColor(QtGui.QColor("#EEEE11"), 11)
        self.setMarginWidth(3, self.fontMetrics.width("0"))

        mask = (1 << 8) | (1 << 9)
        self.setMarginMarkerMask(1, mask)
        self.setMarginSensitivity(1, True)
        mask = (1 << 11)
        self.setMarginMarkerMask(3, mask)

        self.showLineNumbers()
        self.setMarkOperationalLines()

        if self.useData.SETTINGS["ShowCaretLine"] == 'True':
            self.setCaretLineVisible(True)

        self.lexer = self.colorScheme.styleEditor(self)
        self.setStyleSheet(StyleSheet.editorStyle)

        self.setKeymap()
        
    def startTokenizeTimer(self):
        self.tokenizeTimer.start(1000)
        
    def startDocTimer(self):
        self.docThreadTimer.start(500)
        
    def startCompletionTimer(self):
        self.completionThreadTimer.start(500)

    def getOperationTokens(self):
        if self.useData.SETTINGS['MarkOperationalLines'] == 'True':
            self.tokenizeThread.tokenize(self.text())

    def displayTokenLines(self):
        self.markerDeleteAll(11)

        for line in self.tokenizeThread.tokenList:
            self.markerAdd(line, 11)

    def showDoc(self, doc, pos):
        if self.isListActive():
            return
        if doc is not None:
            QtGui.QToolTip.showText(self.lastHoverPos, doc, self)

    def getDoc(self):
        self.docThread.doc(
            self.refactor.getProject(), self.text(), self.hoverOffset)

    def mouseReleaseEvent(self, event):
        self.middleMousePressed = False
        super(CodeEditor, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.MidButton or button == QtCore.Qt.MiddleButton:
            self.middleMousePressed = True
        else:
            self.middleMousePressed = False

        super(CodeEditor, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.useData.SETTINGS["DocOnHover"] == "True":
            self.lastHoverPos = event.globalPos()
            self.hoverOffset = self.positionFromPoint(event.pos())

            QtGui.QToolTip.hideText()
            self.startDocTimer()

        # resize view if middle mouse button is held down
        if self.middleMousePressed:
            pos = event.pos()
            delta = pos - self.mousePosition

            x = delta.x()
            y = delta.y()
            if x > 0:
                x = 1
            elif x < 0:
                x = -1
            if y > 0:
                y = 1
            elif y < 0:
                y = -1

            self.editorTabWidget.resizeView(x, y)

        self.mousePosition = event.posF()
        super(CodeEditor, self).mouseMoveEvent(event)

    def createActions(self):
        self.cutAct = QtGui.QAction(
            "Cut", self,
            statusTip="Cut selected text", triggered=self.cut)

        self.copyAct = QtGui.QAction(
            "Copy", self,
            statusTip="Copy selected text", triggered=self.copy)

        self.pasteAct = QtGui.QAction(
            "Paste", self,
            statusTip="Paste text from clipboard",
            triggered=self.paste)

        self.selectToMatchingBraceAct = \
            QtGui.QAction(
                "Select to Matching Brace", self,
                statusTip="Select to Matching Brace",
                          triggered=self.selectToMatchingBrace)

        self.snippetsAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "edit2")),
                "Insert Snippet...", self,
                statusTip="Insert Snippet...",
                          triggered=self.showSnippets)

        self.toggleBookmarkAct = \
            QtGui.QAction(
                "Toggle Bookmark", self,
                statusTip="Toggle Bookmark",
                triggered=self._toggleBookmark)

        self.toggleBreakpointAct = \
            QtGui.QAction(
                "Toggle Line Breakpoint", self,
                statusTip="Toggle Line Breakpoint",
                triggered=self.toggleLineBreakpoint)

        self.takeSnapshotAct = \
            QtGui.QAction("Take Snapshot", self,
                          statusTip="Take Snapshot",
                          triggered=self.takeSnapshot)

        self.zoomAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "zoom")),
            "Zoom", self,
            statusTip="Zoom", triggered=self.showZoomWidget)

        self.indentationGuideAct = \
            QtGui.QAction(
                "Indentation Guide", self,
                statusTip="Indentation Guide",
                          triggered=self.showIndentationGuide)
        self.indentationGuideAct.setCheckable(True)

        self.contextMenu = QtGui.QMenu()
        self.contextMenu.addAction(self.snippetsAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.cutAct)
        self.contextMenu.addAction(self.copyAct)
        self.contextMenu.addAction(self.pasteAct)
        self.contextMenu.addAction(self.selectToMatchingBraceAct)
        self.contextMenu.addAction(self.toggleBookmarkAct)
#        self.contextMenu.addAction(self.toggleBreakpointAct)

        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.refactor.findDefAct)
        self.contextMenu.addAction(self.refactor.findOccurrencesAct)

        self.contextMenu.addMenu(self.refactor.refactorMenu)

        self.viewMenu = self.contextMenu.addMenu("View")
        self.viewMenu.addAction(self.editorTabWidget.vSplitEditorAct)
        self.viewMenu.addAction(self.editorTabWidget.hSplitEditorAct)
        self.viewMenu.addAction(self.editorTabWidget.noSplitEditorAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.indentationGuideAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.zoomAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.takeSnapshotAct)

    def contextMenuEvent(self, event):
        filePath = self.DATA['filePath']
        isProjectFile = self.editorTabWidget.isProjectFile(filePath)
        self.refactor.refactorMenu.setEnabled(isProjectFile)
        self.refactor.findOccurrencesAct.setEnabled(isProjectFile)

        hasSelection = self.hasSelectedText()
        self.copyAct.setEnabled(hasSelection)
        self.cutAct.setEnabled(hasSelection)

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

    def startCompletion(self):
        if self.useData.SETTINGS["EnableAutoCompletion"] == "True":
            if self.useData.SETTINGS["AutoCompletion"] == "Api":
                lineno, col = self.getCursorPosition()
                self.completionCallPos = self.getCursorPosition()
                lineText = self.text(lineno)[:col]

                ropeProject = self.refactor.getProject()
                offset = self.getOffset()

                self.autoCompletionThread.complete(
                    self.refactor.root,
                        ropeProject, offset, self.text(), lineText, col)

    def showCompletions(self, result):
        if len(result) > 0:
            if self.hasFocus():
                self.showUserList(
                    self.autoCompletionThread.completionType, result)
        else:
            self.cancelList()

    def insertText(self, id, text):
        word = self.get_current_word()
        if not word:
            pass
        else:
            self.deleteWordToLeft()
        self.removeSelectedText()
        if id == 1:
            file = open(os.path.join(self.useData.appPathDict[
                        "snippetsdir"], text), 'r')
            cmpl = file.readlines()
            file.close()
            line, col = self.getCursorPosition()
            if self.text(line).strip() == '':
                padding = ' ' * col
                paddedText = ''
                for i in range(len(cmpl)):
                    textLine = padding + cmpl[i]
                    paddedText += textLine
                self.setCursorPosition(line, 0)
                self.insert(paddedText)
            else:
                self.insert(cmpl[0])
        elif id == 2:
            # TODO: Insert must check for brackets after inserting functions.
            x = text.split()
            cmpl = x[0]
            type = x[2].strip(")")
            self.insert(cmpl)
        elif id == 3:
            cmpl = text.rstrip(os.path.sep)
            self.insert(cmpl)
        self.moveCursorWordRight()

    def takeSnapshot(self):
        reply = QtGui.QMessageBox.warning(self, "Snapshot",
                                          "Take a snapshot of the current module state?",
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            subStack = self.editorTabWidget.currentWidget()
            subStack.widget(1).setText(self.text())
        else:
            return

    def toggleLineBreakpoint(self):
        line, index = self.getCursorPosition()
        if self.markersAtLine(line) != 0:
            self.markerDelete(line, self.breakpointMarker)
        else:
            self.markerAdd(line, self.breakpointMarker)
        self.ensureLineVisible(line - 1)

    def updateLexer(self, lexer):
        self.lexer = lexer
        self.setLexer(lexer)

    def _toggleBookmark(self):
        nmargin = 0
        nline = self.getCursorPosition()[0]

        self.toggleBookmark(nmargin, nline)

    def toggleBookmark(self, nmargin, nline, modifiers=None):
        for handle in self.DATA["bookmarkList"]:
            if self.markerLine(handle) == nline:
                self.DATA["bookmarkList"].remove(handle)
                self.markerDeleteHandle(handle)

                markersExist = self.bookmarksExist()
                self.editorTabWidget.enableBookmarkButtons(markersExist)
                return
        handle = self.markerAdd(nline, 8)
        self.DATA["bookmarkList"].append(handle)

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

    def showSnippets(self):
        try:
            snippetList = os.listdir(
                self.useData.appPathDict["snippetsdir"])
        except:
            self.notification.showMessage("Could not fetch snippets.")
            return
        if len(snippetList) > 0:
            self.showUserList(1, snippetList)
        else:
            self.notification.showMessage("No snippets available.")

    def clearErrorMarkerAndIndicator(self):
        self.clearAllIndicators(self.syntaxErrorIndicator)
        self.clearAnnotations()
        self.markerDeleteAll(9)

    def setAutoCompletion(self):
        if self.useData.SETTINGS["EnableAutoCompletion"] == "False":
            self.setAutoCompletionSource(QsciScintilla.AcsNone)
            return
        if self.useData.SETTINGS["AutoCompletion"] == "Api":
            self.setAutoCompletionSource(QsciScintilla.AcsNone)
        elif self.useData.SETTINGS["AutoCompletion"] == "Document":
            self.setAutoCompletionSource(QsciScintilla.AcsDocument)

    def setMarkOperationalLines(self):
        if self.useData.SETTINGS["MarkOperationalLines"] == 'True':
            self.setMarginWidth(3, self.fontMetrics.width("0"))
            self.getOperationTokens()
        else:
            self.markerDeleteAll(11)
            self.setMarginWidth(3, 0)

    def getOffset(self):
        offset = self.currentPosition()
        return offset

    def showLine(self, lineNum, highlight=True):
        if highlight:
            self.setSelection(
                lineNum, 0, lineNum, self.lineLength(lineNum) - 1)
        self.ensureLineVisible(lineNum)

    def showIndentationGuide(self):
        if self.indentationGuides():
            self.setIndentationGuides(False)
        else:
            self.setIndentationGuides(True)

    def showZoomWidget(self):
        self.zoomWidget.show()

    def showWhiteSpaces(self):
        if self.useData.SETTINGS["ShowWhiteSpaces"] == 'True':
            self.setWhitespaceVisibility(QsciScintilla.WsVisible)
        else:
            self.setWhitespaceVisibility(QsciScintilla.WsInvisible)

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

    def removeBookmarks(self):
        if len(self.DATA["bookmarkList"]) > 0:
            self.DATA["bookmarkList"] = []
            self.markerDeleteAll(8)

    def addCommentPrefix(self, line):
        if self.text(line).strip().startswith('#'):
            pass
        else:
            self.insertAt('#', line, 0)

    def removeCommentPrefix(self, line):
        if self.text(line).strip().startswith('#'):
            lineText = self.text(line)
            commentIndex = lineText.find('#')
            self.setSelection(line, commentIndex, line, commentIndex + 1)
            self.replaceSelectedText('')
        else:
            pass

    def comment(self):
        if self.hasSelectedText():
            lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
            if lineFrom == lineTo:
                self.addCommentPrefix(lineFrom)
            else:
                self.beginUndoAction()
                for i in range(lineFrom, lineTo + 1):
                    self.addCommentPrefix(i)
                self.endUndoAction()
            self.setSelection(lineFrom, indexFrom, lineTo, indexTo)
        else:
            line, index = self.getCursorPosition()
            self.addCommentPrefix(line)

    def unComment(self):
        if self.hasSelectedText():
            lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
            if lineFrom == lineTo:
                self.removeCommentPrefix(lineFrom)
            else:
                self.beginUndoAction()
                for i in range(lineFrom, lineTo + 1):
                    self.removeCommentPrefix(i)
                self.endUndoAction()
            self.setSelection(lineFrom, indexFrom, lineTo, indexTo)
        else:
            line, index = self.getCursorPosition()
            self.removeCommentPrefix(line)

    def replaceTabsWithSpaces(self):
        text = self.text()
        text = text.replace('\t', ' ' * 4)
        self.selectAll()
        self.replaceSelectedText(text)

    def removeTrailingWhitespaces(self):
        self.beginUndoAction()
        for i in range(self.lines()):
            text = self.text(i)
            white_len = len(text) - len(text.rstrip())
            if white_len > 1:
                self.setSelection(i, self.lineLength(i) - white_len, i,
                                  self.lineLength(i) - 1)
                self.removeSelectedText()
        self.endUndoAction()

    def setKeymap(self):
        self.updateKeymap(self.useData)

        shortcuts = self.useData.CUSTOM_SHORTCUTS

        self.cutAct.setShortcut(shortcuts["Editor"]["Cut-Selection"][0])
        self.copyAct.setShortcut(shortcuts["Editor"]["Copy-Selection"][0])
        self.pasteAct.setShortcut(shortcuts["Editor"]["Paste"][0])

        self.shortSnippets = QtGui.QShortcut(
            shortcuts["Ide"]["Snippets"], self)
        self.shortSnippets.activated.connect(self.showSnippets)

        self.shortIndentationGuide = QtGui.QShortcut(
            shortcuts["Ide"]["Toggle-Indentation-Guide"], self)
        self.shortIndentationGuide.activated.connect(self.showIndentationGuide)

        self.shortShowCompletion = QtGui.QShortcut(
            shortcuts["Ide"]["Show-Completion"], self)
        self.shortShowCompletion.activated.connect(self.startCompletion)

        self.shortToggleBreakpoint = QtGui.QShortcut(
            shortcuts["Ide"]["Toggle-Breakpoint"], self)
        self.shortToggleBreakpoint.activated.connect(self.toggleLineBreakpoint)

        self.shortNextBookmark = QtGui.QShortcut(
            shortcuts["Ide"]["Next-Bookmark"], self)
        self.shortNextBookmark.activated.connect(self.findNextBookmark)

        self.shortPreviousBookmark = QtGui.QShortcut(
            shortcuts["Ide"]["Previous-Bookmark"], self)
        self.shortPreviousBookmark.activated.connect(self.findPreviousBookmark)

        self.shortComment = QtGui.QShortcut(
            shortcuts["Ide"]["Comment"], self)
        self.shortComment.activated.connect(self.comment)

        self.shortUncomment = QtGui.QShortcut(
            shortcuts["Ide"]["Uncomment"], self)
        self.shortUncomment.activated.connect(self.unComment)

        self.shortZoomIn = QtGui.QShortcut(
            shortcuts["Editor"]["Zoom-In"][0], self)
        self.shortZoomIn.activated.connect(self.zoomWidget.zoomIn)

        self.shortZoomOut = QtGui.QShortcut(
            shortcuts["Editor"]["Zoom-Out"][0], self)
        self.shortZoomOut.activated.connect(self.zoomWidget.zoomOut)
