from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter


class VerticalSplitter(QSplitter):

    def __init__(self, parent=None):
        QSplitter.__init__(self, parent)

        self.setObjectName("vSplitter")
        self.setOrientation(Qt.Orientation.Vertical)

        self.bottomTabCollapsed = False
        self.splitterMoved.connect(self.updateStatus)

    def updateStatus(self):
        bottomTabSize = self.sizes()[1]
        self.bottomTabCollapsed = (bottomTabSize == 0)
        if self.bottomTabCollapsed:
            self.showNormal()

    def showMessageAvailable(self):
        if not self.bottomTabCollapsed:
            return
        self.setStyleSheet("""

                                 QSplitter#vSplitter::handle {
                                     background: none;
                                 }

                                 QSplitter#vSplitter::handle:horizontal {
                                     width: 5px;
                                 }

                                 QSplitter#vSplitter::handle:vertical {
                                     background: #1281CB;
                                 }

                                 QSplitter#vSplitter::handle:pressed {
                                     background: gray;
                                 }

                              """)

    def showRunning(self):
        if not self.bottomTabCollapsed:
            return
        self.setStyleSheet("""

                                 QSplitter#vSplitter::handle {
                                     background: none;
                                 }

                                 QSplitter#vSplitter::handle:horizontal {
                                     width: 5px;
                                 }

                                 QSplitter#vSplitter::handle:vertical {
                                     background: #4EC24E;
                                 }

                                 QSplitter#vSplitter::handle:pressed {
                                     background: gray;
                                 }

                              """)

    def showError(self):
        if not self.bottomTabCollapsed:
            return
        self.setStyleSheet("""

                                 QSplitter#vSplitter::handle {
                                     background: none;
                                 }

                                 QSplitter#vSplitter::handle:horizontal {
                                     width: 5px;
                                 }

                                 QSplitter#vSplitter::handle:vertical {
                                     background: #FD6500;
                                 }

                                 QSplitter#vSplitter::handle:pressed {
                                     background: gray;
                                 }

                              """)

    def showNormal(self):
        self.setStyleSheet("""

                                 QSplitter#vSplitter::handle {
                                     background: none;
                                 }

                                 QSplitter#vSplitter::handle:vertical {
                                     background: lightgray;
                                 }

                                 QSplitter#vSplitter::handle:pressed {
                                     background: gray;
                                 }

                              """)
