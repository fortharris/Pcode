import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
)

import autopep8
import pycodestyle as pep8
import pyflakes
import rope


def _rope_version():
    return getattr(rope, "VERSION", None) or getattr(rope, "__version__", "unknown")


def _cx_freeze_version():
    try:
        import cx_Freeze
        return getattr(cx_Freeze, "__version__", None) or cx_Freeze.version
    except Exception:
        return "n/a"


def _pyqt6_version():
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR
        return PYQT_VERSION_STR
    except Exception:
        try:
            import PyQt6
            return getattr(PyQt6, "__version__", "unknown")
        except Exception:
            return "unknown"


class About(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(
            self, parent,
            Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("About")

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.setFixedSize(500, 270)

        form = QFormLayout()
        form.setContentsMargins(10, 10, 10, 10)
        form.addRow("<b>Version</b>", QLabel("0.1.5"))
        form.addRow("<b>Author</b>", QLabel("Amoatey Harrison"))
        form.addRow("<b>Email</b>", QLabel("fortharris@gmail.com"))

        mainLayout.addLayout(form)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(5, 0, 5, 0)
        mainLayout.addLayout(hbox)

        self.label = QLabel("External Libraries:")
        hbox.addWidget(self.label)

        hbox.addStretch(1)

        licenseButton = QPushButton("License")
        licenseButton.setCheckable(True)
        licenseButton.clicked.connect(self.showLicense)
        hbox.addWidget(licenseButton)

        self.view = QStackedWidget()
        mainLayout.addWidget(self.view)

        table = QTreeWidget()
        table.setMinimumHeight(150)
        table.setIndentation(0)
        table.setHeaderLabels(["Name", "Version", "Author"])
        table.setColumnWidth(0, 150)
        table.addTopLevelItem(QTreeWidgetItem(
            ["Rope", _rope_version(), "Ali Gholami Rudi"]))
        table.addTopLevelItem(QTreeWidgetItem(
            ["PyFlakes", pyflakes.__version__, "Florent Xicluna"]))
        table.addTopLevelItem(QTreeWidgetItem(
            ["Pep8", pep8.__version__, "Florent Xicluna"]))
        table.addTopLevelItem(QTreeWidgetItem(
            ["PyQt6", _pyqt6_version(), "The Qt Company"]))
        table.addTopLevelItem(QTreeWidgetItem(
            ["AutoPep8", autopep8.__version__, "Hideo Hattori"]))
        table.addTopLevelItem(QTreeWidgetItem(
            ["CxFreeze", _cx_freeze_version(), "Anthony Tuininga"]))
        self.view.addWidget(table)

        self.licenseEdit = QTextEdit()
        with open(os.path.join("Resources", "LICENSE"), "r", encoding="utf-8") as file:
            self.licenseEdit.setText(file.read())

        self.view.addWidget(self.licenseEdit)

        self.hide()

    def showLicense(self, checked):
        if checked:
            self.view.setCurrentIndex(1)
            self.label.hide()
        else:
            self.view.setCurrentIndex(0)
            self.label.show()
