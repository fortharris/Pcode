import os
from PyQt4 import QtCore, QtGui


class GetName(QtGui.QDialog):

    def __init__(self, caption, path, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        self.path = path

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(QtGui.QLabel("Name:"))

        self.nameLine = QtGui.QLineEdit()
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.statusLabel = QtGui.QLabel()
        hbox.addWidget(self.statusLabel)

        self.statusLabel = QtGui.QLabel("")
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.acceptButton = QtGui.QPushButton("Ok")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        hbox.addWidget(self.cancelButton)

        self.resize(300, 20)
        self.enableAcceptButton()

        self.accepted = False

        self.exec_()

    def enableAcceptButton(self):
        text = self.nameLine.text().strip()
        if text == '':
            self.acceptButton.setDisabled(True)
        else:
            preExistNames = os.listdir(self.path)
            if text in preExistNames:
                self.statusLabel.setText("Unavailable")
                self.acceptButton.setDisabled(True)
            else:
                self.statusLabel.setText("Available")
                self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.name = self.nameLine.text().strip()
        self.close()


class SnippetsManager(QtGui.QDialog):

    def __init__(self, path, parent):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Snippets")
        self.setAcceptDrops(True)
        self.resize(500, 300)

        self.path = path

        mainLayout = QtGui.QVBoxLayout()

        self.mainSplitter = QtGui.QSplitter()

        self.snippetsListWidget = QtGui.QListWidget()
        self.snippetsListWidget.setSortingEnabled(True)
        self.snippetsListWidget.itemPressed.connect(self.loadSnippet)
        self.snippetsListWidget.currentItemChanged.connect(self.loadSnippet)

        self.mainSplitter.addWidget(self.snippetsListWidget)

        self.snippetViewer = QtGui.QTextEdit()
        self.snippetViewer.setReadOnly(True)
        self.mainSplitter.addWidget(self.snippetViewer)
        mainLayout.addWidget(self.mainSplitter)
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.mainSplitter)

        hbox = QtGui.QHBoxLayout()

        self.addButton = QtGui.QToolButton()
        self.addButton.setAutoRaise(True)
        self.addButton.setToolTip("Add")
        self.addButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "add")))
        self.addButton.clicked.connect(self.addSnippet)
        hbox.addWidget(self.addButton)

        self.removeButton = QtGui.QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setToolTip("Remove")
        self.removeButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "minus")))
        self.removeButton.clicked.connect(self.removeSnippet)
        hbox.addWidget(self.removeButton)

        self.renameButton = QtGui.QToolButton()
        self.renameButton.setAutoRaise(True)
        self.renameButton.setToolTip("Rename")
        self.renameButton.setIcon(QtGui.QIcon(
            os.path.join("Resources", "images", "ui-text-field")))
        self.renameButton.clicked.connect(self.renameSnippet)
        hbox.addWidget(self.renameButton)

        hbox.addStretch(1)

        self.saveButton = QtGui.QPushButton("Save")
        self.saveButton.clicked.connect(self.saveSnippet)
        hbox.addWidget(self.saveButton)

        mainLayout.addLayout(hbox)

        self.mainSplitter.setSizes([10, 400])

        self.mainSplitter.setCollapsible(0, False)
        self.mainSplitter.setCollapsible(1, False)

        self.loadSnippetList()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.CopyAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        # FIXME: Dragging only works when dropped anywhere else but the editor.
        # Have to find a way to get the editor to accept drop actions that
        # have to do with text
        if event.mimeData().hasText():
            mime = event.mimeData()
            event.setDropAction(QtCore.Qt.CopyAction)
            snippet = GetName("Add Snippet", self.path, self)
            if snippet.accepted:
                file = open(os.path.join(self.path, snippet.name), 'w')
                file.write(mime.text())
                file.close()

                self.loadSnippetList()
                found = self.snippetsListWidget.findItems(snippet.name,
                                                          QtCore.Qt.MatchCaseSensitive)
                item = found[0]
                self.snippetsListWidget.setCurrentItem(item)
        else:
            event.ignore()

    def addSnippet(self):
        snippet = GetName("Add Snippet", self.path, self)
        if snippet.accepted:
            file = open(os.path.join(self.path, snippet.name), 'w')
            file.close()

            self.loadSnippetList()
            found = self.snippetsListWidget.findItems(snippet.name,
                                                      QtCore.Qt.MatchCaseSensitive)
            item = found[0]
            self.snippetsListWidget.setCurrentItem(item)

    def saveSnippet(self):
        name = self.snippetsListWidget.currentItem().text()
        path = os.path.join(self.path, name)
        file = open(path, 'w')
        file.write(self.snippetViewer.toPlainText())
        file.close()

    def renameSnippet(self):
        snippet = GetName("Rename Snippet", self.path, self)
        if snippet.accepted:
            old_name = self.snippetsListWidget.currentItem().text()
            new_name = snippet.name
            old_path = os.path.join(self.path, old_name)
            new_path = os.path.join(self.path, new_name)
            os.rename(old_path, new_path)

            self.loadSnippetList()
            found = self.snippetsListWidget.findItems(new_name,
                                                      QtCore.Qt.MatchCaseSensitive)
            item = found[0]
            self.snippetsListWidget.setCurrentItem(item)

    def removeSnippet(self):
        name = self.snippetsListWidget.currentItem().text()

        mess = 'Remove "{0}" from snippets?'.format(name)
        reply = QtGui.QMessageBox.warning(self, "Remove", mess,
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            os.remove(os.path.join(self.path, name))
            self.loadSnippetList()
        elif reply == QtGui.QMessageBox.No:
            pass

    def loadSnippetList(self):
        self.snippetViewer.clear()
        self.snippetsListWidget.clear()
        for i in os.listdir(self.path):
            self.snippetsListWidget.addItem(i)
        if self.snippetsListWidget.count() == 0:
            self.snippetViewer.setReadOnly(True)
            self.removeButton.setDisabled(True)
        else:
            self.snippetViewer.setReadOnly(False)
            self.removeButton.setDisabled(False)
            self.snippetsListWidget.setCurrentRow(0)

    def loadSnippet(self):
        if self.snippetsListWidget.count() == 0:
            return
        currentItem = self.snippetsListWidget.currentItem()
        if currentItem is None:
            return
        key = currentItem.text()
        file = open(os.path.join(self.path, key), 'r')
        self.snippetViewer.setText(file.read())
        file.close()
