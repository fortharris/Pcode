from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QCheckBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMenu, QMessageBox, QPushButton, QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

import os
import ctypes
import re

from Extensions import Global
from Extensions.Diff import DiffWindow


class FinderThread(QtCore.QThread):

    listItemAvailable = pyqtSignal()
    currentDir = pyqtSignal(str)

    def run(self):
        for dirname, _, files in os.walk(self.directory):
            self.currentDir.emit(dirname)
            if self.stop:
                break
            for f in files:
                if self.stop:
                    break
                if re.match(self.filterRe, f):
                    file = os.path.join(dirname, f)
                    parentItem = QTreeWidgetItem()
                    # read the file and split it into textlines
                    try:
                        with open(file, 'r') as fh:
                            text = fh.read()
                        lines = text.splitlines(True)
                    except Exception:
                        continue

                    # now perform the search and display the lines found
                    count = 0
                    for line in lines:
                        if self.stop:
                            break

                        count += 1
                        contains = self.search.search(line)
                        if contains:
                            start = contains.start()
                            end = contains.end()
                            line = line.replace("\r", "").replace("\n", "")
                            childItem = self.createChild(
                                str(count), line, (start, end))
                            parentItem.addChild(childItem)
                    if parentItem.childCount() > 0:
                        parentItem.setText(0, file)
                        parentItem.setForeground(0, QBrush(
                            QColor("#003366")))
                        self.found.append(parentItem)
                        self.listItemAvailable.emit()
            if self.recursive is False:
                return

    def find(self, directory, filterRe, search, recursive):
        self.directory = directory
        self.filterRe = filterRe
        self.search = search
        self.recursive = recursive

        self.stop = False
        self.found = []

        self.start()

    def createChild(self, line, text, pos):
        childItem = QTreeWidgetItem()
        childItem.setText(0, line)
        childItem.setText(1, text)
        childItem.setToolTip(1, text)
        childItem.setData(0, 3, pos)

        return childItem

    def stopThread(self):
        self.stop = True


class ConfirmReplaceDialog(QDialog):

    def __init__(self, path, text, replaceText, search, parent=None):
        QDialog.__init__(
            self, parent,
            QtCore.Qt.WindowType.Window
            | QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(path)
        self.resize(700, 400)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 5)
        self.setLayout(mainLayout)

        diff = DiffWindow()

        self.path = path
        self.text = text
        self.replaceText = replaceText
        self.search = search

        with open(path, 'r') as fh:
            content = fh.read()
        a = content.splitlines()
        b = content.splitlines()
        for i in range(len(b)):
            b[i] = search.sub(replaceText, b[i])

        diffExists = diff.generateUnifiedDiff(a, b)

        if diffExists:
            mainLayout.addWidget(diff)
        else:
            QMessageBox.information(
                self, "Replace", "There is nothing to replace.")
            return

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        mainLayout.addLayout(hbox)

        self.replaceButton = QPushButton("Replace")
        self.replaceButton.clicked.connect(self.replace)
        hbox.addWidget(self.replaceButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.pressed.connect(self.close)
        hbox.addWidget(self.cancelButton)

        hbox.addStretch(1)

        self.replaced = False
        self.exec()

    def replace(self):
        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)

        with open(self.path, 'r') as file:
            new = self.search.sub(self.replaceText, file.read())

        with open(self.path, 'w') as file:
            file.write(new)

        QApplication.restoreOverrideCursor()

        self.replaced = True
        self.close()


class FoundFilesView(QTreeWidget):

    def __init__(self, parent):
        QTreeWidget.__init__(self, parent)

        self.setHeaderHidden(True)
        self.setColumnCount(2)
        self.itemSelectionChanged.connect(self.updateActions)

        self.parent = parent
        self.createActions()

        self.updateActions()

    def updateActions(self):
        state = (len(self.selectedItems()) != 0)
        self.viewAct.setEnabled(state)
        self.locateAct.setEnabled(state)

    def contextMenuEvent(self, event):
        selected = self.selectedItems()
        if len(selected) == 0:
            pass
        else:
            item = selected[0]
            if item.parent() is None:
                self.viewAct.setEnabled(False)
        self.contextMenu.exec(event.globalPos())

    def createActions(self):
        self.viewAct = QAction(
            "View", self, statusTip="View", triggered=self.parent.viewFile)

        self.locateAct = \
            QAction(
                "Open Containing Folder", self, statusTip="Open Containing Folder", triggered=self.parent.locateFile)

        self.contextMenu = QMenu()
        self.contextMenu.addAction(self.viewAct)
        self.contextMenu.addAction(self.locateAct)


class FindInFiles(QWidget):

    def __init__(self, useData, editorTabWidget, projectPathDict, bottomStackSwitcher):
        super(FindInFiles, self).__init__()

        self.useData = useData
        self.projectPathDict = projectPathDict
        self.findThread = FinderThread()
        self.editorTabWidget = editorTabWidget
        self.bottomStackSwitcher = bottomStackSwitcher
        self._explorer_shortcuts = []

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.statusWidget = QWidget()
        self.statusWidget.setMaximumHeight(25)
        mainLayout.addWidget(self.statusWidget)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 5, 0, 0)
        self.statusWidget.setLayout(hbox)

        label = QLabel()
        label.setMaximumWidth(25)
        label.setMaximumHeight(25)
        label.setScaledContents(True)
        label.setPixmap(
            QPixmap(os.path.join("Resources", "images", "cascade")))
        hbox.addWidget(label)

        self.dirLabel = QLabel()
        hbox.addWidget(self.dirLabel)

        self.statusWidget.hide()

        self.filesView = FoundFilesView(self)
        self.filesView.activated.connect(self.viewFile)
        mainLayout.addWidget(self.filesView)

        # create finder controls

        self.dashboard = QWidget()

        vbox = QVBoxLayout()
        self.dashboard.setLayout(vbox)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        label = QLabel("Find:        ")  # extra space is for alignment
        label.setMinimumWidth(30)

        hbox.addWidget(label)

        self.findtextLine = QLineEdit()
        hbox.addWidget(self.findtextLine)

        self.replaceLabel = QLabel("Replace With:")
        hbox.addWidget(self.replaceLabel)

        self.replaceLine = QLineEdit()
        hbox.addWidget(self.replaceLine)

        hbox.setStretch(1, 1)
        hbox.setStretch(3, 1)

        hbox.addWidget(QLabel("Extensions (*.ext; ...)"))

        self.filterEdit = QLineEdit()
        self.filterEdit.setText('*')
        self.filterEdit.setMaximumWidth(72)
        hbox.addWidget(self.filterEdit)

        hbox = QHBoxLayout()

        hbox.addWidget(QLabel("Directory:"))

        self.directoryLine = QLineEdit()
        hbox.addWidget(self.directoryLine)

        hbox.setStretch(1, 1)

        self.projectBox = QCheckBox(
            "Project  ")  # extra space is for alignment
        self.projectBox.toggled.connect(self.projectBoxToggled)
        hbox.addWidget(self.projectBox)

        self.browseButton = QPushButton('...')
        self.browseButton.clicked.connect(self.setPath)
        hbox.addWidget(self.browseButton)

        self.stopButton = QPushButton("Stop")
        self.stopButton.setIcon(
            QIcon(os.path.join("Resources", "images", "stop")))
        self.stopButton.clicked.connect(self.stopFinder)
        self.stopButton.hide()
        hbox.addWidget(self.stopButton)

        self.findButton = QPushButton("Find")
        self.findButton.clicked.connect(self.find)
        hbox.addWidget(self.findButton)

        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        self.matchCaseBox = QCheckBox("MC")
        self.matchCaseBox.setToolTip("Match Case")
        self.matchCaseBox.stateChanged.connect(self.searchOptionsChanged)
        hbox.addWidget(self.matchCaseBox)

        self.matchWholeWordBox = QCheckBox("WW")
        self.matchWholeWordBox.setToolTip("Whole Word")
        self.matchWholeWordBox.stateChanged.connect(self.searchOptionsChanged)
        hbox.addWidget(self.matchWholeWordBox)

        self.regExpBox = QCheckBox("RE")
        self.regExpBox.setToolTip("Regular Expression")
        self.regExpBox.stateChanged.connect(self.searchOptionsChanged)
        hbox.addWidget(self.regExpBox)

        self.recursiveBox = QCheckBox("Recursive")
        self.recursiveBox.setChecked(True)
        self.recursiveBox.stateChanged.connect(self.searchOptionsChanged)
        hbox.addWidget(self.recursiveBox)

        self.replaceBox = QCheckBox("Replace")
        self.replaceBox.stateChanged.connect(self.toggleReplace)
        hbox.addWidget(self.replaceBox)

        hbox.addStretch(1)

        self.hideButton = QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "exit")))
        self.hideButton.clicked.connect(self.dashboard.hide)
        hbox.addWidget(self.hideButton)

        self.searchOptionsChanged()

        self.findtextLine.setFocus()

        self.findThread.listItemAvailable.connect(self.updateFilesTable)
        self.findThread.currentDir.connect(self.displayCurrentSearchDir)
        self.findThread.started.connect(self.searchStarted)
        self.findThread.finished.connect(self.searchEnded)

        self.toggleReplace(False)

    def manageSplitter(self):
        count = self.viewTab.count()
        if count == 0:
            self.splitter.widget(1).hide()
        else:
            self.splitter.widget(1).show()

    def viewFile(self, item):
        item = self.filesView.selectedItems()[0]
        if item.parent() is None:
            return
        path = item.parent().text(0)
        if self.replaceBox.isChecked():
            os.path.basename(
                path) + " ( '" + self.text + "' --> '" + self.replaceLine.text() + "' )"
            replaced = ConfirmReplaceDialog(
                path, self.text, self.replaceLine.text(), self.search, self)
            if replaced.replaced:
                if self.editorTabWidget.alreadyOpened(path):
                    QMessageBox.information(
                        self, "Reload", "This file has changed on disk. You may want to reload it.")
        else:
            line = int(item.text(0)) - 1
            pos = item.data(0, 3)
            if not self.editorTabWidget.loadfile(path):
                return
            editor = self.editorTabWidget.getEditor()
            editor.setSelection(line, pos[0], line, pos[1])

    def locateFile(self):
        item = self.filesView.selectedItems()[0]
        if item.parent() is None:
            path = item.text(0)
        else:
            path = item.parent().text(0)
        path = os.path.normpath(path)
        ctypes.windll.shell32.ShellExecuteW(None, 'open', 'explorer.exe',
                                            '/n,/select, ' + path, None, 1)

    def setPath(self):
        options = (QFileDialog.Option.DontResolveSymlinks
                   | QFileDialog.Option.ShowDirsOnly)
        directory = QFileDialog.getExistingDirectory(self,
                                                           "Select Folder", self.useData.getLastOpenedDir(), options)
        if directory:
            directory = os.path.normpath(directory)
            self.useData.saveLastOpenedDir(directory)
            self.directoryLine.setText(directory)

    def updateShortcutsList(self, shortcuts):
        self._explorer_shortcuts = list(shortcuts or [])
        if self._explorer_shortcuts:
            self.directoryLine.setText(self._explorer_shortcuts[0])

    def projectBoxToggled(self, state):
        self.directoryLine.setDisabled(state)
        self.browseButton.setDisabled(state)

    def displayCurrentSearchDir(self, dir):
        self.dirLabel.setText(dir)

    def searchOptionsChanged(self):
        self.matchCase = self.matchCaseBox.isChecked()
        self.matchWholeWord = self.matchWholeWordBox.isChecked()
        self.regExp = self.regExpBox.isChecked()
        self.recursive = self.recursiveBox.isChecked()

    def toggleReplace(self, state):
        self.replaceLine.setVisible(state)
        self.replaceLabel.setVisible(state)

    def find(self):
        self.text = self.findtextLine.text()
        if self.regExp:
            text = self.text
        else:
            text = re.escape(self.text)
        if self.matchWholeWord:
            text = "\\b{0}\\b".format(text)
        flags = re.UNICODE
        if not self.matchCase:
            flags |= re.IGNORECASE
        try:
            self.search = re.compile(text, flags)
        except re.error as err:
            QMessageBox.warning(self, "Find-in-Files",
                                                "Wrong regular expression: {0}!".format(str(err).capitalize()))
            return
        fileFilter = self.filterEdit.text()
        fileFilterList = \
            [r"^{0}$".format(filter.replace(".", r"\.").replace("*", ".*"))
             for filter in fileFilter.split(";")]
        filterRe = re.compile("|".join(fileFilterList))
        if self.projectBox.isChecked():
            dirName = self.projectPathDict["sourcedir"]
        else:
            dirName = self.directoryLine.text().strip()
            if dirName == '':
                QMessageBox.warning(self, "Find-in-Files",
                                                    "Please specify a directory!")
                return
        if not os.path.exists(dirName):
            QMessageBox.warning(self, "Find-in-Files",
                                                "Path does not exist!")
        if not os.path.isdir(dirName):
            QMessageBox.warning(self, "Find-in-Files",
                                                "Path is not a directory!")
            return
        else:
            self.filesView.clear()
            self.findThread.find(
                dirName, filterRe, self.search, self.recursive)
        self.bottomStackSwitcher.setCurrentWidget(self)

    def updateFilesTable(self):
        self.stopButton.setHidden(True)
        while len(self.findThread.found) != 0:
            item = self.findThread.found.pop(0)
            icon = Global.iconFromPath(item.text(0))
            item.setIcon(0, icon)
            self.filesView.addTopLevelItem(item)
            item.setFirstColumnSpanned(True)
            item.setExpanded(True)
        self.stopButton.setHidden(False)

    def searchStarted(self):
        self.findButton.setDisabled(True)
        self.findButton.hide()
        self.stopButton.show()
        self.statusWidget.show()

    def searchEnded(self):
        self.findButton.setDisabled(False)
        self.stopButton.hide()
        self.findButton.show()
        self.dirLabel.clear()
        self.statusWidget.hide()

    def stopFinder(self):
        self.findThread.stopThread()
