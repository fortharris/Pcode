from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter

from Extensions import StyleSheet


class VerticalSplitter(QSplitter):

    def __init__(self, parent=None):
        QSplitter.__init__(self, parent)

        self.setObjectName("vSplitter")
        self.setOrientation(Qt.Orientation.Vertical)

        self.bottomTabCollapsed = False
        self.splitterMoved.connect(self.updateStatus)
        self.showNormal()

    def _handle_style(self, color):
        return """
            QSplitter#vSplitter::handle {{
                background: none;
            }}
            QSplitter#vSplitter::handle:horizontal {{
                width: 5px;
            }}
            QSplitter#vSplitter::handle:vertical {{
                background: {color};
            }}
            QSplitter#vSplitter::handle:pressed {{
                background: {pressed};
            }}
        """.format(
            color=color,
            pressed=StyleSheet.CURRENT_PALETTE.get("textDim", "gray"))

    def updateStatus(self):
        bottomTabSize = self.sizes()[1]
        self.bottomTabCollapsed = (bottomTabSize == 0)
        if self.bottomTabCollapsed:
            self.showNormal()

    def showMessageAvailable(self):
        if not self.bottomTabCollapsed:
            return
        p = StyleSheet.CURRENT_PALETTE
        self.setStyleSheet(self._handle_style(p.get("info", p["accent"])))

    def showRunning(self):
        if not self.bottomTabCollapsed:
            return
        p = StyleSheet.CURRENT_PALETTE
        self.setStyleSheet(self._handle_style(p.get("success", "#4EC24E")))

    def showError(self):
        if not self.bottomTabCollapsed:
            return
        p = StyleSheet.CURRENT_PALETTE
        self.setStyleSheet(self._handle_style(p.get("danger", "#FD6500")))

    def showNormal(self):
        p = StyleSheet.CURRENT_PALETTE
        self.setStyleSheet(self._handle_style(p.get("border", "lightgray")))
