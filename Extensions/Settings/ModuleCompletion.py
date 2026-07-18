from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem


class ModuleCompletion(QTreeWidget):

    def __init__(self, useData, parent=None):
        QTreeWidget.__init__(self, parent)

        self.useData = useData
        self.selectedItem = None
        self.selectedParent = None

        self.setHeaderLabel("Modules")
        for name, value in self.useData.libraryDict.items():
            try:
                submodules, use = value[0], value[1]
            except (TypeError, IndexError, KeyError):
                continue
            item = QTreeWidgetItem(self)
            item.setText(0, name)
            checked = str(use).lower() in ("true", "1", "yes")
            item.setCheckState(
                0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

            for sub in submodules or []:
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
        if selected:
            self.selectedItem = selected[0]
            self.selectedParent = self.selectedItem.parent()
        else:
            # Right-click on empty area (common when modules list is empty).
            self.selectedItem = self.itemAt(event.pos())
            self.selectedParent = (
                self.selectedItem.parent() if self.selectedItem is not None
                else None)

        has_item = self.selectedItem is not None
        is_top = has_item and self.selectedParent is None
        is_child = has_item and self.selectedParent is not None

        self.removeItemAct.setEnabled(is_top)
        self.addModuleAct.setEnabled(has_item)
        self.removeModuleAct.setEnabled(is_child)
        # Add Library stays enabled even with an empty tree.
        self.addItemAct.setEnabled(True)

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
        if self.selectedItem is None or self.selectedParent is not None:
            return
        name = self.selectedItem.text(0)
        self.useData.libraryDict.pop(name, None)
        index = self.indexOfTopLevelItem(self.selectedItem)
        if index >= 0:
            self.takeTopLevelItem(index)
        self.useData.saveModulesForCompletion()

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
        if self.selectedItem is None or self.selectedParent is None:
            return
        itemText = self.selectedItem.text(0)
        parentText = self.selectedParent.text(0)
        entry = self.useData.libraryDict.get(parentText)
        if entry and itemText in entry[0]:
            entry[0].remove(itemText)
        parent = self.selectedParent
        parent.removeChild(self.selectedItem)
        self.useData.saveModulesForCompletion()
