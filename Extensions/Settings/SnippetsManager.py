import os

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox,
    QPushButton, QSplitter, QTextEdit, QToolButton, QVBoxLayout,
)


class GetName(QDialog):

    def __init__(self, caption, path, parent=None):
        QDialog.__init__(self, parent, Qt.WindowType.Window |
                               Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        self.path = path

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(QLabel("Name:"))

        self.nameLine = QLineEdit()
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.statusLabel = QLabel()
        hbox.addWidget(self.statusLabel)

        self.statusLabel = QLabel("")
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.acceptButton = QPushButton("Ok")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        hbox.addWidget(self.cancelButton)

        self.resize(300, 20)
        self.enableAcceptButton()

        self.accepted = False

        self.exec()

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


class SnippetsManager(QDialog):

    def __init__(self, path, parent):
        QDialog.__init__(self, parent)

        self.setWindowTitle("Snippets")
        self.setAcceptDrops(True)
        self.resize(500, 300)

        self.path = path

        mainLayout = QVBoxLayout()

        self.mainSplitter = QSplitter()

        self.snippetsListWidget = QListWidget()
        self.snippetsListWidget.setSortingEnabled(True)
        self.snippetsListWidget.itemPressed.connect(self.loadSnippet)
        self.snippetsListWidget.currentItemChanged.connect(self.loadSnippet)

        self.mainSplitter.addWidget(self.snippetsListWidget)

        self.snippetViewer = QTextEdit()
        self.snippetViewer.setReadOnly(True)
        self.snippetViewer.setAcceptDrops(False)
        self.mainSplitter.addWidget(self.snippetViewer)
        self.snippetsListWidget.setAcceptDrops(False)
        self.snippetViewer.installEventFilter(self)
        self.snippetsListWidget.installEventFilter(self)
        mainLayout.addWidget(self.mainSplitter)
        self.setLayout(mainLayout)

        mainLayout.addWidget(self.mainSplitter)

        hbox = QHBoxLayout()

        self.addButton = QToolButton()
        self.addButton.setAutoRaise(True)
        self.addButton.setToolTip("Add")
        self.addButton.setIcon(QIcon(os.path.join("Resources", "images", "add")))
        self.addButton.clicked.connect(self.addSnippet)
        hbox.addWidget(self.addButton)

        self.removeButton = QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setToolTip("Remove")
        self.removeButton.setIcon(QIcon(os.path.join("Resources", "images", "minus")))
        self.removeButton.clicked.connect(self.removeSnippet)
        hbox.addWidget(self.removeButton)

        self.renameButton = QToolButton()
        self.renameButton.setAutoRaise(True)
        self.renameButton.setToolTip("Rename")
        self.renameButton.setIcon(QIcon(
            os.path.join("Resources", "images", "ui-text-field")))
        self.renameButton.clicked.connect(self.renameSnippet)
        hbox.addWidget(self.renameButton)

        hbox.addStretch(1)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.saveSnippet)
        hbox.addWidget(self.saveButton)

        mainLayout.addLayout(hbox)

        self.mainSplitter.setSizes([10, 400])

        self.mainSplitter.setCollapsible(0, False)
        self.mainSplitter.setCollapsible(1, False)

        self.loadSnippetList()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.DragEnter,
                            QEvent.Type.DragMove):
            if event.mimeData().hasText():
                event.acceptProposedAction()
                return True
        if event.type() == QEvent.Type.Drop:
            self.dropEvent(event)
            return True
        return QDialog.eventFilter(self, obj, event)

    def dropEvent(self, event):
        if event.mimeData().hasText():
            mime = event.mimeData()
            event.setDropAction(Qt.DropAction.CopyAction)
            snippet = GetName("Add Snippet", self.path, self)
            if snippet.accepted:
                with open(os.path.join(self.path, snippet.name), 'w') as file:
                    file.write(mime.text())

                self.loadSnippetList()
                found = self.snippetsListWidget.findItems(snippet.name,
                                                          Qt.MatchFlag.MatchCaseSensitive)
                item = found[0]
                self.snippetsListWidget.setCurrentItem(item)
        else:
            event.ignore()

    def addSnippet(self):
        snippet = GetName("Add Snippet", self.path, self)
        if snippet.accepted:
            with open(os.path.join(self.path, snippet.name), 'w'):
                pass

            self.loadSnippetList()
            found = self.snippetsListWidget.findItems(snippet.name,
                                                      Qt.MatchFlag.MatchCaseSensitive)
            item = found[0]
            self.snippetsListWidget.setCurrentItem(item)

    def saveSnippet(self):
        name = self.snippetsListWidget.currentItem().text()
        path = os.path.join(self.path, name)
        with open(path, 'w') as file:
            file.write(self.snippetViewer.toPlainText())

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
                                                      Qt.MatchFlag.MatchCaseSensitive)
            item = found[0]
            self.snippetsListWidget.setCurrentItem(item)

    def removeSnippet(self):
        name = self.snippetsListWidget.currentItem().text()

        mess = 'Remove "{0}" from snippets?'.format(name)
        reply = QMessageBox.warning(self, "Remove", mess,
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            os.remove(os.path.join(self.path, name))
            self.loadSnippetList()
        elif reply == QMessageBox.StandardButton.No:
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
        with open(os.path.join(self.path, key), 'r') as file:
            self.snippetViewer.setText(file.read())
