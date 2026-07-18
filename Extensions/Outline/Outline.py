import logging
import os
from operator import itemgetter

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QIcon
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

from Extensions.Outline.Python import pyclbr


class PythonOutlineThread(QThread):

    updateNavigator = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.source = ""
        self._generation = 0

    def run(self):
        generation = self._generation
        try:
            outlineDict = pyclbr._readmodule(self.source)
        except Exception:
            logging.debug("Outline parse failed", exc_info=True)
            outlineDict = {}
        if generation != self._generation:
            return
        self.updateNavigator.emit(outlineDict)

    def startNavigator(self, source):
        self.source = source
        self._generation += 1
        if self.isRunning():
            return False
        self.start()
        return True


class Outline(QTreeWidget):

    def __init__(self, useData, editorTabWidget, parent=None):
        QTreeWidget.__init__(self, parent)

        self.pythonOutlineThread = PythonOutlineThread(self)
        self.useData = useData
        self.editorTabWidget = editorTabWidget
        self._outline_pending = False

        self.setObjectName("sidebarItem")
        self.setStyleSheet("QTreeView {margin-top: 23px;}")
        self.setAccessibleName("Code outline")

        self.navigatorTimer = QTimer()
        self.navigatorTimer.setSingleShot(True)
        self.navigatorTimer.timeout.connect(self.startOutline)

        self.editorTabWidget.currentChanged.connect(self.startNavigatorTimer)
        self.editorTabWidget.currentEditorTextChanged.connect(
            self.startNavigatorTimer)

        self.pythonOutlineThread.updateNavigator.connect(self.updateOutline)
        self.pythonOutlineThread.finished.connect(self._outlineThreadFinished)

        self.setAutoScroll(True)
        self.setAnimated(True)
        self.setAutoScrollMargin(1)
        self.setHeaderHidden(True)
        self.activated.connect(self.navigatorItemActivated)
        self.itemPressed.connect(self.navigatorItemActivated)

    def startNavigatorTimer(self):
        self.navigatorTimer.start(500)

    def startOutline(self):
        source = self.editorTabWidget.getSource()
        started = self.pythonOutlineThread.startNavigator(source)
        if not started:
            self._outline_pending = True

    def _outlineThreadFinished(self):
        if self._outline_pending:
            self._outline_pending = False
            self.startOutline()

    def updateOutline(self, outlineDict):
        self.clear()

        objs = list(outlineDict.values())
        objs.sort(key=lambda a: getattr(a, 'lineno', 0))
        for obj in objs:
            if obj.objectType == "Class":
                classItem = QTreeWidgetItem()
                classItem.setText(0, obj.name)
                classItem.setIcon(0,
                                 QIcon(os.path.join("Resources", "images", "class")))
                classItem.setForeground(0,
                                         QBrush(QColor("#FF0000")))
                classItem.setData(0, 3, obj.lineno)
                self.addTopLevelItem(classItem)
                classItem.setExpanded(True)

                methods = sorted(obj.methods.items(), key=itemgetter(1))
                for name, lineno in methods:
                    functionItem = QTreeWidgetItem(classItem)
                    functionItem.setText(0, name)
                    functionItem.setData(0, 3, lineno)
                    functionItem.setIcon(0,
                                        QIcon(os.path.join("Resources", "images", "function")))
                    self.addTopLevelItem(functionItem)
            elif obj.objectType == "Function":
                functionItem = QTreeWidgetItem()
                functionItem.setText(0, obj.name)
                functionItem.setData(0, 3, obj.lineno)
                functionItem.setIcon(0,
                                    QIcon(os.path.join("Resources", "images", "function")))
                self.addTopLevelItem(functionItem)
            elif obj.objectType == "GlobalVariable":
                globalItem = QTreeWidgetItem()
                globalItem.setText(0, obj.name)
                globalItem.setData(0, 3, obj.lineno)
                globalItem.setIcon(0,
                                    QIcon(os.path.join("Resources", "images", "led")))
                self.addTopLevelItem(globalItem)

        if len(outlineDict) == 0:
            item = QTreeWidgetItem()
            item.setText(0, "<Empty>")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.addTopLevelItem(item)
            item.setExpanded(True)

    def navigatorItemActivated(self):
        currentEditor = self.editorTabWidget.focusedEditor()
        item = self.selectedItems()[0]
        if item is None:
            selection = currentEditor.selectedItems()
            if len(selection) == 0:
                return
            else:
                item = selection[0]
        if item.data(0, 3) is None:
            return
        else:
            line = item.data(0, 3) - 1
            currentEditor.setSelection(line, 0, line,
                                       currentEditor.lineLength(line) - 1)
            currentEditor.setFirstVisibleLine(line)
