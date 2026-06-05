from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem


class ModuleCompletion(QTreeWidget):

    def __init__(self, useData, parent=None):
        QTreeWidget.__init__(self, parent)

        self.useData = useData

        self.setHeaderLabel("Modules")
        for i, v in self.useData.libraryDict.items():
            item = QTreeWidgetItem(self)
            item.setCheckState(0, False)
            item.setText(0, i)
            item.setCheckState(0, 2)

            for sub in v[0]:
                subItem = QTreeWidgetItem(item)
                subItem.setText(0, sub)

        self.createActions()

    def createActions(self):
        self.addItemAct = QAction(
            "Add Library", self, statusTip="Add Library", triggered=self.addLibrary)

        self.removeItemAct = \
            QAction(
                "Remove Library", self, statusTip="Remove Library", triggered=self.removeLibrary)

        self.addModuleAct = \
            QAction(
                "Add Module", self, statusTip="Add Module", triggered=self.addModule)

        self.removeModuleAct = \
            QAction(
                "Remove Module", self, statusTip="Remove Module", triggered=self.removeModule)

        self.contextMenu = QMenu()
        self.contextMenu.addAction(self.addItemAct)
        self.contextMenu.addAction(self.removeItemAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.addModuleAct)
        self.contextMenu.addAction(self.removeModuleAct)

    def contextMenuEvent(self, event):
        selected = self.selectedItems()
        self.selectedItem = selected[0]
        self.selectedParent = self.selectedItem.parent()

        self.contextMenu.exec(event.globalPos())

    def addLibrary(self):
        return
        if self.selectedParent is None:
            parent = self.selectedItem
        else:
            parent = self.selectedParent
        newItem = QTreeWidgetItem()
        newItem.setFlags(Qt.ItemFlag.ItemIsEditable |
                         Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        parent.insertChild(self.cu, newItem)
        self.editItem(newItem)

    def removeLibrary(self):
        if self.selectedParent != None:
            itemText = self.selectedItem.text(0)
            parentText = self.selectedParent.text(0)
            self.useData.libraryDict[parentText][0].remove(itemText)
            self.setItemHidden(self.selectedItem, True)

    def addModule(self):
        return
        if self.selectedParent is None:
            parent = self.selectedItem
        else:
            parent = self.selectedParent
        newItem = QTreeWidgetItem()
        newItem.setFlags(Qt.ItemFlag.ItemIsEditable |
                         Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        parent.insertChild(self.cu, newItem)
        self.editItem(newItem)

    def removeModule(self):
        if self.selectedParent != None:
            itemText = self.selectedItem.text(0)
            parentText = self.selectedParent.text(0)
            self.useData.libraryDict[parentText][0].remove(itemText)
            self.setItemHidden(self.selectedItem, True)