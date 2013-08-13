
from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla

from Extensions.BaseScintilla import BaseScintilla
from Extensions import StyleSheet


class CodeSnapshot(BaseScintilla):

    def __init__(self, colorScheme, parent=None):
        BaseScintilla.__init__(self, parent)

        self.colorScheme = colorScheme
        self.DATA = {"fileType": "python"}

        self.createContextMenu()
        self.setStyleSheet(StyleSheet.editorStyle)

        self.colorScheme.styleEditor(self)
        self.setMarginLineNumbers(0, True)

    def updateLexer(self, lexer):
        self.setLexer(lexer)

    def contextMenuEvent(self, event):
        state = self.hasSelectedText()
        self.copyAct.setEnabled(state)

        self.contextMenu.exec_(event.globalPos())

    def createContextMenu(self):
        self.copyAct = QtGui.QAction(
            "Copy", self,
            statusTip="Copy selected text", triggered=self.copy)

        self.selectAllAct = QtGui.QAction("Select All", self,
                                          statusTip="Select All",
                                          triggered=self.selectAllText)

        self.selectToMatchingBraceAct = \
            QtGui.QAction(QtGui.QIcon("Resources\\images\\compose"),
                          "Select to Matching Brace", self,
                          statusTip="Select to Matching Brace",
                          triggered=self.selectToMatchingBrace)

        self.contextMenu = QtGui.QMenu()
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.copyAct)
        self.contextMenu.addAction(self.selectAllAct)
        self.contextMenu.addAction(self.selectToMatchingBraceAct)

    def selectAllText(self):
        self.selectAll()
