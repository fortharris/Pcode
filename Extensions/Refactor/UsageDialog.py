import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QTreeWidget, QVBoxLayout


class UsageDialog(QDialog):

    def __init__(self, editorTabWidget, title, itemsList, parent=None):
        QDialog.__init__(
            self, parent,
            Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.resize(600, 300)

        self.editorTabWidget = editorTabWidget

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.view = QTreeWidget()
        self.view.setHeaderLabels(["#"])
        self.view.setColumnWidth(0, 300)
        self.view.setSortingEnabled(True)
        self.view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.view.itemActivated.connect(self.showLine)
        mainLayout.addWidget(self.view)

        for item in itemsList:
            self.view.addTopLevelItem(item)

        self.exec()

    def showLine(self, item):
        if item.parent() is None:
            return
        path = item.parent().text(0)
        fullPath = os.path.join(
            self.editorTabWidget.projectPathDict["sourcedir"], path)
        self.editorTabWidget.loadfile(fullPath)
        line = int(item.text(0)) - 1
        self.editorTabWidget.showLine(line)
