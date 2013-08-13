from PyQt4 import QtGui, QtCore

from Xtra import autopep8
from Xtra import pep8
import pyflakes
import rope
import cx_Freeze


class About(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent,
                               QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("About")

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        self.setFixedSize(500, 270)

        form = QtGui.QFormLayout()
        form.setMargin(10)
        form.addRow("<b>Version</b>", QtGui.QLabel("0.1"))
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
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["PyQt4", "4.10", "Riverbank Computing Limited"]))
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["AutoPep8", autopep8.__version__, "Hideo Hattori"]))
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["Export Formats", "5.2.2", "Detlev Offenbach"]))
        table.addTopLevelItem(QtGui.QTreeWidgetItem(
            ["CxFreeze", cx_Freeze.version, "Anthony Tuininga"]))
        self.view.addWidget(table)
        
        self.licenseEdit = QtGui.QTextEdit()
        file = open("Resources\\LICENSE.GPL3", "r")
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