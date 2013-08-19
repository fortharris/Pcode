from PyQt4 import QtCore, QtGui
import os.path


class SearchWidget(QtGui.QLabel):

    def __init__(self, useData, editorTabWidget, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.useData = useData
        self.editorTabWidget = editorTabWidget

        self.mainLayout = QtGui.QVBoxLayout()
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
        self.textFinderWidget = QtGui.QWidget()

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(0)
        hbox.addWidget(QtGui.QLabel("Find:"))

        self.findLine = QtGui.QLineEdit()
        self.findLine.textEdited.connect(self.find)
        self.previousWordLength = 0
        hbox.addWidget(self.findLine)

        self.findDownButton = QtGui.QToolButton()
        self.findDownButton.setAutoRaise(True)
        self.findDownButton.setIconSize(QtCore.QSize(20, 20))
        self.findDownButton.setDefaultAction(
            QtGui.QAction(QtGui.QIcon(os.path.join("Resources","images","findDown")),
                          "Find Next", self, triggered=self.findNext))
        hbox.addWidget(self.findDownButton)

        self.findUpButton = QtGui.QToolButton()
        self.findUpButton.setAutoRaise(True)
        self.findUpButton.setIconSize(QtCore.QSize(20, 20))
        self.findUpButton.setDefaultAction(
            QtGui.QAction(QtGui.QIcon(os.path.join("Resources","images","findUp")),
                          "Find Previous", self,
                          triggered=self.findPrevious))
        hbox.addWidget(self.findUpButton)

        self.matchCaseBox = QtGui.QCheckBox("MC")
        self.matchCaseBox.setToolTip("Match Case")
        self.matchCaseBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.matchCaseBox)

        self.matchWholeWordBox = QtGui.QCheckBox("WW")
        self.matchWholeWordBox.setToolTip("Whole Word")
        self.matchWholeWordBox.stateChanged.connect(
            self.updateFindOptions)
        hbox.addWidget(self.matchWholeWordBox)

        self.matchRegExpBox = QtGui.QCheckBox("RE")
        self.matchRegExpBox.setToolTip("Regular Expression")
        self.matchRegExpBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.matchRegExpBox)

        self.wrapAroundBox = QtGui.QCheckBox("WA")
        self.wrapAroundBox.setToolTip("Wrap Around")
        self.wrapAroundBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.wrapAroundBox)

        hbox.addStretch(1)

        self.hideFindWidgetButton = QtGui.QToolButton()
        self.hideFindWidgetButton.setAutoRaise(True)
        self.hideFindWidgetButton.setIcon(
            QtGui.QIcon(os.path.join("Resources","images","exit")))
        self.hideFindWidgetButton.clicked.connect(self.hideFindWidget)
        hbox.addWidget(self.hideFindWidgetButton)

        self.textFinderWidget.setLayout(hbox)
        hbox.setStretch(1, 1)
        self.mainLayout.addWidget(self.textFinderWidget)

    def createReplaceWidget(self):
        self.replacerWidget = QtGui.QWidget()

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(0)
        hbox.addStretch(1)

        label = QtGui.QLabel("Replace with:")
        hbox.addWidget(label)

        self.replaceLine = QtGui.QLineEdit()
        hbox.addWidget(self.replaceLine)

        self.replaceButton = QtGui.QPushButton("Replace")
        self.replaceButton.clicked.connect(self.replace)
        hbox.addWidget(self.replaceButton)

        self.replaceAllButton = QtGui.QPushButton("Replace All")
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
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
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
            if self.useData.SETTINGS['DynamicSearch'] == 'True':
                editor.setCursorPosition(0, 0)
                editor.clearAllIndicators(editor.searchIndicator)
                found = editor.findFirst(text, self.matchRegExp,
                                         self.matchCase, self.matchWholeWord, self.wrapAround, True, -1, -1, True)
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
            editor.findFirst(text, self.matchRegExp,
                             self.matchCase, self.matchWholeWord, self.wrapAround,
                             True, -1, -1, True)

    def findPrevious(self):
        text = self.findLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if text == '':
            pass
        else:
            editor.findFirst(text, self.matchRegExp,
                             self.matchCase, self.matchWholeWord,
                             self.wrapAround, False, -1, -1, True)
            editor.findNext()

    def replace(self):
        # FIXME Text replace only works after finding next
        # not after finding previous
        text = self.findLine.text()
        replaceText = self.replaceLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if editor.hasSelectedText() == True:
            pass
        else:
            editor.findFirst(text, self.matchRegExp,
                             self.matchCase, self.matchWholeWord, self.wrapAround,
                             True, -1, -1, True)
        editor.replace(replaceText)
        found = editor.findFirst(text, self.matchRegExp,
                                 self.matchCase, self.matchWholeWord, self.wrapAround,
                                 True, -1, -1, True)

    def replaceAll(self):
        text = self.findLine.text()
        replaceText = self.replaceLine.text()
        editor = self.editorTabWidget.focusedEditor()
        editor.setCursorPosition(0, 0)
        find = editor.findFirst(text,
                                self.matchRegExp,
                                self.matchCase, self.matchWholeWord, self.wrapAround,
                                True, 1, 1, True)
        editor.beginUndoAction()
        while find == True:
            editor.replace(replaceText)
            find = editor.findNext()
        editor.endUndoAction()
