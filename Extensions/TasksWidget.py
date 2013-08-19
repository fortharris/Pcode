import re
import os.path
from PyQt4 import QtCore, QtGui


class TaskFinderThread(QtCore.QThread):

    TASKS_PATTERN = r"(^|#)[ ]*(TODO|FIXME|XXX|HINT|TIP)( |:)([^#]*)"
    newTasks = QtCore.pyqtSignal(list)
    results = []

    def run(self):
        # TODO: this is a test for the following function
        """Find tasks in source code (TODO, FIXME, XXX, ...)"""
        results = []
        for line, text in enumerate(self.editorTabWidget.getSource().splitlines()):
            for todo in re.findall(self.TASKS_PATTERN, text):
                results.append((todo[1], line+1, todo[
                               -1].strip().capitalize()))
        if results != self.results:
            self.results = []
            self.results.extend(results)
            self.newTasks.emit(results)

    def findTasks(self, editorTabWidget):
        self.editorTabWidget = editorTabWidget
        self.start()


class Tasks(QtGui.QTreeWidget):
    def __init__(self, editorTabWidget, bottomStackSwitcher, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)

        self.setColumnCount(4)
        self.setHeaderLabels(["#", "Type", "Line", "Task"])
        self.setAutoScroll(True)

        self.setColumnWidth(0, 60)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 80)
        self.itemPressed.connect(self.taskPressed)

        self.editorTabWidget = editorTabWidget
        self.bottomStackSwitcher = bottomStackSwitcher
        self.taskFinder = TaskFinderThread()

        self.taskFinderTimer = QtCore.QTimer()
        self.taskFinderTimer.setSingleShot(True)
        self.taskFinderTimer.timeout.connect(self.findTasks)

        self.editorTabWidget.currentEditorTextChanged.connect(self.startTimer)
        self.editorTabWidget.currentChanged.connect(self.startTimer)
        self.taskFinder.newTasks.connect(self.updateTasks)

        self.setStyleSheet("""
                    QTreeView {
                         show-decoration-selected: 1; /* make the selection span the entire width of the view */
                         border: none;
                    }
                    """ )

    def startTimer(self):
        self.taskFinderTimer.start(1000)

    def updateTasks(self, results):
        self.clear()
        self.bottomStackSwitcher.setCount(self, str(len(results)))
        for i in results:
            item = QtGui.QTreeWidgetItem()
            item.setIcon(0, QtGui.QIcon(
                os.path.join("Resources","images","Clear Green Button")))
            item.setText(1, i[0])
            item.setText(2, str(i[1]))
            item.setText(3, i[2])
            self.addTopLevelItem(item)

    def taskPressed(self, item):
        lineno = int(item.text(2)) - 1
        self.editorTabWidget.showLine(lineno)

    def findTasks(self):
        self.taskFinder.findTasks(self.editorTabWidget)
