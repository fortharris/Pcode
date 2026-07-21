import os

from PyQt6.QtCore import QDateTime
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

    def addMessage(self, messType, title, messageList):
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

        self.vSplitter.showMessageAvailable()
        self.bottomStackSwitcher.setCount(self, str(self.topLevelItemCount()))
        self.bottomStackSwitcher.setCurrentWidget(self)
