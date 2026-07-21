import os
import re

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem


class TaskFinderThread(QThread):

    TASKS_PATTERN = r"(^|#)[ ]*(TODO|FIXME|XXX|HINT|TIP)( |:)([^#]*)"
    newTasks = pyqtSignal(list)
    results = []

    def run(self):
        """Find tasks in source code (TODO, FIXME, XXX, ...)."""
        results = []
        for line, text in enumerate(self.source.splitlines()):
            for todo in re.findall(self.TASKS_PATTERN, text):
                results.append((todo[1], line + 1, todo[
                               -1].strip().capitalize()))
        if results != self.results:
            self.results = []
            self.results.extend(results)
            self.newTasks.emit(results)

    def findTasks(self, source):
        self.source = source

        self.start()


class Tasks(QTreeWidget):

    def __init__(self, editorTabWidget, bottomStackSwitcher, parent=None):
        QTreeWidget.__init__(self, parent)

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

        self.taskFinderTimer = QTimer()
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
                    """)

    def startTimer(self):
        self.taskFinderTimer.start(1000)

    def updateTasks(self, results):
        self.clear()
        self.bottomStackSwitcher.setCount(self, str(len(results)))
        if not results:
            item = QTreeWidgetItem()
            item.setText(3, "No TODO / FIXME tasks in this file")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.addTopLevelItem(item)
            return
        for i in results:
            item = QTreeWidgetItem()
            item.setIcon(0, QIcon(
                os.path.join("Resources", "images", "Clear Green Button")))
            item.setText(1, i[0])
            item.setText(2, str(i[1]))
            item.setText(3, i[2])
            self.addTopLevelItem(item)

    def taskPressed(self, item):
        lineno = int(item.text(2)) - 1
        self.editorTabWidget.showLine(lineno)

    def findTasks(self):
        self.taskFinder.findTasks(self.editorTabWidget.getSource())
