import os

from Extensions.qt_bindings import QtGui, QtCore

import autopep8
import pycodestyle as pep8
import pyflakes
import rope


def _cx_freeze_version():
    try:
        import cx_Freeze
        return getattr(cx_Freeze, "__version__", None) or cx_Freeze.version
    except Exception:
        return "n/a"


class About(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent,
                               QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("About")

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.setFixedSize(500, 270)

        form = QtGui.QFormLayout()
        form.setContentsMargins(10, 10, 10, 10)
        form.addRow("<b>Version</b>", QtGui.QLabel("0.1.5"))
        form.addRow("<b>Author</b>", QtGui.QLabel("Amoatey Harrison"))
        form.addRow("<b>Email</b>", QtGui.QLabel("fortharris@gmail.com"))

        mainLayout.addLayout(form)

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(5, 0, 5, 0)
        mainLayout.addLayout(hbox)

        self.label = QtGui.QLabel("External Libraries:")
        hbox.addWidget(self.label)

        hbox.addStretch(1)

        licenseButton = QtGui.QPushButton("License")
        licenseButton.setCheckable(True)
        licenseButton.clicked.connect(self.showLicense)
        hbox.addWidget(licenseButton)

        self.view = QtGui.QStackedWidget()
        mainLayout.addWidget(self.view)

        table = QtGui.QTreeWidget()
        table.setMinimumHeight(150)
        table.setIndentation(0)
        table.setHeaderLabels(["Name", "Version", "Author"])
        table.setColumnWidth(0, 150)
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["Rope", rope.VERSION, "Ali Gholami Rudi"]))
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["PyFlakes", pyflakes.__version__, "Florent Xicluna"]))
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["Pep8", pep8.__version__, "Florent Xicluna"]))
        import PyQt6
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["PyQt6", PyQt6.__version__, "The Qt Company"]))
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["AutoPep8", autopep8.__version__, "Hideo Hattori"]))
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["CxFreeze", _cx_freeze_version(), "Anthony Tuininga"]))
        self.view.addWidget(table)

        self.licenseEdit = QtGui.QTextEdit()
        file = open(os.path.join("Resources", "LICENSE"), "r")
        self.licenseEdit.setText(file.read())
        file.close()

        self.view.addWidget(self.licenseEdit)

        self.hide()

    def showLicense(self, checked):
        if checked:
            self.view.setCurrentIndex(1)
            self.label.hide()
        else:
            self.view.setCurrentIndex(0)
            self.label.show()
