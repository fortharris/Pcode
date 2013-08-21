import os
from PyQt4 import QtCore, QtGui


class UsageDialog(QtGui.QDialog):

    def __init__(self, editorTabWidget, title, itemsList, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.resize(600, 300)

        self.editorTabWidget = editorTabWidget

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        self.view = QtGui.QTreeWidget()
        self.view.setHeaderLabels(["#"])
        self.view.setColumnWidth(0, 300)
        self.view.setSortingEnabled(True)
        self.view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.view.itemActivated.connect(self.showLine)
        mainLayout.addWidget(self.view)

        for item in itemsList:
            self.view.addTopLevelItem(item)

        self.exec_()

    def showLine(self, item):
        if item.parent() is None:
            return
        path = item.parent().text(0)
        fullPath = os.path.join(
            self.editorTabWidget.pathDict["sourcedir"], path)
        self.editorTabWidget.loadfile(fullPath)
        line = int(item.text(0)) - 1
        self.editorTabWidget.showLine(line)
