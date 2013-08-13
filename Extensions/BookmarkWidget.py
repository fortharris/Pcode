from PyQt4 import QtCore, QtGui


class BookmarkWidget(QtGui.QTreeWidget):

    def __init__(self, editorTabWidget, bottomStackSwitcher, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)

        self.markersLineList = []
        self.editorTabWidget = editorTabWidget
        self.bottomStackSwitcher = bottomStackSwitcher

        self.setColumnCount(3)
        self.setHeaderLabels(["#", "Line", "Text"])
        self.itemPressed.connect(self.locateItem)

        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 80)

        self.loadTimer = QtCore.QTimer()
        self.loadTimer.setSingleShot(True)
        self.loadTimer.setInterval(0)
        self.loadTimer.timeout.connect(self.load)

        self.editorTabWidget.currentEditorTextChanged.connect(
            self.loadTimer.start)
        self.editorTabWidget.bookmarksChanged.connect(self.loadTimer.start)

    def startTimer(self):
        self.loadTimer.start(0)

    def load(self):
        markerLines = []
        editor = self.editorTabWidget.getEditor()
        bookmarks = editor.getBookmarks()
        for line in bookmarks:
            markerLines.append((line, editor.text(line).strip()))
        if markerLines != self.markersLineList:
            self.markersLineList = markerLines
            self.clear()
            m = 1
            for i in markerLines:
                item = QtGui.QTreeWidgetItem()
                item.setText(0, str(m))
                item.setText(1, str(i[0] + 1))
                item.setToolTip(2, i[1])
                item.setText(2, i[1])
                self.addTopLevelItem(item)

                m += 1
        self.bottomStackSwitcher.setCount(self, str(len(markerLines)))

    def locateItem(self, item):
        lineNum = int(item.data(1, 0)) - 1
        self.editorTabWidget.showLine(lineNum)
