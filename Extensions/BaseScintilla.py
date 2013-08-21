# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2012 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a compatability interface class to QsciScintilla.
"""

import re
from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciScintilla


class BaseScintilla(QsciScintilla):

    def __init__(self, useData, parent=None):
        QsciScintilla.__init__(self, parent)

    def updateShortcuts(self, useData):
        self.clearKeys()

        shortcuts = useData.CUSTOM_DEFAULT_SHORTCUTS

        self.shortUndo = QtGui.QShortcut(
            shortcuts["Editor"]["Undo-Last-Command"][0], self)
        self.shortUndo.activated.connect(self.undo)

        self.shortRedo = QtGui.QShortcut(
            shortcuts["Editor"]["Redo-Last-Command"][0], self)
        self.shortRedo.activated.connect(self.redo)

        self.shortCut = QtGui.QShortcut(
            shortcuts["Editor"]["Cut-Selection"][0], self)
        self.shortCut.activated.connect(self.cut)

        self.shortCopy = QtGui.QShortcut(
            shortcuts["Editor"]["Copy-Selection"][0], self)
        self.shortCopy.activated.connect(self.copy)

        self.shortPaste = QtGui.QShortcut(
            shortcuts["Editor"]["Paste"][0], self)
        self.shortPaste.activated.connect(self.paste)

        self.shortSelectToMatchingBrace = QtGui.QShortcut(
            shortcuts["Editor"]["Select-to-Matching-Brace"][0], self)
        self.shortSelectToMatchingBrace.activated.connect(
            self.selectToMatchingBrace)

        self.shortIndent = QtGui.QShortcut(
            shortcuts["Editor"]["Indent-One-Level"][0], self)
        self.shortIndent.activated.connect(self.increaseIndent)

        self.shortUnindent = QtGui.QShortcut(
            shortcuts["Editor"]["De-indent-One-Level"][0], self)
        self.shortUnindent.activated.connect(self.decreaseIndent)

        self.shortSelectAll = QtGui.QShortcut(
            shortcuts["Editor"]["Select-All"][0], self)
        self.shortSelectAll.activated.connect(self.selectAll)

        self.shortUppercase = QtGui.QShortcut(
            shortcuts["Editor"]["Convert-Selection-To-Upper-Case"][0], self)
        self.shortUppercase.activated.connect(self.toUpperCase)

        self.shortLowercase = QtGui.QShortcut(
            shortcuts["Editor"]["Convert-Selection-To-Lower-Case"][0], self)
        self.shortLowercase.activated.connect(self.toLowerCase)

        self.shortMoveCursorWordRight = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Right-One-Word"][0], self)
        self.shortMoveCursorWordRight.activated.connect(
            self.moveCursorWordRight)

        self.shortMoveCursorWordLeft = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Left-One-Word"][0], self)
        self.shortMoveCursorWordLeft.activated.connect(self.moveCursorWordLeft)

        self.shortMoveCursorRight = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Right-One-Character"][0], self)
        self.shortMoveCursorRight.activated.connect(self.moveCursorRight)

        self.shortMoveCursorLeft = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Left-One-Character"][0], self)
        self.shortMoveCursorLeft.activated.connect(self.moveCursorLeft)

        self.shortNewLineBelow = QtGui.QShortcut(
            shortcuts["Editor"]["Insert-Newline"][0], self)
        self.shortNewLineBelow.activated.connect(self.newLineBelow)

        self.shortDeleteBack = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Previous-Character"][0], self)
        self.shortDeleteBack.activated.connect(self.deleteBack)

        self.shortDeleteCurrentCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Current-Character"][0], self)
        self.shortDeleteCurrentCharacter.activated.connect(
            self.deleteCurrentCharacter)

        self.shortDeleteWordLeft = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Word-To-Left"][0], self)
        self.shortDeleteWordLeft.activated.connect(self.deleteWordLeft)

        self.shortDeleteWordRight = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Word-To-Right"][0], self)
        self.shortDeleteWordRight.activated.connect(self.deleteWordRight)

        self.shortDeleteLineRight = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Line-To-Left"][0], self)
        self.shortDeleteLineRight.activated.connect(self.deleteLineLeft)

        self.shortDeleteLineRight = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Line-To-Right"][0], self)
        self.shortDeleteLineRight.activated.connect(self.deleteLineRight)

        self.shortExtendSelectionLeft = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Left-One-Character"][0], self)
        self.shortExtendSelectionLeft.activated.connect(
            self.extendSelectionLeft)

        self.shortExtendSelectionRight = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Right-One-Character"][0], self)
        self.shortExtendSelectionRight.activated.connect(
            self.extendSelectionRight)

        self.shortExtendSelectionWordLeft = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Left-One-Word"][0], self)
        self.shortExtendSelectionWordLeft.activated.connect(
            self.extendSelectionWordLeft)

        self.shortExtendSelectionWordRight = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Right-One-Word"][0], self)
        self.shortExtendSelectionWordRight.activated.connect(
            self.extendSelectionWordRight)

        self.shortMoveLeftOneWordPart = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Left-One-Word-Part"][0], self)
        self.shortMoveLeftOneWordPart.activated.connect(
            self.moveLeftOneWordPart)

        self.shortMoveRightOneWordPart = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Right-One-Word-Part"][0], self)
        self.shortMoveRightOneWordPart.activated.connect(
            self.moveRightOneWordPart)

        self.shortStutteredMoveUpOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Stuttered-Move-Up-One-Page"][0], self)
        self.shortStutteredMoveUpOnePage.activated.connect(
            self.stutteredMoveUpOnePage)

        self.shortStutteredMoveDownOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Stuttered-Move-Down-One-Page"][0], self)
        self.shortStutteredMoveDownOnePage.activated.connect(
            self.stutteredMoveDownOnePage)

        self.shortMoveToStartOfDocument = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-Start-Of-Document"][0], self)
        self.shortMoveToStartOfDocument.activated.connect(
            self.moveToStartOfDocument)

        self.shortMoveToEndOfDocument = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-End-Of-Document"][0], self)
        self.shortMoveToEndOfDocument.activated.connect(
            self.moveToEndOfDocument)

        self.shortMoveDownOneParagraph = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Down-One-Paragraph"][0], self)
        self.shortMoveDownOneParagraph.activated.connect(
            self.moveDownOneParagraph)

        self.shortMoveUpOneParagraph = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Up-One-Paragraph"][0], self)
        self.shortMoveUpOneParagraph.activated.connect(
            self.moveUpOneParagraph)

        self.shortExtendSelectionUpOneParagraph = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Up-One-Paragraph"][0], self)
        self.shortExtendSelectionUpOneParagraph.activated.connect(
            self.extendSelectionUpOneParagraph)

        self.shortExtendSelectionDownOneParagraph = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Down-One-Paragraph"][0], self)
        self.shortExtendSelectionDownOneParagraph.activated.connect(
            self.extendSelectionDownOneParagraph)

        self.shortExtendSelectionDownOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Down-One-Line"][0], self)
        self.shortExtendSelectionDownOneLine.activated.connect(
            self.extendSelectionDownOneLine)

        self.shortExtendSelectionUpOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Up-One-Line"][0], self)
        self.shortExtendSelectionUpOneLine.activated.connect(
            self.extendSelectionUpOneLine)

        self.shortExtendSelectionLeftOneCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Left-One-Character"][0], self)
        self.shortExtendSelectionLeftOneCharacter.activated.connect(
            self.extendSelectionLeftOneCharacter)

        self.shortExtendSelectionRightOneCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Right-One-Character"][0], self)
        self.shortExtendSelectionRightOneCharacter.activated.connect(
            self.extendSelectionRightOneCharacter)

        self.shortExtendSelectionUpOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Up-One-Page"][0], self)
        self.shortExtendSelectionUpOnePage.activated.connect(
            self.extendSelectionUpOnePage)

        self.shortExtendSelectionDownOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Down-One-Page"][0], self)
        self.shortExtendSelectionDownOnePage.activated.connect(
            self.extendSelectionDownOnePage)

        self.shortExtendRectangularSelectionDownOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-Down-One-Line"][0], self)
        self.shortExtendRectangularSelectionDownOneLine.activated.connect(
            self.extendRectangularSelectionDownOneLine)

        self.shortCopyCurrentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Copy-Current-Line"][0], self)
        self.shortCopyCurrentLine.activated.connect(
            self.copyCurrentLine)

        self.shortCutCurrentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Cut-Current-Line"][0], self)
        self.shortCutCurrentLine.activated.connect(
            self.cutCurrentLine)

        self.shortDuplicateTheCurrentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Duplicate-The-Current-Line"][0], self)
        self.shortDuplicateTheCurrentLine.activated.connect(
            self.duplicateTheCurrentLine)

        self.shortDuplicateSelection = QtGui.QShortcut(
            shortcuts["Editor"]["Duplicate-Selection"][0], self)
        self.shortDuplicateSelection.activated.connect(
            self.duplicateSelection)

        self.shortTransposeCurrentAndPreviousLines = QtGui.QShortcut(
            shortcuts["Editor"]["Transpose-Current-And-Previous-Lines"][0], self)
        self.shortTransposeCurrentAndPreviousLines.activated.connect(
            self.transposeCurrentAndPreviousLines)

        self.shortMoveSelectedLinesDownOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Selected-Lines-Down-One-Line"][0], self)
        self.shortMoveSelectedLinesDownOneLine.activated.connect(
            self.moveSelectedLinesDownOneLine)

        self.shortMoveSelectedLinesUpOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Selected-Lines-Up-One-Line"][0], self)
        self.shortMoveSelectedLinesUpOneLine.activated.connect(
            self.moveSelectedLinesUpOneLine)

        self.shortExtendRectangularSelectionRightOneCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-Right-One-Character"][0], self)
        self.shortExtendRectangularSelectionRightOneCharacter.activated.connect(
            self.extendRectangularSelectionRightOneCharacter)

        self.shortExtendRectangularSelectionLeftOneCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-Left-One-Character"][0], self)
        self.shortExtendRectangularSelectionLeftOneCharacter.activated.connect(
            self.extendRectangularSelectionLeftOneCharacter)

        self.shortExtendSelectionToStartOfDocument = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-Start-Of-Document"][0], self)
        self.shortExtendSelectionToStartOfDocument.activated.connect(
            self.extendSelectionToStartOfDocument)

        self.shortExtendSelectionToEndOfDocument = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-End-Of-Document"][0], self)
        self.shortExtendSelectionToEndOfDocument.activated.connect(
            self.extendSelectionToEndOfDocument)

        self.shortFormfeed = QtGui.QShortcut(
            shortcuts["Editor"]["Formfeed"][0], self)
        self.shortFormfeed.activated.connect(
            self.formfeed)

        self.shortCancel = QtGui.QShortcut(
            shortcuts["Editor"]["Cancel"][0], self)
        self.shortCancel.activated.connect(
            self.cancel)

        self.shortScrollViewDownOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Scroll-View-Down-One-Line"][0], self)
        self.shortScrollViewDownOneLine.activated.connect(
            self.scrollViewDownOneLine)

        self.shortScrollViewUpOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Scroll-View-Up-One-Line"][0], self)
        self.shortScrollViewUpOneLine.activated.connect(
            self.scrollViewUpOneLine)

        self.shortScrollToStartOfDocument = QtGui.QShortcut(
            shortcuts["Editor"]["Scroll-To-Start-Of-Document"][0], self)
        self.shortScrollToStartOfDocument.activated.connect(
            self.scrollToStartOfDocument)

        self.shortScrollToEndOfDocument = QtGui.QShortcut(
            shortcuts["Editor"]["Scroll-To-End-Of-Document"][0], self)
        self.shortScrollToEndOfDocument.activated.connect(
            self.scrollToEndOfDocument)

        self.shortScrollVerticallyToCentreCurrentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Scroll-Vertically-To-Centre-Current-Line"][0], self)
        self.shortScrollVerticallyToCentreCurrentLine.activated.connect(
            self.scrollVerticallyToCentreCurrentLine)

        self.shortMoveDownOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Down-One-Line"][0], self)
        self.shortMoveDownOneLine.activated.connect(
            self.moveDownOneLine)

        self.shortMoveUpOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Up-One-Line"][0], self)
        self.shortMoveUpOneLine.activated.connect(
            self.moveUpOneLine)

        self.shortToggleInsertOrOvertype = QtGui.QShortcut(
            shortcuts["Editor"]["Toggle-Insert-or-Overtype"][0], self)
        self.shortToggleInsertOrOvertype.activated.connect(
            self.toggleInsertOrOvertype)

        self.shortDeleteRightToEndOfNextWord = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Right-To-End-Of-Next-Word"][0], self)
        self.shortDeleteRightToEndOfNextWord.activated.connect(
            self.deleteRightToEndOfNextWord)

        self.shortMoveCursorToEOL = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-End-Of-Document-Line"][0], self)
        self.shortMoveCursorToEOL.activated.connect(
            self.moveCursorToEOL)

        self.shortMoveCursorToBOL = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-Start-Of-Document-Line"][0], self)
        self.shortMoveCursorToBOL.activated.connect(
            self.moveCursorToBOL)

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

    def extendRectangularSelectionUpOneLine(self):
        """
        Extend the rectangular selection up one line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEUPRECTEXTEND)

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
        """
        Public method to scroll the text area.

        @param lines number of lines to scroll (negative scrolls up,
            positive scrolls down) (integer)
        """
        self.SendScintilla(QsciScintilla.SCI_LINESCROLL, 0, lines)

    def moveCursorToEOL(self):
        """
        Move to the end of the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEEND)

    def moveCursorToBOL(self):
        """
        Move to the start of the displayed or document line.
        """
        self.SendScintilla(QsciScintilla.SCI_HOMEWRAP)

    def moveCursorLeft(self):
        """
        Public method to move the cursor left.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARLEFT)

    def moveCursorRight(self):
        """
        Public method to move the cursor right.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARRIGHT)

    def moveCursorWordLeft(self):
        """
        Public method to move the cursor left one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFT)

    def moveCursorWordRight(self):
        """
        Public method to move the cursor right one word.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHT)

    def newLineBelow(self):
        """
        Insert a platform dependent newline.
        """
        self.SendScintilla(QsciScintilla.SCI_NEWLINE)

    def deleteBack(self):
        """
        Public method to delete the character to the left of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELETEBACK)

    def delete(self):
        """
        Public method to delete the character to the right of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_CLEAR)

    def deleteWordLeft(self):
        """
        Public method to delete the word to the left of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELWORDLEFT)

    def deleteWordRight(self):
        """
        Public method to delete the word to the right of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELWORDRIGHT)

    def deleteLineLeft(self):
        """
        Public method to delete the line to the left of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELLINELEFT)

    def deleteLineRight(self):
        """
        Public method to delete the line to the right of the cursor.
        """
        self.SendScintilla(QsciScintilla.SCI_DELLINERIGHT)

    def extendSelectionLeft(self):
        """
        Public method to extend the selection one character to the left.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARLEFTEXTEND)

    def extendSelectionRight(self):
        """
        Public method to extend the selection one character to the right.
        """
        self.SendScintilla(QsciScintilla.SCI_CHARRIGHTEXTEND)

    def extendSelectionWordLeft(self):
        """
        Public method to extend the selection one word to the left.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDLEFTEXTEND)

    def extendSelectionWordRight(self):
        """
        Public method to extend the selection one word to the right.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDRIGHTEXTEND)

    def extendSelectionToBOL(self):
        """
        Public method to extend the selection to the beginning of the line.
        """
        self.SendScintilla(QsciScintilla.SCI_VCHOMEEXTEND)

    def extendSelectionToEOL(self):
        """
        Public method to extend the selection to the end of the line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDEXTEND)

    def moveLeftOneWordPart(self):
        """
        Public method to extend the selection to the end of the line.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDPARTLEFT)

    def moveRightOneWordPart(self):
        """
        Public method to extend the selection to the end of the line.
        """
        self.SendScintilla(QsciScintilla.SCI_WORDPARTRIGHT)

    def stutteredMoveUpOnePage(self):
        """
        Public method to extend the selection to the end of the line.
        """
        self.SendScintilla(QsciScintilla.SCI_STUTTEREDPAGEUP)

    def stutteredMoveDownOnePage(self):
        """
        Stuttered move down one page.
        """
        self.SendScintilla(QsciScintilla.SCI_STUTTEREDPAGEDOWN)

    def clearKeys(self):
        """
        Protected method to clear the key commands.
        """
        # call into the QsciCommandSet
        self.standardCommands().clearKeys()

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

    def get_position(self, position):
        if position == 'cursor':
            return self.getCursorPosition()
        elif position == 'sol':
            line, _index = self.getCursorPosition()
            return (line, 0)
        elif position == 'eol':
            line, _index = self.getCursorPosition()
            return (line, self.__get_line_end_index(line))
        elif position == 'eof':
            line = self.lines() - 1
            return (line, len(self.text(line)))
        elif position == 'sof':
            return (0, 0)
        else:
            # Assuming that input argument was already a position
            return position

    def __get_line_end_index(self, line):
        """Return the line end index"""
        pos = self.SendScintilla(QsciScintilla.SCI_GETLINEENDPOSITION, line)
        _, index = self.lineIndexFromPosition(pos)
        return index

    def get_character(self, position):
        """Return character at *position*"""
        line, index = self.get_position(position)
        return self.text(line)[index]

    def get_coordinates(self, position):
        line, index = self.get_position(position)
        return self.get_coordinates_from_lineindex(line, index)

    def get_coordinates_from_lineindex(self, line, index):
        """Return cursor x, y point coordinates for line, index position"""
        pos = self.positionFromLineIndex(line, index)
        x_pt = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, pos)
        y_pt = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, pos)
        return x_pt, y_pt

    def currentPosition(self):
        """
        Public method to get the current position.

        @return absolute position of the cursor (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)

    def positionFromPoint(self, point):
        """
        Public method to calculate the scintilla position from a point in the
        window.

        @param point point in the window (QPoint)
        @return scintilla position (integer) or -1 to indicate, that the point
            is not near any character
        """
        return self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINTCLOSE,
                                  point.x(), point.y())

    def clear_selection(self):
        """Clear current selection"""
        line, index = self.getCursorPosition()
        self.setSelection(line, index, line, index)

    def get_text(self, position_from=None, position_to=None):
        """
        Return text between *position_from* and *position_to*
        Positions may be positions or 'sol', 'eol', 'sof', 'eof' or 'cursor'
        """
        if position_from is None and position_to is None:
            return self.text()
        self.__select_text(position_from, position_to)
        text = self.selectedText()
        self.clear_selection()
        return text

    def __select_text(self, position_from, position_to):
        line_from, index_from = self.get_position(position_from)
        line_to, index_to = self.get_position(position_to)
        self.setSelection(line_from, index_from, line_to, index_to)

    def setLexer(self, lex=None):
        """
        Public method to set the lexer.

        @param lex the lexer to be set or None to reset it.
        """
        super().setLexer(lex)
        if lex is None:
            self.clearStyles()

    def clearStyles(self):
        """
        Public method to set the styles according the selected Qt style.
        """
        palette = QtGui.QApplication.palette()
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE,
                           QsciScintilla.STYLE_DEFAULT, palette.color(QtGui.QPalette.Text))
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK,
                           QsciScintilla.STYLE_DEFAULT, palette.color(QtGui.QPalette.Base))
        self.SendScintilla(QsciScintilla.SCI_STYLECLEARALL)
        self.SendScintilla(QsciScintilla.SCI_CLEARDOCUMENTSTYLE)

    def get_absolute_coordinates(self):
        cx, cy = self.get_coordinates('cursor')
        qPoint = QtCore.QPoint(cx, cy)
        point = self.mapToGlobal(qPoint)
        return point

    def get_current_word(self):
        """Return current word, i.e. word at cursor position"""
        line, index = self.getCursorPosition()
        text = self.text(line)
        wc = self.wordCharacters()
        if wc is None:
            regexp = QtCore.QRegExp('[^\w_]')
        else:
            regexp = QtCore.QRegExp('[^%s]' % re.escape(wc))
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

    def lineAt(self, pos):
        """
        Public method to calculate the line at a position.

        This variant is able to calculate the line for positions in the
        margins and for empty lines.

        @param pos position to calculate the line for (integer or QPoint)
        @return linenumber at position or -1, if there is no line at pos
            (integer, zero based)
        """
        if isinstance(pos, int):
            scipos = pos
        else:
            scipos = \
                self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT,
                                   pos.x(), pos.y())
        line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, scipos)
        if line >= self.lines():
            line = -1
        return line

    def foldLevelAt(self, line):
        """
        Public method to get the fold level of a line of the document.

        @param line line number (integer)
        @return fold level of the given line (integer)
        """
        lvl = self.SendScintilla(QsciScintilla.SCI_GETFOLDLEVEL, line)
        return \
            (lvl & QsciScintilla.SC_FOLDLEVELNUMBERMASK) - \
            QsciScintilla.SC_FOLDLEVELBASE

    def styleAt(self, pos):
        """
        Public method to get the style at a position in the text.

        @param pos position in the text (integer)
        @return style at the requested position or 0, if the position
            is negative or past the end of the document (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, pos)

    def linesOnScreen(self):
        """
        Public method to get the amount of visible lines.

        @return amount of visible lines (integer)
        """
        return self.SendScintilla(QsciScintilla.SCI_LINESONSCREEN)

    def charAt(self, pos):
        """
        Public method to get the character at a position in the text observing
        multibyte characters.

        @param pos position in the text (integer)
        @return character at the requested position or empty string, if the
            position is negative or past the end of the document (string)
        """
        ch = self.byteAt(pos)
        if ch and ord(ch) > 127 and self.isUtf8():
            if (ch[0] & 0xF0) == 0xF0:
                utf8Len = 4
            elif (ch[0] & 0xE0) == 0xE0:
                utf8Len = 3
            elif (ch[0] & 0xC0) == 0xC0:
                utf8Len = 2
            while len(ch) < utf8Len:
                pos += 1
                ch += self.byteAt(pos)
            return ch.decode('utf8')
        else:
            return ch.decode()

    def byteAt(self, pos):
        """
        Public method to get the raw character (bytes) at a position in the
        text.

        @param pos position in the text (integer)
        @return raw character at the requested position or empty bytes, if the
            position is negative or past the end of the document (bytes)
        """
        char = self.SendScintilla(QsciScintilla.SCI_GETCHARAT, pos)
        if char == 0:
            return b""
        if char < 0:
            char += 256
        return bytes.fromhex("{0:02x}".format(char))

    def foldFlagsAt(self, line):
        """
        Public method to get the fold flags of a line of the document.

        @param line line number (integer)
        @return fold flags of the given line (integer)
        """
        lvl = self.SendScintilla(QsciScintilla.SCI_GETFOLDLEVEL, line)
        return lvl & ~QsciScintilla.SC_FOLDLEVELNUMBERMASK

    def clearIndicator(self, indicator, sline, sindex, eline, eindex):
        """
        Public method to clear an indicator for the given range.

        @param indicator number of the indicator (integer,
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param sline line number of the indicator start (integer)
        @param sindex index of the indicator start (integer)
        @param eline line number of the indicator end (integer)
        @param eindex index of the indicator end (integer)
        """
        spos = self.positionFromLineIndex(sline, sindex)
        epos = self.positionFromLineIndex(eline, eindex)
        self.clearIndicatorRange(indicator, spos, epos - spos)

    def clearAllIndicators(self, indicator):
        """
        Public method to clear all occurrences of an indicator.

        @param indicator number of the indicator (integer,
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        """
        self.clearIndicatorRange(0, 0, self.lines(), 0, indicator)

    def setFoldMarkersColors(self, foreColor, backColor):
        """
        Public method to set the foreground and background colors of the
        fold markers.

        @param foreColor foreground color (QColor)
        @param backColor background color (QColor)
        """
        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDER, foreColor)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDER, backColor)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDEROPEN, foreColor)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDEROPEN, backColor)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDEROPENMID, foreColor)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDEROPENMID, backColor)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDERSUB, foreColor)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDERSUB, backColor)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDERTAIL, foreColor)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDERTAIL, backColor)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDERMIDTAIL, foreColor)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDERMIDTAIL, backColor)

        self.SendScintilla(QsciScintilla.SCI_MARKERSETFORE,
                           QsciScintilla.SC_MARKNUM_FOLDEREND, foreColor)
        self.SendScintilla(QsciScintilla.SCI_MARKERSETBACK,
                           QsciScintilla.SC_MARKNUM_FOLDEREND, backColor)

    def clearSearchIndicators(self):
        " Hides the search indicator "
        self.clearAllIndicators(self.matchIndicator)
        return

    def setSearchIndicator(self, startPos, indicLength):
        " Sets a single search indicator "
        self.setIndicatorRange(self.matchIndicator, startPos, indicLength)
        return

    def __doSearchTarget(self):
        """
        Private method to perform the search in target.

        @return flag indicating a successful search (boolean)
        """
        if self.__targetSearchStart == self.__targetSearchEnd:
            self.__targetSearchActive = False
            return False

        self.SendScintilla(QsciScintilla.SCI_SETTARGETSTART,
                           self.__targetSearchStart)
        self.SendScintilla(QsciScintilla.SCI_SETTARGETEND,
                           self.__targetSearchEnd)
        self.SendScintilla(QsciScintilla.SCI_SETSEARCHFLAGS,
                           self.__targetSearchFlags)
        targetSearchExpr = self._encodeString(self.__targetSearchExpr)
        pos = self.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET,
                                 len(targetSearchExpr),
                                 targetSearchExpr)

        if pos == -1:
            self.__targetSearchActive = False
            return False

        targend = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
        self.__targetSearchStart = targend

        return True

    def _encodeString(self, string):
        """
        Protected method to encode a string depending on the current mode.

        @param string string to be encoded (str)
        @return encoded string (bytes)
        """
        if isinstance(string, bytes):
            return string
        else:
            if self.isUtf8():
                return string.encode("utf-8")
            else:
                return string.encode("latin-1")

    def findFirstTarget(self, expr_, re_, cs_, wo_,
                        begline=-1, begindex=-1, endline=-1, endindex=-1,
                        ws_=False):
        """
        Public method to search in a specified range of text without
        setting the selection.

        @param expr_ search expression (string)
        @param re_ flag indicating a regular expression (boolean)
        @param cs_ flag indicating a case sensitive search (boolean)
        @param wo_ flag indicating a word only search (boolean)
        @keyparam begline line number to start from (-1 to indicate current
            position) (integer)
        @keyparam begindex index to start from (-1 to indicate current
            position) (integer)
        @keyparam endline line number to stop at (-1 to indicate end of
            document) (integer)
        @keyparam endindex index number to stop at (-1 to indicate end of
            document) (integer)
        @keyparam ws_ flag indicating a word start search (boolean)
        @return flag indicating a successful search (boolean)
        """
        self.__targetSearchFlags = 0
        if re_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_REGEXP
        if cs_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_MATCHCASE
        if wo_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_WHOLEWORD
        if ws_:
            self.__targetSearchFlags |= QsciScintilla.SCFIND_WORDSTART

        if begline < 0 or begindex < 0:
            self.__targetSearchStart = self.SendScintilla(
                QsciScintilla.SCI_GETCURRENTPOS)
        else:
            self.__targetSearchStart = self.positionFromLineIndex(
                begline, begindex)

        if endline < 0 or endindex < 0:
            self.__targetSearchEnd = self.SendScintilla(
                QsciScintilla.SCI_GETTEXTLENGTH)
        else:
            self.__targetSearchEnd = self.positionFromLineIndex(
                endline, endindex)

        self.__targetSearchExpr = expr_

        if self.__targetSearchExpr:
            self.__targetSearchActive = True

            return self.__doSearchTarget()

        return False

    def findNextTarget(self):
        """
        Public method to find the next occurrence in the target range.

        @return flag indicating a successful search (boolean)
        """
        if not self.__targetSearchActive:
            return False

        return self.__doSearchTarget()

    def setCurrentIndicator(self, indicator):
        """
        Public method to set the current indicator.

        @param indicator number of the indicator (integer,
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @exception ValueError the indicator or style are not valid
        """
        if indicator < QsciScintilla.INDIC_CONTAINER or \
           indicator > QsciScintilla.INDIC_MAX:
            raise ValueError("indicator number out of range")

        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator)

    def setIndicatorRange(self, indicator, spos, length):
        """
        Public method to set an indicator for the given range.

        @param indicator number of the indicator (integer,
            QsciScintilla.INDIC_CONTAINER .. QsciScintilla.INDIC_MAX)
        @param spos position of the indicator start (integer)
        @param length length of the indicator (integer)
        @exception ValueError the indicator or style are not valid
        """
        self.setCurrentIndicator(indicator)
        self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, spos, length)

    def getFoundTarget(self):
        """
        Public method to get the recently found target.

        @return found target as a tuple of starting position and target length
            (integer, integer)
        """
        if self.__targetSearchActive:
            spos = self.SendScintilla(QsciScintilla.SCI_GETTARGETSTART)
            epos = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
            return (spos, epos - spos)
        else:
            return (0, 0)

    def getTargets(self, txt,
                   isRegexp, caseSensitive, wholeWord,
                   lineFrom, indexFrom, lineTo, indexTo):
        " Provides a list of the targets start points and the target length "
        found = self.findFirstTarget(txt, isRegexp, caseSensitive, wholeWord,
                                     lineFrom, indexFrom, lineTo, indexTo)
        foundTargets = []
        while found:
            tgtPos, tgtLen = self.getFoundTarget()
            line, pos = self.lineIndexFromPosition(tgtPos)
            foundTargets.append([line, pos, tgtLen])
            found = self.findNextTarget()
        return foundTargets
