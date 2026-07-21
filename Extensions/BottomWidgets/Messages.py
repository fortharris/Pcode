import os

from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem


class MessagesWidget(QTreeWidget):

    def __init__(self, bottomStackSwitcher, vSplitter, parent=None):
        QTreeWidget.__init__(self, parent)

        self.setAccessibleName("Messages")
        self.bottomStackSwitcher = bottomStackSwitcher
        self.vSplitter = vSplitter

        self.setHeaderLabels(["Message", "Time"])
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 40)
        self._show_empty_state()

    def _show_empty_state(self):
        if self.topLevelItemCount() > 0:
            return
        item = QTreeWidgetItem(self)
        item.setFirstColumnSpanned(True)
        item.setText(0, "No messages yet")
        item.setFlags(Qt.ItemFlag.NoItemFlags)

    def addMessage(self, messType, title, messageList):
        # Remove empty-state placeholder if present.
        if (self.topLevelItemCount() == 1
                and self.topLevelItem(0).text(0) == "No messages yet"):
            self.takeTopLevelItem(0)

        parentItem = QTreeWidgetItem(self)
        if messType == 0:
            parentItem.setIcon(0, QIcon(
                os.path.join("Resources", "images", "security", "attention")))
        elif messType == 1:
            parentItem.setIcon(0, QIcon(
                os.path.join("Resources", "images", "security", "warning")))
        elif messType == 2:
            parentItem.setIcon(0, QIcon(
                os.path.join("Resources", "images", "security", "danger")))
        parentItem.setText(0, title)
        parentItem.setText(1, QDateTime.currentDateTime().toString())
        for i in messageList:
            item = QTreeWidgetItem(parentItem)
            item.setFirstColumnSpanned(True)
            item.setText(0, i)
            parentItem.addChild(item)
        parentItem.setExpanded(True)
        self.scrollToItem(parentItem, 1)

        # Badge + flash collapsed bottom pane; do not steal the active panel.
        self.vSplitter.showMessageAvailable()
        self.bottomStackSwitcher.setCount(self, str(self.topLevelItemCount()))
