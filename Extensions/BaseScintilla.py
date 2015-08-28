import re
from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciScintilla


class FindOccurenceThread(QtCore.QThread):

    markOccurrence = QtCore.pyqtSignal(list)

    def run(self):
        word = re.escape(self.word)
        if self.wholeWord:
            word = "\\b{0}\\b".format(word)
        flags = re.UNICODE | re.LOCALE
        search = re.compile(word, flags)

        lineno = 0
        foundList = []
        for lineText in self.source.splitlines():
            for i in search.finditer(lineText):
                start = i.start()
                end = i.end()
                foundList.append([lineno, start, end])
            lineno += 1
        self.markOccurrence.emit(foundList)

    def find(self, word, wholeWord, source):
        self.source = source
        self.word = word
        self.wholeWord = wholeWord

        self.start()


class BaseScintilla(QsciScintilla):

    def __init__(self, parent=None):
        QsciScintilla.__init__(self, parent)

    def enableMarkOccurrence(self, useData):
        self.useData = useData

        self.matchIndicator = self.indicatorDefine(QsciScintilla.INDIC_BOX, 9)
        self.setIndicatorForegroundColor(
            QtGui.QColor("#FFCC00"), self.matchIndicator)
        self.setIndicatorDrawUnder(True, self.matchIndicator)

        self.findOccurenceThread = FindOccurenceThread()
        self.findOccurenceThread.markOccurrence.connect(self.markOccurence)

        self.occurrencesTimer = QtCore.QTimer()
        self.occurrencesTimer.setSingleShot(True)
        self.occurrencesTimer.timeout.connect(self.findOccurrences)

        self.cursorPositionChanged.connect(self.startOccurrencesTimer)
        
    def startOccurrencesTimer(self):
        self.occurrencesTimer.start(500)

    def updateKeymap(self, useData):
        standardCommands = self.standardCommands()

        for i, v in useData.DEFAULT_SHORTCUTS["Editor"].items():
            command = standardCommands.find(v[1])
            command.setKey(useData.CUSTOM_SHORTCUTS["Editor"][i][1])

    def findOccurrences(self):
        self.clearAllIndicators(self.matchIndicator)
        if self.useData.SETTINGS['MarkSearchOccurrence'] == 'True':
            wholeWord = True
            if self.hasSelectedText():
                lineFrom_, indexFrom_, lineTo_, indexTo_ = self.getSelection()
                if lineFrom_ != lineTo_:
                    return
                word = self.selectedText().strip()
                if word == '':
                    return
                wholeWord = False
            else:
                word = self.get_current_word()
                if not word:
                    self.clearMatchIndicators()
                    return
            self.findOccurenceThread.find(word, wholeWord, self.text())

    def markOccurence(self, foundList):
        self.clearAllIndicators(self.matchIndicator)
        if len(foundList) == 1:
            return
        for i in foundList:
            self.fillIndicatorRange(
                i[0], i[1], i[0], i[2], self.matchIndicator)

    def moveRightOneWordPart(self):
        """
        Move right one word part.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDPARTRIGHT)

    def moveToEndOfDisplayLine(self):
        """
        Move to the end of the displayed line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDDISPLAY)

    def moveToEndOfNextWord(self):
        """
        Move to the end of the next word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHTEND)

    def moveToStartOfDisplayLine(self):
        """
        Move to the start of the displayed line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEDISPLAY)

    def moveToFirstVisibleCharacterOfDisplayInDocumentLine(self):
        """
        Move to the first visible character of the displayed or document
        line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOMEWRAP)

    def moveToStartOfDisplayOrDocumentLine(self):
        """
        Move to the start of the displayed or document line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEWRAP)

    def deletePreviousCharacterIfNotAtStartOfLine(self):
        """
        Delete the previous character if not at start of line.
        """
        self.SendScintilla(QsciScintilla.SCI_DELETEBACKNOTLINE)

    def extendRectangularSelectionDownOnePage(self):
        """
        Extend the rectangular selection down one page.
        """
        self.SendScintilla(QsciScintilla.SCI_PAGEDOWNRECTEXTEND)

    def extendRectangularSelectionUpOnePage(self):
        """
        Extend the rectangular selection up one page.
        """
        self.SendScintilla(QsciScintilla.SCI_PAGEUPRECTEXTEND)

    def extendSelectionToEndOfDocumentLine(self):
        """
        Extend the selection to the end of the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDEXTEND)

    def extendSelectionToEndOfDisplayLine(self):
        """
        Extend the selection to the end of the displayed line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDDISPLAYEXTEND)

    def stutteredExtendSelectionUpOnePage(self):
        """
        Stuttered extend the selection up one page.
        """
        self.SendScintilla(QsciScintilla.SCI_STUTTEREDPAGEUPEXTEND)

    def extendSelectionToEndOfNextWord(self):
        """
        Extend the selection to the end of the next word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHTENDEXTEND)

    def extendSelectionToFirstVisibleCharacterInDisplayOrDocumentLine(self):
        """
        Extend the selection to the first visible character of the
        displayed or document line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOMEWRAPEXTEND)

    def extendSelectionRightOneWordPart(self):
        """
        Extend the selection right one word part.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDPARTRIGHTEXTEND)

    def deleteCurrentLine(self):
        """
        Delete the current line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEDELETE)

    def extendSelectionToStartOfDisplayOrDocumentLine(self):
        """
        Extend the selection to the start of the displayed or document
        line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEWRAPEXTEND)

    def extendSelectionToFirstVisibleCharacterInDocumentLine(self):
        """
        Extend the selection to the first visible character in the document
        line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOMEEXTEND)

    def moveToEndOfPreviousWord(self):
        """
        Move to the end of the previous word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFTEND)

    def moveToEndOfDisplayOrDocumentLine(self):
        """
        Move to the end of the displayed or document line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDWRAP)

    def extendRectangularSelectionToEndOfDocumentLine(self):
        """
        Extend the rectangular selection to the end of the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDRECTEXTEND)

    def extendSelectionToEndOfDisplayOrDocumentLine(self):
        """
        Extend the selection to the start of the displayed line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEDISPLAYEXTEND)

    def stutteredExtendSelectionDownOnePage(self):
        """
        Stuttered extend the selection down one page.
        """
        self.SendScintilla(QsciScintilla.SCI_STUTTEREDPAGEDOWNEXTEND)

    def extendSelectionToStartOfDocumentLine(self):
        """
        Extend the selection to the start of the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEEXTEND)

    def extendSelectionToEndOfPreviousWord(self):
        """
        Extend the selection to the end of the previous word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFTENDEXTEND)

    def extendSelectionLeftOneWordPart(self):
        """
        Extend the selection left one word part.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDPARTLEFTEXTEND)

    def extendRectangularSelectionToStartOfDocumentLine(self):
        """
        Extend the rectangular selection to the start of the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMERECTEXTEND)

    def extendRectangularSelectionToFirstVisibleCharacterInDocumentLine(self):
        """
        Extend the rectangular selection to the first visible character in
        the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOMERECTEXTEND)

    def moveToFirstVisibleCharacterInDocumentLine(self):
        """
        Move to the first visible character in the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOME)

    def extendRectangularSelectionUpOneLine(self):
        """
        Extend the rectangular selection up one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEUPRECTEXTEND)

    def extendSelectionToStartOfDisplayLine(self):
        """
        Extend the selection to the start of the displayed line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEDISPLAYEXTEND)

    def deleteRightToEndOfNextWord(self):
        """
        Delete right to the end of the next word.
        """
        self.SendScintilla(QsciScintilla.SCI_DELWORDRIGHTEND)

    def toggleInsertOrOvertype(self):
        """
        Toggle insert/overtype.
        """
        self.SendScintilla(QsciScintilla.SCI_EDITTOGGLEOVERTYPE)

    def deleteCurrentCharacter(self):
        """
        Delete the current character.
        """
        self.SendScintilla(QsciScintilla.SCI_CLEAR)

    def moveUpOneLine(self):
        """
        Move up one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEUP)

    def moveDownOneLine(self):
        """
        Move down one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEDOWN)

    def scrollVerticallyToCentreCurrentLine(self):
        """
        Scroll vertically to centre the current line.
        """
        self.SendScintilla(QsciScintilla.SCI_VERTICALCENTRECARET)

    def scrollToEndOfDocument(self):
        """
        Scroll to the end of the document.
        """
        self.SendScintilla(QsciScintilla.SCI_SCROLLTOEND)

    def scrollToStartOfDocument(self):
        """
        Scroll to the start of the document.
        """
        self.SendScintilla(QsciScintilla.SCI_SCROLLTOSTART)

    def scrollViewUpOneLine(self):
        """
        Scroll the view up one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINESCROLLUP)

    def scrollViewDownOneLine(self):
        """
        Scroll the view down one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINESCROLLDOWN)

    def cancel(self):
        """
        Cancel any current operation.
        """
        self.SendScintilla(QsciScintilla.SCI_CANCEL)

    def formfeed(self):
        """
        Insert a formfeed.
        """
        self.SendScintilla(QsciScintilla.SCI_FORMFEED)

    def extendSelectionToEndOfDocument(self):
        """
        Extend the selection to the end of the document.
        """
        self.SendScintilla(QsciScintilla.SCI_DOCUMENTENDEXTEND)

    def extendSelectionToStartOfDocument(self):
        """
        Extend the selection to the start of the document.
        """
        self.SendScintilla(QsciScintilla.SCI_DOCUMENTSTARTEXTEND)

    def extendRectangularSelectionLeftOneCharacter(self):
        """
        Extend the rectangular selection left one character.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARLEFTRECTEXTEND)

    def extendRectangularSelectionRightOneCharacter(self):
        """
        Extend the rectangular selection right one character.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARRIGHTRECTEXTEND)

    def moveSelectedLinesUpOneLine(self):
        """
        Move the selected lines up one line.
        """
        self.SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESUP)

    def moveSelectedLinesDownOneLine(self):
        """
        Move the selected lines down one line.
        """
        self.SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESDOWN)

    def transposeCurrentAndPreviousLines(self):
        """
        Transpose the current and previous lines.
        """
        self.SendScintilla(QsciScintilla.SCI_LINETRANSPOSE)

    def duplicateSelection(self):
        """
        Duplicate the selection.
        """
        self.SendScintilla(QsciScintilla.SCI_SELECTIONDUPLICATE)

    def duplicateTheCurrentLine(self):
        """
        Duplicate the current line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEDUPLICATE)

    def cutCurrentLine(self):
        """
        Cut the current line to the clipboard.
        """
        self.SendScintilla(QsciScintilla.SCI_LINECUT)

    def copyCurrentLine(self):
        """
        Copy the current line to the clipboard.
        """
        self.SendScintilla(QsciScintilla.SCI_LINECOPY)

    def extendRectangularSelectionDownOneLine(self):
        """
        Extend the rectangular selection down one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEDOWNRECTEXTEND)

    def extendSelectionDownOnePage(self):
        """
        Extend the selection down one page.
        """
        self.SendScintilla(QsciScintilla.SCI_PAGEDOWNEXTEND)

    def extendSelectionUpOnePage(self):
        """
        Extend the selection up one page.
        """
        self.SendScintilla(QsciScintilla.SCI_PAGEUPEXTEND)

    def extendSelectionRightOneCharacter(self):
        """
        Extend the selection right one character.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARRIGHTEXTEND)

    def extendSelectionLeftOneCharacter(self):
        """
        Extend the selection left one character.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARLEFTEXTEND)

    def extendSelectionUpOneLine(self):
        """
        Extend the selection up one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEUPEXTEND)

    def extendSelectionDownOneLine(self):
        """
        Extend the selection down one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEDOWNEXTEND)

    def extendSelectionDownOneParagraph(self):
        """
        Extend the selection down one paragraph.
        """
        self.SendScintilla(QsciScintilla.SCI_PARADOWNEXTEND)

    def extendSelectionUpOneParagraph(self):
        """
        Extend the selection up one paragraph.
        """
        self.SendScintilla(QsciScintilla.SCI_PARAUPEXTEND)

    def moveDownOneParagraph(self):
        """
        Move down one paragraph.
        """
        self.SendScintilla(QsciScintilla.SCI_PARADOWN)

    def moveUpOneParagraph(self):
        """
        Move up one paragraph.
        """
        self.SendScintilla(QsciScintilla.SCI_PARAUP)

    def moveToStartOfDocument(self):
        """
        Move to the start of the document.
        """
        self.SendScintilla(QsciScintilla.SCI_DOCUMENTSTART)

    def moveToEndOfDocument(self):
        """
        Move to the end of the document.
        """
        self.SendScintilla(QsciScintilla.SCI_DOCUMENTEND)

    def scrollVertical(self, lines):
        self.SendScintilla(QsciScintilla.SCI_LINESCROLL, 0, lines)

    def moveCursorToEndOfDocumentLine(self):
        """
        Move to the end of the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEEND)

    def moveCursorToStartOfDocumentLine(self):
        """
        Move to the start of the displayed or document line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEWRAP)

    def moveLeftOneCharacter(self):
        """
        Move left one character.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARLEFT)

    def moveCursorRight(self):
        """
        Move right one character.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARRIGHT)

    def moveCursorWordLeft(self):
        """
        Move left one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFT)

    def moveCursorWordRight(self):
        """
        Move right one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHT)

    def insertNewline(self):
        """
        Insert a platform dependent newline.
        """
        self.SendScintilla(QsciScintilla.SCI_NEWLINE)

    def deletePreviousCharacter(self):
        """
        Delete the previous character.
        """
        self.SendScintilla(QsciScintilla.SCI_DELETEBACK)

    def delete(self):
        """
        Delete the current character.
        """
        self.SendScintilla(QsciScintilla.SCI_CLEAR)

    def deleteWordToLeft(self):
        """
        Delete the word to the left.
        """
        self.SendScintilla(QsciScintilla.SCI_DELWORDLEFT)

    def deleteWordToRight(self):
        """
        Delete the word to the right.
        """
        self.SendScintilla(QsciScintilla.SCI_DELWORDRIGHT)

    def deleteLineLeft(self):
        """
        Delete the line to the left.
        """
        self.SendScintilla(QsciScintilla.SCI_DELLINELEFT)

    def deleteLineToRight(self):
        """
        Delete the line to the right.
        """
        self.SendScintilla(QsciScintilla.SCI_DELLINERIGHT)

    def extendSelectionLeftOneWord(self):
        """
        Extend the selection left one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFTEXTEND)

    def extendSelectionWordRight(self):
        """
        Extend the selection right one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHTEXTEND)

    def extendSelectionToBOL(self):
        """
        Extend the selection to the first visible character in the document
        line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOMEEXTEND)

    def moveLeftOneWordPart(self):
        """
        Move left one word part.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDPARTLEFT)

    def stutteredMoveUpOnePage(self):
        """
        Stuttered move up one page.
        """
        self.SendScintilla(QsciScintilla.SCI_STUTTEREDPAGEUP)

    def stutteredMoveDownOnePage(self):
        """
        Stuttered move down one page.
        """
        self.SendScintilla(QsciScintilla.SCI_STUTTEREDPAGEDOWN)

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

    def toLowerCase(self):
        self.SendScintilla(QsciScintilla.SCI_LOWERCASE)

    def toUpperCase(self):
        self.SendScintilla(QsciScintilla.SCI_UPPERCASE)

    def showLineNumbers(self):
        if self.useData.SETTINGS["ShowLineNumbers"] == 'True':
            # Line numbers
            # conventionnaly, margin 0 is for line numbers
            self.setMarginLineNumbers(0, True)
            self.setMarginWidth(0, self.fontMetrics.width("0000") + 5)
        else:
            self.setMarginLineNumbers(0, False)
            self.setMarginWidth(0, 0)

    def position(self, position):
        if position == 'cursor':
            return self.getCursorPosition()
        elif position == 'sol':
            line, _index = self.getCursorPosition()
            return (line, 0)
        elif position == 'eol':
            line, _index = self.getCursorPosition()
            pos = self.SendScintilla(
                QsciScintilla.SCI_GETLINEENDPOSITION, line)
            _, index = self.lineIndexFromPosition(pos)
            return (line, index)
        elif position == 'eof':
            line = self.lines() - 1
            return (line, len(self.text(line)))
        elif position == 'sof':
            return (0, 0)
        else:
            return position

    def coordinates(self, position):
        line, index = self.position(position)

        pos = self.positionFromLineIndex(line, index)
        x_pt = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, pos)
        y_pt = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, pos)
        return x_pt, y_pt

    def currentPosition(self):
        return self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)

    def positionFromPoint(self, point):
        return self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINTCLOSE,
                                  point.x(), point.y())

    def getText(self, positionFrom=None, positionTo=None):
        """
        Return text between *positionFrom* and *positionTo*
        Positions may be positions or 'sol', 'eol', 'sof', 'eof' or 'cursor'
        """
        if positionFrom is None and positionTo is None:
            return self.text()
        self.selectText(positionFrom, positionTo)
        text = self.selectedText()

        # Clear current selection
        line, index = self.getCursorPosition()
        self.setSelection(line, index, line, index)

        return text

    def selectText(self, position_from, position_to):
        line_from, index_from = self.position(position_from)
        line_to, index_to = self.position(position_to)
        self.setSelection(line_from, index_from, line_to, index_to)

    def get_absolute_coordinates(self):
        cx, cy = self.coordinates('cursor')
        qPoint = QtCore.QPoint(cx, cy)
        point = self.mapToGlobal(qPoint)
        return point

    def get_current_word(self):
        """
        Return current word at cursor position
        """
        line, index = self.getCursorPosition()
        text = self.text(line)
        wc = self.wordCharacters()
        if wc is None:
            regexp = QtCore.QRegExp('[^\w_]')
        else:
            regexp = QtCore.QRegExp('[^{0}]'.format(re.escape(wc)))
        start = regexp.lastIndexIn(text, index) + 1
        end = regexp.indexIn(text, index)
        if start == end + 1 and index > 0:
            # we are on a word boundary, try again
            start = regexp.lastIndexIn(text, index - 1) + 1
        if start == -1:
            start = 0
        if end == -1:
            end = len(text)
        if end > start:
            word = text[start:end]
        else:
            word = ''
        return word

    def clearAllIndicators(self, indicator):
        self.clearIndicatorRange(0, 0, self.lines(), 0, indicator)

    def setFoldMarkersColors(self, foreground, background):
        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDER, foreground)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDER, background)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDEROPEN, foreground)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDEROPEN, background)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDEROPENMID, foreground)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDEROPENMID, background)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDERSUB, foreground)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDERSUB, background)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDERTAIL, foreground)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDERTAIL, background)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDERMIDTAIL, foreground)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDERMIDTAIL, background)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDEREND, foreground)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDEREND, background)

    def clearMatchIndicators(self):
        self.clearAllIndicators(self.matchIndicator)
