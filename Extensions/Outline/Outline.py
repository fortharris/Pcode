from PyQt4 import QtCore, QtGui
from Extensions.Outline.Python import pyclbr


class PythonOutlineThread(QtCore.QThread):

    updateNavigator = QtCore.pyqtSignal(list)

    def run(self):
        outlineList = []

        dict = pyclbr.readmodule_ex(self.editorTabWidget.getSource())
        listed = list(dict.items())
        newList = []
        for i in listed:
            n = []
            n.append(i[0])
            n.append(i[1])
            n.append(i[1].lineno)
            newList.append(n)
        s = sorted(newList, key=lambda member: member[2])

        self.updateNavigator.emit(s)

    def startNavigator(self, editorTabWidget):
        self.editorTabWidget = editorTabWidget
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
        self.editorTabWidget.currentEditorTextChanged.connect(self.navigatorTimer.start)
        
        self.pythonOutlineThread.updateNavigator.connect(self.updateOutline)

        self.setAutoScroll(True)
        self.setAnimated(True)
        self.setAutoScrollMargin(1)
        self.setHeaderHidden(True)
        self.activated.connect(self.navigatorItemActivated)
        self.itemPressed.connect(self.navigatorItemActivated)

    def startOutline(self):
        self.pythonOutlineThread.startNavigator(self.editorTabWidget)

    def updateOutline(self, outlineList):
        self.clear()
        for x in outlineList:
            object = x[1]
            if "Function" in str(object):
                item = QtGui.QTreeWidgetItem()
                item.setText(0, x[0])
                item.setData(0, 3, x[2])
                item.setIcon(0,
                             QtGui.QIcon("Resources\\images\\function"))
                self.addTopLevelItem(item)
                item.setExpanded(True)
            elif "Class" in str(object):
                sub_parent = QtGui.QTreeWidgetItem()
                if x[0] == "@@Globals@@":
                    attributes = list(object.globals.items())
                    newList = []
                    for m in attributes:
                        n = []
                        n.append(m[0])
                        n.append(m[1])
                        n.append(m[1].lineno)
                        newList.append(n)
                    sorted_attrib = sorted(
                        newList, key=lambda member: member[2])
                    for i in sorted_attrib:
                        attribute = QtGui.QTreeWidgetItem()
                        attribute.setText(0, i[0])
                        attribute.setIcon(0,
                                          QtGui.QIcon("Resources\\images\\led"))
                        attribute.setData(0, 3, i[2])
                        self.addTopLevelItem(attribute)
                        attribute.setExpanded(True)
                    continue
                elif x[0] == "@@Coding@@":
                    sub_parent.setText(0, "-- coding --")
                else:
                    sub_parent.setText(0, x[0])
                    sub_parent.setIcon(0,
                                       QtGui.QIcon("Resources\\images\\class"))
                sub_parent.setForeground(0,
                                         QtGui.QBrush(QtGui.QColor("#FF0000")))
                sub_parent.setData(0, 3, x[2])
                self.addTopLevelItem(sub_parent)
                sub_parent.setExpanded(True)

                attributes = list(object.attributes.items())
                newList = []
                for m in attributes:
                    n = []
                    n.append(m[0])
                    n.append(m[1])
                    n.append(m[1].lineno)
                    newList.append(n)
                sorted_attrib = sorted(newList, key=lambda member: member[2])

                attrib = QtGui.QTreeWidgetItem()
                attrib.setText(0, "Attributes")
                if len(sorted_attrib) == 0:
                    pass
                else:
                    for i in sorted_attrib:
                        attribute = QtGui.QTreeWidgetItem()
                        attribute.setText(0, i[0])
                        attribute.setIcon(0,
                                          QtGui.QIcon("Resources\\images\\led"))
                        attribute.setData(0, 3, i[2])
                        attrib.addChild(attribute)
                    sub_parent.addChild(attrib)

                methods = list(object.methods.items())
                newList = []
                for m in methods:
                    n = []
                    n.append(m[0])
                    n.append(m[1])
                    n.append(m[1].lineno)
                    n.append(m[1].parameters)
                    newList.append(n)
                sorted_meth = sorted(newList, key=lambda member: member[2])
                for i in sorted_meth:  # (name, line)
                    item = QtGui.QTreeWidgetItem()
                    item.setText(0, i[0])
                    item.setData(0, 3, i[2])
                    item.setIcon(0,
                                 QtGui.QIcon("Resources\\images\\function"))
                    sub_parent.addChild(item)
        if len(outlineList) == 0:
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
