import os
from operator import itemgetter

from PyQt4 import QtCore, QtGui
from Extensions.Outline.Python import pyclbr


class PythonOutlineThread(QtCore.QThread):

    updateNavigator = QtCore.pyqtSignal(dict)

    def run(self):
        outlineDict = pyclbr._readmodule(self.source)
        self.updateNavigator.emit(outlineDict)

    def startNavigator(self, source):
        self.source = source
        self.start()


class Outline(QtGui.QTreeWidget):

    def __init__(self, useData, editorTabWidget, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)

        self.pythonOutlineThread = PythonOutlineThread()
        self.useData = useData
        self.editorTabWidget = editorTabWidget

        self.navigatorTimer = QtCore.QTimer()
        self.navigatorTimer.setSingleShot(True)
        self.navigatorTimer.setInterval(500)
        self.navigatorTimer.timeout.connect(self.startOutline)

        self.editorTabWidget.currentChanged.connect(self.navigatorTimer.start)
        self.editorTabWidget.currentEditorTextChanged.connect(
            self.navigatorTimer.start)

        self.pythonOutlineThread.updateNavigator.connect(self.updateOutline)

        self.setAutoScroll(True)
        self.setAnimated(True)
        self.setAutoScrollMargin(1)
        self.setHeaderHidden(True)
        self.activated.connect(self.navigatorItemActivated)
        self.itemPressed.connect(self.navigatorItemActivated)

    def startOutline(self):
        self.pythonOutlineThread.startNavigator(
            self.editorTabWidget.getSource())

    def updateOutline(self, outlineDict):
        self.clear()

        objs = list(outlineDict.values())
        objs.sort(key=lambda a: getattr(a, 'lineno', 0))
        for obj in objs:
            if obj.objectType == "Class":
                # obj.name, obj.super, obj.lineno
                classItem = QtGui.QTreeWidgetItem()
                classItem.setText(0, obj.name)
                classItem.setIcon(0,
                                 QtGui.QIcon(os.path.join("Resources", "images", "class")))
                classItem.setForeground(0,
                                         QtGui.QBrush(QtGui.QColor("#FF0000")))
                classItem.setData(0, 3, obj.lineno)
                self.addTopLevelItem(classItem)
                classItem.setExpanded(True)

                methods = sorted(obj.methods.items(), key=itemgetter(1))
                for name, lineno in methods:
                    # obj.name, obj.lineno
                    functionItem = QtGui.QTreeWidgetItem(classItem)
                    functionItem.setText(0, name)
                    functionItem.setData(0, 3, lineno)
                    functionItem.setIcon(0,
                                        QtGui.QIcon(os.path.join("Resources", "images", "function")))
                    self.addTopLevelItem(functionItem)
            elif obj.objectType == "Function":
               # obj.name, obj.lineno
                methods = sorted(obj.methods.items(), key=itemgetter(1))
                for name, lineno in methods:
                    print("  def", name, lineno)
                    functionItem = QtGui.QTreeWidgetItem()
                    functionItem.setText(0, name)
                    functionItem.setData(0, 3, lineno)
                    functionItem.setIcon(0,
                                        QtGui.QIcon(os.path.join("Resources", "images", "function")))
                    self.addTopLevelItem(functionItem)

        if len(outlineDict) == 0:
            item = QtGui.QTreeWidgetItem()
            item.setText(0, "<Empty>")
            item.setFlags(QtCore.Qt.NoItemFlags)
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
