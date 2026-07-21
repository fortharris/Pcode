from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup, QHBoxLayout, QPushButton, QWidget,
)


class StackSwitcher(QWidget):

    changed = pyqtSignal(str)

    def __init__(self, stack, parent=None):
        QWidget.__init__(self, parent)

        self.stack = stack
        self.lastIndex = 0

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(True)
        self.buttonGroup.buttonPressed.connect(self.setIndex)

    def addButton(self, name=None, icon=None, toolTip=None, showText=True):
        button = QPushButton()
        switch_name = name or toolTip or ""
        button.setProperty("switchName", switch_name)
        if name is not None and showText:
            button.setText(name)
        if toolTip is not None:
            button.setToolTip(toolTip)
            button.setAccessibleName(toolTip)
        elif name is not None:
            button.setAccessibleName(name)
        button.setCheckable(True)
        if icon is not None:
            button.setIcon(icon)
        self.buttonGroup.addButton(button)
        self.buttonGroup.setId(button, self.lastIndex)
        self.mainLayout.addWidget(button)

        self.lastIndex += 1

    def _button_name(self, button):
        name = button.property("switchName")
        if name:
            return name
        tip = button.toolTip()
        if tip:
            return tip
        return button.text()

    def setIndex(self, button):
        index = self.buttonGroup.id(button)
        self.stack.setCurrentIndex(index)
        self.changed.emit(self._button_name(button))

    def setCount(self, widget, text):
        index = self.stack.indexOf(widget)
        button = self.buttonGroup.button(index)
        if button is None:
            return
        # Badge counts stay visible; empty clears back to icon-only.
        button.setText("" if text in (None, "") else str(text))

    def setCurrentWidget(self, widget):
        index = self.stack.indexOf(widget)
        button = self.buttonGroup.button(index)
        button.setChecked(True)
        self.stack.setCurrentWidget(widget)

        self.changed.emit(self._button_name(button))

    def setDefault(self):
        button = self.buttonGroup.button(0)
        button.setChecked(True)
        self.changed.emit(self._button_name(button))

    def setButton(self, name):
        for button in self.buttonGroup.buttons():
            if (button.text() == name
                    or button.property("switchName") == name
                    or button.toolTip() == name
                    or button.accessibleName() == name):
                self.setIndex(button)
                button.setChecked(True)
                return True
        return False
