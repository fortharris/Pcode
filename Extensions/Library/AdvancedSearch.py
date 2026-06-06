import os
import re

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QProgressBar, QPushButton, QVBoxLayout, QWidget,
)
from PyQt6.QtXml import QDomDocument


class FinderThread(QThread):

    searchSoFar = pyqtSignal(int)

    def find(self, text, matchCase, matchWholeWord, regExp, searchLoc, libraryDir):
        self.text = text
        self.cs = matchCase
        self.wo = matchWholeWord
        self.reg = regExp
        self.searchLoc = searchLoc
        self.libraryDir = libraryDir

        self.stop = False
        self.found = []

        self.start()

    def run(self):
        self.found = []
        if self.reg:
            txt = self.text
        else:
            txt = re.escape(self.text)
        if self.wo:
            txt = "\\b{0}\\b".format(txt)
        flags = re.UNICODE
        if not self.cs:
            flags |= re.IGNORECASE
        try:
            search = re.compile(txt, flags)
        except re.error as why:
            print(why)

        files = os.listdir(self.libraryDir)
        dom_document = QDomDocument()
        for i in range(len(files)):
            if self.stop:
                break
            file = os.path.abspath(os.path.join(self.libraryDir, files[i]))

            try:
                with open(file, 'r') as fh:
                    text = fh.read()
            except Exception:
                continue
            dom_document.setContent(text)

            documentElement = dom_document.documentElement()
            childElement = documentElement.firstChild().toElement()
            while childElement.isNull() is False:
                if childElement.nodeName() == 'comments':
                    if (self.searchLoc == 0) or (self.searchLoc == 2):
                        comments = childElement.firstChild().nodeValue()
                        contains = search.search(comments)
                        if contains:
                            self.found.append(files[i])
                elif childElement.nodeName() == 'code':
                    if (self.searchLoc == 0) or (self.searchLoc == 1):
                        code = childElement.firstChild().nodeValue()
                        contains = search.search(code)
                        if contains:
                            if files[i] not in self.found:
                                self.found.append(files[i])
                childElement = childElement.nextSibling()
            self.searchSoFar.emit(i)

    def stopFind(self):
        self.stop = True


class AdvancedSearch(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent, Qt.WindowType.Window |
                               Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("Advanced Search")
        self.resize(400, 120)

        self.library = parent
        self.finderThread = FinderThread()

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.searchResultsListWidget = QListWidget()
        self.searchResultsListWidget.itemPressed.connect(
            self.library.viewSearchItem)
        self.searchResultsListWidget.itemActivated.connect(
            self.library.viewSearchItem)
        mainLayout.addWidget(self.searchResultsListWidget)

        mainLayout.addWidget(QLabel("Find:"))

        self.searchLine = QLineEdit()
        self.searchLine.returnPressed.connect(self.startSearch)
        mainLayout.addWidget(self.searchLine)

        mainLayout.addWidget(QLabel("Location:"))

        self.searchLocBox = QComboBox()
        self.searchLocBox.addItem("Comments AND Source Code")
        self.searchLocBox.addItem("Source Code")
        self.searchLocBox.addItem("Comments")
        mainLayout.addWidget(self.searchLocBox)

        hbox = QHBoxLayout()

        self.matchCaseBox = QCheckBox("Match Case")
        hbox.addWidget(self.matchCaseBox)

        self.matchWholeWordBox = QCheckBox("Whole Word")
        hbox.addWidget(self.matchWholeWordBox)

        self.regExpBox = QCheckBox("Regular Expression")
        hbox.addWidget(self.regExpBox)

        mainLayout.addLayout(hbox)

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.HLine)
        frame.setFrameShadow(QFrame.Shadow.Sunken)
        mainLayout.addWidget(frame)

        hbox = QHBoxLayout()

        self.searchLabel = QLabel("Searching...")
        hbox.addWidget(self.searchLabel)

        self.progressBar = QProgressBar()
        self.progressBar.setMaximumHeight(15)
        self.progressBar.setMinimumWidth(100)
        hbox.addWidget(self.progressBar)

        self.searchLabel.hide()
        self.progressBar.hide()

        self.foundLabel = QLabel()
        hbox.addWidget(self.foundLabel)
        self.foundLabel.hide()

        hbox.addStretch(1)

        searchButton = QPushButton("Search")
        searchButton.clicked.connect(self.startSearch)
        hbox.addWidget(searchButton)

        mainLayout.addLayout(hbox)

        mainLayout.setStretch(0, 1)

        self.setLayout(mainLayout)

        self.finderThread.searchSoFar.connect(self.updateProgress)
        self.finderThread.started.connect(self.searchStarted)
        self.finderThread.finished.connect(self.searchStopped)

    def startSearch(self):
        searchText = self.searchLine.text()
        self.progressBar.setMaximum(len(os.listdir(
            self.library.useData.appPathDict["librarydir"])))
        self.finderThread.find(searchText, self.matchCaseBox.isChecked(),
                               self.matchWholeWordBox.isChecked(),
                               self.regExpBox.isChecked(),
                               self.searchLocBox.currentIndex(),
                               self.library.useData.appPathDict["librarydir"])

    def searchStarted(self):
        self.foundLabel.hide()
        self.searchLabel.show()
        self.progressBar.setValue(0)
        self.progressBar.show()

    def searchStopped(self):
        self.searchLabel.hide()
        self.progressBar.hide()
        self.foundLabel.show()
        self.foundLabel.setText(str(len(self.finderThread.found)) + " found!")

        self.searchResultsListWidget.clear()
        for i in self.finderThread.found:
            self.searchResultsListWidget.addItem(QListWidgetItem(i))

    def updateProgress(self, value):
        self.progressBar.setValue(value)
