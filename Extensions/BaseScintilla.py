
import re
from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciScintilla


class BaseScintilla(QsciScintilla):

    def __init__(self, useData, parent=None):
        QsciScintilla.__init__(self, parent)

    def updateShortcuts(self, useData):
        self.standardCommands().clearKeys()

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

        self.shortMoveLeftOneCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Move-Left-One-Character"][0], self)
        self.shortMoveLeftOneCharacter.activated.connect(
            self.moveLeftOneCharacter)

        self.shortInsertNewline = QtGui.QShortcut(
            shortcuts["Editor"]["Insert-Newline"][0], self)
        self.shortInsertNewline.activated.connect(self.insertNewline)

        self.shortDeletePreviousCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Previous-Character"][0], self)
        self.shortDeletePreviousCharacter.activated.connect(
            self.deletePreviousCharacter)

        self.shortDeleteCurrentCharacter = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Current-Character"][0], self)
        self.shortDeleteCurrentCharacter.activated.connect(
            self.deleteCurrentCharacter)

        self.shortDeleteWordToLeft = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Word-To-Left"][0], self)
        self.shortDeleteWordToLeft.activated.connect(self.deleteWordToLeft)

        self.shortDeleteWordToRight = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Word-To-Right"][0], self)
        self.shortDeleteWordToRight.activated.connect(self.deleteWordToRight)

        self.shortDeleteLineToRight = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Line-To-Left"][0], self)
        self.shortDeleteLineToRight.activated.connect(self.deleteLineLeft)

        self.shortDeleteLineToRight = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Line-To-Right"][0], self)
        self.shortDeleteLineToRight.activated.connect(self.deleteLineToRight)

        self.shortExtendSelectionWordLeft = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Left-One-Word"][0], self)
        self.shortExtendSelectionWordLeft.activated.connect(
            self.extendSelectionLeftOneWord)

        self.shortExtendSelectionLeftOneWord = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Right-One-Word"][0], self)
        self.shortExtendSelectionLeftOneWord.activated.connect(
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

        self.shortMoveCursorToEndOfDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-End-Of-Document-Line"][0], self)
        self.shortMoveCursorToEndOfDocumentLine.activated.connect(
            self.moveCursorToEndOfDocumentLine)

        self.shortMoveCursorToStartOfDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-Start-Of-Document-Line"][0], self)
        self.shortMoveCursorToStartOfDocumentLine.activated.connect(
            self.moveCursorToStartOfDocumentLine)

        self.shortExtendSelectionToStartOfDisplayLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-Start-Of-Display-Line"][0], self)
        self.shortExtendSelectionToStartOfDisplayLine.activated.connect(
            self.extendSelectionToStartOfDisplayLine)

        self.shortExtendRectangularSelectionUpOneLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-Up-One-Line"][0], self)
        self.shortExtendRectangularSelectionUpOneLine.activated.connect(
            self.extendRectangularSelectionUpOneLine)

        self.shortMoveToFirstVisibleCharacterInDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-First-Visible-Character-In-Document-Line"][0], self)
        self.shortMoveToFirstVisibleCharacterInDocumentLine.activated.connect(
            self.moveToFirstVisibleCharacterInDocumentLine)

        self.shortExtendRectangularSelectionToFirstVisibleCharacterInDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-To-First-Visible-Character-In-Document-Line"][0], self)
        self.shortExtendRectangularSelectionToFirstVisibleCharacterInDocumentLine.activated.connect(
            self.extendRectangularSelectionToFirstVisibleCharacterInDocumentLine)

        self.shortExtendRectangularSelectionToStartOfDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-To-Start-Of-Document-Line"][0], self)
        self.shortExtendRectangularSelectionToStartOfDocumentLine.activated.connect(
            self.extendRectangularSelectionToStartOfDocumentLine)

        self.shortExtendSelectionLeftOneWordPart = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Left-One-Word-Part"][0], self)
        self.shortExtendSelectionLeftOneWordPart.activated.connect(
            self.extendSelectionLeftOneWordPart)

        self.shortExtendSelectionToEndOfPreviousWord = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-End-Of-Previous-Word"][0], self)
        self.shortExtendSelectionToEndOfPreviousWord.activated.connect(
            self.extendSelectionToEndOfPreviousWord)

        self.shortExtendSelectionToStartOfDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-Start-Of-Document-Line"][0], self)
        self.shortExtendSelectionToStartOfDocumentLine.activated.connect(
            self.extendSelectionToStartOfDocumentLine)

        self.shortStutteredExtendSelectionDownOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Stuttered-Extend-Selection-Down-One-Page"][0], self)
        self.shortStutteredExtendSelectionDownOnePage.activated.connect(
            self.stutteredExtendSelectionDownOnePage)

        self.shortExtendSelectionToEndOfDisplayOrDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-End-Of-Display-Or-Document-Line"][0], self)
        self.shortExtendSelectionToEndOfDisplayOrDocumentLine.activated.connect(
            self.extendSelectionToEndOfDisplayOrDocumentLine)

        self.shortExtendRectangularSelectionToEndOfDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-To-End-Of-Document-Line"][0], self)
        self.shortExtendRectangularSelectionToEndOfDocumentLine.activated.connect(
            self.extendSelectionToEndOfDisplayOrDocumentLine)

        self.shortMoveToEndOfDisplayOrDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-End-Of-Display-Or-Document-Line"][0], self)
        self.shortMoveToEndOfDisplayOrDocumentLine.activated.connect(
            self.moveToEndOfDisplayOrDocumentLine)

        self.shortMoveToEndOfPreviousWord = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-End-Of-Previous-Word"][0], self)
        self.shortMoveToEndOfPreviousWord.activated.connect(
            self.moveToEndOfPreviousWord)

        self.shortExtendSelectionToFirstVisibleCharacterInDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-First-Visible-Character-In-Document-Line"][0], self)
        self.shortExtendSelectionToFirstVisibleCharacterInDocumentLine.activated.connect(
            self.extendSelectionToFirstVisibleCharacterInDocumentLine)

        self.shortExtendSelectionToStartOfDisplayOrDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-Start-Of-Display-Or-Document-Line"][0], self)
        self.shortExtendSelectionToStartOfDisplayOrDocumentLine.activated.connect(
            self.extendSelectionToStartOfDisplayOrDocumentLine)

        self.shortDeleteCurrentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Current-Line"][0], self)
        self.shortDeleteCurrentLine.activated.connect(
            self.deleteCurrentLine)

        self.shortExtendSelectionRightOneWordPart = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-Right-One-Word-Part"][0], self)
        self.shortExtendSelectionRightOneWordPart.activated.connect(
            self.extendSelectionRightOneWordPart)

        self.shortExtendSelectionToFirstVisibleCharacterInDisplayOrDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-First-Visible-Character-In-Display-Or-Document-Line"][0], self)
        self.shortExtendSelectionToFirstVisibleCharacterInDisplayOrDocumentLine.activated.connect(
            self.extendSelectionToFirstVisibleCharacterInDisplayOrDocumentLine)

        self.shortExtendSelectionToEndOfNextWorde = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-End-Of-Next-Word"][0], self)
        self.shortExtendSelectionToEndOfNextWorde.activated.connect(
            self.extendSelectionToEndOfNextWord)

        self.shortStutteredExtendSelectionUpOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Stuttered-Extend-Selection-Up-One-Page"][0], self)
        self.shortStutteredExtendSelectionUpOnePage.activated.connect(
            self.stutteredExtendSelectionUpOnePage)

        self.shortExtendSelectionToEndOfDisplayLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-End-Of-Display-Line"][0], self)
        self.shortExtendSelectionToEndOfDisplayLine.activated.connect(
            self.extendSelectionToEndOfDisplayLine)

        self.shortExtendSelectionToEndOfDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Selection-To-End-Of-Document-Line"][0], self)
        self.shortExtendSelectionToEndOfDocumentLine.activated.connect(
            self.extendSelectionToEndOfDocumentLine)

        self.shortExtendRectangularSelectionUpOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-Up-One-Page"][0], self)
        self.shortExtendRectangularSelectionUpOnePage.activated.connect(
            self.extendRectangularSelectionUpOnePage)

        self.shortExtendRectangularSelectionDownOnePage = QtGui.QShortcut(
            shortcuts["Editor"]["Extend-Rectangular-Selection-Down-One-Page"][0], self)
        self.shortExtendRectangularSelectionDownOnePage.activated.connect(
            self.extendRectangularSelectionDownOnePage)

        self.shortDeletePreviousCharacterIfNotAtStartOfLine = QtGui.QShortcut(
            shortcuts["Editor"]["Delete-Previous-Character-If-Not-At-Start-Of-Line"][0], self)
        self.shortDeletePreviousCharacterIfNotAtStartOfLine.activated.connect(
            self.deletePreviousCharacterIfNotAtStartOfLine)

        self.shortMoveToStartOfDisplayOrDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-Start-Of-Display-Or-Document-Line"][0], self)
        self.shortMoveToStartOfDisplayOrDocumentLine.activated.connect(
            self.moveToStartOfDisplayOrDocumentLine)

        self.shortMoveToFirstVisibleCharacterOfDisplayInDocumentLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-First-Visible-Character-Of-Display-In-Document-Line"][0], self)
        self.shortMoveToFirstVisibleCharacterOfDisplayInDocumentLine.activated.connect(
            self.moveToFirstVisibleCharacterOfDisplayInDocumentLine)

        self.shortMoveToStartOfDisplayLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-Start-Of-Display-Line"][0], self)
        self.shortMoveToStartOfDisplayLine.activated.connect(
            self.moveToStartOfDisplayLine)

        self.shortMoveToEndOfNextWord = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-End-Of-Next-Word"][0], self)
        self.shortMoveToEndOfNextWord.activated.connect(
            self.moveToEndOfNextWord)

        self.shortMoveToEndOfDisplayLine = QtGui.QShortcut(
            shortcuts["Editor"]["Move-To-End-Of-Display-Line"][0], self)
        self.shortMoveToEndOfDisplayLine.activated.connect(
            self.moveToEndOfDisplayLine)

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

    def extendSelectionToEOL(self):
        """
        Extend the selection to the end of the document line.
        """
        self.SendScintilla(QsciScintilla.SCI_LINEENDEXTEND)

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
