from PyQt4 import QtCore, QtGui


class ModuleCompletion(QtGui.QTreeWidget):

    def __init__(self, useData, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)

        self.useData = useData

        self.setHeaderLabel("Modules")
        for i, v in self.useData.libraryDict.items():
            item = QtGui.QTreeWidgetItem(self)
            item.setCheckState(0, False)
            item.setText(0, i)
            item.setCheckState(0, 2)

            for sub in v[0]:
                subItem = QtGui.QTreeWidgetItem(item)
                subItem.setText(0, sub)

        self.createActions()

    def createActions(self):
        self.addItemAct = QtGui.QAction(
            "Add Item", self, statusTip="Add Item", triggered=self.addItem)

        self.removeItemAct = \
            QtGui.QAction(
                "Remove Item", self, statusTip="Remove Item", triggered=self.removeItem)

        self.addModuleAct = \
            QtGui.QAction(
                "Add Module", self, statusTip="Add Module", triggered=self.addModule)

        self.removeModuleAct = \
            QtGui.QAction(
                "Remove Module", self, statusTip="Remove Module", triggered=self.removeModule)

        self.contextMenu = QtGui.QMenu()
        self.contextMenu.addAction(self.addItemAct)
        self.contextMenu.addAction(self.removeItemAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.addModuleAct)
        self.contextMenu.addAction(self.removeModuleAct)

    def contextMenuEvent(self, event):
        selected = self.selectedItems()
        self.selectedItem = selected[0]
        self.selectedParent = self.selectedItem.parent()

        self.contextMenu.exec_(event.globalPos())

    def addItem(self):
        return
        if self.selectedParent is None:
            parent = self.selectedItem
        else:
            parent = self.selectedParent
        newItem = QtGui.QTreeWidgetItem()
        newItem.setFlags(QtCore.Qt.ItemIsEditable |
                         QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        parent.insertChild(self.cu, newItem)
        self.editItem(newItem)

    def removeItem(self):
        if self.selectedParent != None:
            itemText = self.selectedItem.text(0)
            parentText = self.selectedParent.text(0)
            self.useData.libraryDict[parentText][0].remove(itemText)
            self.setItemHidden(self.selectedItem, True)

    def addModule(self):
        pass

    def removeModule(self):
        pass
