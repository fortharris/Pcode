from PyQt4 import QtGui, QtCore


class MessagesWidget(QtGui.QTreeWidget):

    def __init__(self, bottomStackSwitcher, vSplitter, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)

        self.bottomStackSwitcher = bottomStackSwitcher
        self.vSplitter = vSplitter

        self.setHeaderLabels(["Message", "Time"])
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 40)

    def addMessage(self, messType, title, messageList):
        parentItem = QtGui.QTreeWidgetItem(self)
        if messType == 0:
            parentItem.setIcon(0, QtGui.QIcon(
                "Resources\\images\\security\\attention"))
        elif messType == 1:
            parentItem.setIcon(0, QtGui.QIcon(
                "Resources\\images\\security\\warning"))
        elif messType == 2:
            parentItem.setIcon(0, QtGui.QIcon(
                "Resources\\images\\security\\danger"))
        parentItem.setText(0, title)
        parentItem.setText(1, QtCore.QDateTime().currentDateTime().toString())
        for i in messageList:
            item = QtGui.QTreeWidgetItem(parentItem)
            item.setFirstColumnSpanned(True)
            item.setText(0, i)
            parentItem.addChild(item)
        parentItem.setExpanded(True)
        self.scrollToItem(parentItem, 1)

        self.vSplitter.showMessageAvailable()
        self.bottomStackSwitcher.setCount(self, str(self.topLevelItemCount()))
        self.bottomStackSwitcher.setCurrentWidget(self)
