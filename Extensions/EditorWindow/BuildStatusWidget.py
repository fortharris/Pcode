from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QWidget


class BuildStatusWidget(QWidget):

    cancel = pyqtSignal()

    def __init__(self, app, useData, parent=None):
        QWidget.__init__(self, parent)

        self.useData = useData
        self.app = app

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        mainLayout.addWidget(QLabel("Build Started..."))

        self.progressBar = QProgressBar()
        self.progressBar.setMaximumHeight(10)
        self.progressBar.setMinimumWidth(100)
        self.progressBar.setStyleSheet("""
                                         QProgressBar {
                                             border: none;
                                             background: transparent;
                                             border-top: 1px solid #6570EA;
                                             border-radius: 0px;
                                         }

                                         QProgressBar::chunk {
                                             background-color: #65B0EA;
                                             width: 15px;
                                         }
                                        """)
        mainLayout.addWidget(self.progressBar)

        self.hide()

    def showBusy(self, busy):
        if busy:
            self.show()
            self.progressBar.setRange(0, 0)
        else:
            self.hide()
            self.progressBar.setRange(0, 1)
            if self.useData.setting_bool('SoundsEnabled'):
                self.app.beep()
