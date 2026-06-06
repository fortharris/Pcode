import os

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QToolButton,
    QVBoxLayout, QWidget,
)


class SearchWidget(QLabel):

    def __init__(self, useData, editorTabWidget, parent=None):
        QLabel.__init__(self, parent)

        self.useData = useData
        self.editorTabWidget = editorTabWidget

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(5, 0, 0, 0)

        self.createFindWidget()
        self.createReplaceWidget()

        self.setLayout(self.mainLayout)

        self.matchCase = False
        self.matchWholeWord = False
        self.matchRegExp = False
        self.wrapAround = False

        self.hide()

    def createFindWidget(self):
        self.textFinderWidget = QWidget()

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(QLabel("Find:"))

        self.findLine = QLineEdit()
        self.findLine.textEdited.connect(self.find)
        self.previousWordLength = 0
        hbox.addWidget(self.findLine)

        self.findDownButton = QToolButton()
        self.findDownButton.setAutoRaise(True)
        self.findDownButton.setIconSize(QSize(20, 20))
        self.findDownButton.setDefaultAction(
            QAction(
                QIcon(os.path.join("Resources", "images", "findDown")),
                "Find Next", self, triggered=self.findNext))
        hbox.addWidget(self.findDownButton)

        self.findUpButton = QToolButton()
        self.findUpButton.setAutoRaise(True)
        self.findUpButton.setIconSize(QSize(20, 20))
        self.findUpButton.setDefaultAction(
            QAction(
                QIcon(os.path.join("Resources", "images", "findUp")),
                "Find Previous", self, triggered=self.findPrevious))
        hbox.addWidget(self.findUpButton)

        self.matchCaseBox = QCheckBox("MC")
        self.matchCaseBox.setToolTip("Match Case")
        self.matchCaseBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.matchCaseBox)

        self.matchWholeWordBox = QCheckBox("WW")
        self.matchWholeWordBox.setToolTip("Whole Word")
        self.matchWholeWordBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.matchWholeWordBox)

        self.matchRegExpBox = QCheckBox("RE")
        self.matchRegExpBox.setToolTip("Regular Expression")
        self.matchRegExpBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.matchRegExpBox)

        self.wrapAroundBox = QCheckBox("WA")
        self.wrapAroundBox.setToolTip("Wrap Around")
        self.wrapAroundBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.wrapAroundBox)

        hbox.addStretch(1)

        self.hideFindWidgetButton = QToolButton()
        self.hideFindWidgetButton.setAutoRaise(True)
        self.hideFindWidgetButton.setIcon(
            QIcon(os.path.join("Resources", "images", "exit")))
        self.hideFindWidgetButton.clicked.connect(self.hideFindWidget)
        hbox.addWidget(self.hideFindWidgetButton)

        self.textFinderWidget.setLayout(hbox)
        hbox.setStretch(1, 1)
        self.mainLayout.addWidget(self.textFinderWidget)

    def createReplaceWidget(self):
        self.replacerWidget = QWidget()

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addStretch(1)

        label = QLabel("Replace with:")
        hbox.addWidget(label)

        self.replaceLine = QLineEdit()
        hbox.addWidget(self.replaceLine)

        self.replaceButton = QPushButton("Replace")
        self.replaceButton.clicked.connect(self.replace)
        hbox.addWidget(self.replaceButton)

        self.replaceAllButton = QPushButton("Replace All")
        self.replaceAllButton.clicked.connect(self.replaceAll)
        hbox.addWidget(self.replaceAllButton)

        hbox.addStretch(1)

        self.replacerWidget.setLayout(hbox)
        hbox.setStretch(2, 1)
        self.mainLayout.addWidget(self.replacerWidget)

    def showFinder(self):
        self.mainLayout.setContentsMargins(5, 0, 5, 0)
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        self.replacerWidget.hide()

        self.show()
        self.fixTextAtCursor()
        self.textFinderWidget.show()
        self.findLine.selectAll()
        self.findLine.setFocus()

    def fixTextAtCursor(self):
        editor = self.editorTabWidget.focusedEditor()
        self.findLine.selectAll()
        if editor.hasSelectedText():
            selection = editor.selectedText()
            self.findLine.insert(selection)

    def showReplaceWidget(self):
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.setMinimumHeight(70)
        self.setMaximumHeight(70)
        self.findLine.setText(self.editorTabWidget.get_current_word())
        self.show()
        self.fixTextAtCursor()
        self.replacerWidget.show()
        self.findLine.selectAll()
        self.findLine.setFocus()

    def hideFindWidget(self):
        self.hide()

    def updateFindOptions(self):
        self.matchCase = self.matchCaseBox.isChecked()
        self.matchWholeWord = self.matchWholeWordBox.isChecked()
        self.matchRegExp = self.matchRegExpBox.isChecked()
        self.wrapAround = self.wrapAroundBox.isChecked()

        self.find()

    def find(self):
        text = self.findLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if text == '':
            self.findLine.setStyleSheet(
                "QLineEdit {border-bottom: 1px solid lightgrey;}")
            editor.clearAllIndicators(editor.searchIndicator)
        else:
            if self.useData.setting_bool('DynamicSearch'):
                editor.clearAllIndicators(editor.searchIndicator)
                found = editor.findFirst(
                    text, self.matchRegExp, self.matchCase, self.matchWholeWord,
                    self.wrapAround, True, 0, 0, True)
                if found:
                    self.findLine.setStyleSheet(
                        "QLineEdit {border-bottom: 1px solid lightgrey;}")
                else:
                    self.findLine.setStyleSheet(
                        "QLineEdit {border-bottom: 2px solid #FF6666;}")

    def findNext(self):
        text = self.findLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if text == '':
            pass
        else:
            editor.findFirst(
                text, self.matchRegExp, self.matchCase, self.matchWholeWord,
                self.wrapAround, True, -1, -1, True)

    def findPrevious(self):
        text = self.findLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if text == '':
            pass
        else:
            editor.findFirst(
                text, self.matchRegExp, self.matchCase, self.matchWholeWord,
                self.wrapAround, False, -1, -1, True)
            editor.findNext()

    def replace(self):
        text = self.findLine.text()
        replaceText = self.replaceLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if not editor.hasSelectedText():
            editor.setCursorPosition(editor.getCursorPosition()[0],
                                     editor.getCursorPosition()[1])
            editor.findFirst(
                text, self.matchRegExp, self.matchCase, self.matchWholeWord,
                self.wrapAround, True, -1, -1, True)
        editor.replace(replaceText)
        editor.findFirst(
            text, self.matchRegExp, self.matchCase, self.matchWholeWord,
            self.wrapAround, True, -1, -1, True)

    def replaceAll(self):
        text = self.findLine.text()
        replaceText = self.replaceLine.text()
        editor = self.editorTabWidget.focusedEditor()
        editor.setCursorPosition(0, 0)
        find = editor.findFirst(
            text, self.matchRegExp, self.matchCase, self.matchWholeWord,
            self.wrapAround, True, 1, 1, True)
        editor.beginUndoAction()
        while find:
            editor.replace(replaceText)
            find = editor.findNext()
        editor.endUndoAction()
