from PyQt4 import QtCore, QtGui

from Extensions import StyleSheet

import os.path

class ViewSwitcher(QtGui.QLabel):

    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)

        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        self.setMinimumWidth(175)
        self.setMaximumWidth(175)

        self.lastIndex = 0

        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)

        self.editorTabWidget = parent
        self.editorTabWidget.currentChanged.connect(self.setCurrentView)

        self.buttonGroup = QtGui.QButtonGroup()
        self.buttonGroup.setExclusive(True)
        self.buttonGroup.buttonPressed.connect(self.viewChanged)

        self.hideButton = QtGui.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(QtGui.QIcon(os.path.join("Resources","images","exit")))
        self.hideButton.clicked.connect(self.hide)
        self.mainLayout.addWidget(self.hideButton)

        self.setStyleSheet(StyleSheet.subTaskSwitcherStyle)

        self.addButton(QtGui.QIcon(
            os.path.join("Resources","images","notes_selected")), "Editor")
        self.addButton(QtGui.QIcon(
            os.path.join("Resources","images","notes")), "Snapshot")
        self.addButton(QtGui.QIcon(
            os.path.join("Resources","images","links_selected")), "Unified Diff")
        self.addButton(QtGui.QIcon(
            os.path.join("Resources","images","links")), "Context Diff")

    def setCurrentView(self):
        index = self.editorTabWidget.currentWidget().currentIndex()
        self.setIndex(None, index)
        
    def viewChanged(self, button):
        index = self.buttonGroup.id(button)
        self.setIndex(button, index)
        if index == 2:
            self.editorTabWidget.getUnifiedDiff().generateUnifiedDiff()
        if index == 3:
            self.editorTabWidget.getContextDiff().generateContextDiff()

    def addButton(self, icon, toolTip):
        button = QtGui.QToolButton()
        button.setToolTip(toolTip)
        button.setCheckable(True)
        button.setIcon(icon)
        self.buttonGroup.addButton(button)
        self.buttonGroup.setId(button, self.lastIndex)
        self.mainLayout.addWidget(button)

        self.lastIndex += 1

    def setIndex(self, button, index=None):
        button = self.buttonGroup.button(index)
        button.setChecked(True)
        subStack = self.editorTabWidget.currentWidget()
        subStack.setCurrentIndex(index)

    def setDefault(self):
        """
        Shows the active button after initialization
        """
        button = self.buttonGroup.button(0)
        button.setChecked(True)
        self.changed.emit(button.text())
