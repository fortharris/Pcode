import os
import sys
import shutil


from Extensions.Projects.ProjectManager.ProjectView.ProjectView import IconProvider
from Pvenv import EnvBuilder

from Extensions import StyleSheet
from Extensions.file_dialog_utils import file_dialog_path
from PyQt6.QtCore import QDir, Qt
from PyQt6.QtGui import (
    QIcon, QFileSystemModel, QPalette,
)
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox,
    QPushButton, QSpinBox, QTabWidget, QToolButton, QTreeView, QVBoxLayout,
    QWidget,
)

class SelectBox(QDialog):

    def __init__(self, caption, itemsList, parent=None):
        QDialog.__init__(self, parent, Qt.WindowType.Window |
                               Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        mainLayout = QVBoxLayout()

        self.itemBox = QComboBox()
        self.itemBox.addItem()
        for i in itemsList:
            self.itemBox.addItems(itemsList)
        self.itemBox.currentIndexChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.itemBox)

        hbox = QHBoxLayout()

        hbox.addStretch(1)

        self.acceptButton = QPushButton("Ok")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)
        hbox.addWidget(self.cancelButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.resize(400, 20)
        self.enableAcceptButton()

        self.exec()

    def enableAcceptButton(self):
        if self.itemBox.currentIndex() == 0:
            self.acceptButton.setDisabled(True)
        else:
            self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.item = self.itemBox.currentText()
        self.close()

    def cancel(self):
        self.accepted = False
        self.close()


class GetText(QDialog):

    def __init__(self, caption, format, parent=None):
        QDialog.__init__(self, parent, Qt.WindowType.Window |
                               Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        mainLayout = QVBoxLayout()

        mainLayout.addWidget(QLabel(format))

        self.nameLine = QLineEdit()
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QHBoxLayout()

        self.statusLabel = QLabel()
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.acceptButton = QPushButton("Ok")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)
        hbox.addWidget(self.cancelButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.resize(400, 20)
        self.enableAcceptButton()

        self.exec()

    def enableAcceptButton(self):
        text = self.nameLine.text().strip()
        if text == '':
            self.acceptButton.setDisabled(True)
        else:
            self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.text = self.nameLine.text().strip()
        self.close()

    def cancel(self):
        self.accepted = False
        self.close()


class RopeConfig(QWidget):

    def __init__(self, projectPathDict, useData, parent=None):
        QWidget.__init__(self, parent)

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.ignoreSyntaxErrorsBox = QComboBox()
        self.ignoreSyntaxErrorsBox.addItem("Ignore Syntax Errors")
        self.ignoreSyntaxErrorsBox.addItem("Don't Ignore Syntax Errors")
#        self.ignoreSyntaxErrorsBox.setCurrentIndex(
# self.ignoreSyntaxErrorsBox.findText(profileData["appendscripttolibrary"]))
        mainLayout.addWidget(self.ignoreSyntaxErrorsBox)

        self.ignoreBadImportsBox = QComboBox()
        self.ignoreBadImportsBox.addItem("Ignore Bad Imports")
        self.ignoreBadImportsBox.addItem("Don't Ignore Bad Imports")
#        self.ignoreBadImportsBox.setCurrentIndex(
# self.ignoreBadImportsBox.findText(profileData["appendscripttolibrary"]))
        mainLayout.addWidget(self.ignoreBadImportsBox)

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addWidget(QLabel("Max History Items: "))
        self.maxHistoryBox = QSpinBox()
        hbox.addWidget(self.maxHistoryBox)

        frame = QFrame()
        frame.setGeometry(1, 1, 1, 2)
        frame.setFrameShape(frame.HLine)
        frame.setFrameShadow(frame.Sunken)
        mainLayout.addWidget(frame)

        self.listSelectorBox = QComboBox()
        self.listSelectorBox.addItem("Extensions")
        self.listSelectorBox.addItem("Ignored Resources")
        self.listSelectorBox.addItem("Custom Folders")
#        self.listSelectorBox.activated.connect(self.viewList)
#        self.listSelectorBox.currentIndexChanged.connect(self.viewList)
        mainLayout.addWidget(self.listSelectorBox)

        self.listWidget = QListWidget()
        mainLayout.addWidget(self.listWidget)

        self.helpDict = {
            "Extensions": "Specify which files should be considered python files.",
            "Ignored Resources": "Specify which files and folders to ignore in the project.",
            "Custom Folders": (
                "By default rope searches the project for finding source folders\n"
                "(folders that should be searched for finding modules).\n"
                "You can add paths to that list. Note that rope guesses project \n"
                "source folders correctly most of the time; use this if you have \n"
                "any problems.\n"
                "The folders should be relative to project root and use '/' for\n"
                "separating folders regardless of the platform rope is running on.\n"
                "src/my_source_folder' for instance."
                )
            }

        self.docLabel = QLabel()
        self.docLabel.setWordWrap(True)
        mainLayout.addWidget(self.docLabel)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        mainLayout.addLayout(hbox)

        self.addButton = QPushButton()
        self.addButton.setIcon(
            QIcon(os.path.join("Resources", "images", "add")))
#        self.addButton.clicked.connect(self.appendToList)
        hbox.addWidget(self.addButton)

        self.removeButton = QPushButton()
        self.removeButton.setIcon(
            QIcon(os.path.join("Resources", "images", "minus")))
#        self.removeButton.clicked.connect(self.removeItem)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

    def save(self):
        from Extensions.RopeProfile import save as save_rope_profile
        rope_folder = os.path.join(
            self.projectPathDict["root"], "Rope")
        save_rope_profile(rope_folder, {
            "ignore_syntax_errors": self.ignoreSyntaxErrorsBox.currentText(),
            "ignore_bad_imports": self.ignoreBadImportsBox.currentText(),
            "max_history_items": self.maxHistoryBox.value(),
            "extensions": ["*.py", "*.pyw"],
            "ignored_resources": [
                "*.pyc", "*~", ".ropeproject",
                ".hg", ".svn", "_svn", ".git", "__pycache__",
            ],
            "custom_folders": [],
        })


class VenvSetup(QWidget):

    def __init__(self, projectPathDict, projectSettings, useData, parent=None):
        QWidget.__init__(self, parent)

        self.projectPathDict = projectPathDict
        self.useData = useData
        self.projectSettings = projectSettings

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addWidget(QLabel("Version: "))

        self.currentVersionLabel = QLabel()
        hbox.addWidget(self.currentVersionLabel)

        self.openButton = QPushButton("Open")
        self.openButton.clicked.connect(self.openVenv)
        hbox.addWidget(self.openButton)

        hbox.setStretch(1, 1)

        self.treeView = QTreeView()

        self.iconProvider = IconProvider()

        self.treeView.setModel(self.newFileSystemModel())
        self.treeView.setColumnWidth(0, 300)
        mainLayout.addWidget(self.treeView)

        self.packagesPath = os.path.join(
            self.projectPathDict["venvdir"], "Lib", "site-packages")
        if os.path.exists(self.projectPathDict["venvdir"]):
            self.currentVersionLabel.setText(self.setVesionFromVenv())
            self.treeView.setRootIndex(
                self.treeView.model().index(self.packagesPath))

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.installVenvButton = QPushButton("Install")
        self.installVenvButton.clicked.connect(self.install)
        hbox.addWidget(self.installVenvButton)

        self.upgradeVenvButton = QPushButton("Upgrade")
        self.upgradeVenvButton.clicked.connect(self.upgrade)
        hbox.addWidget(self.upgradeVenvButton)

        self.uninstallVenvButton = QPushButton("Uninstall")
        self.uninstallVenvButton.clicked.connect(self.uninstall)
        hbox.addWidget(self.uninstallVenvButton)

    def openVenv(self):
        if os.path.exists(self.projectPathDict["venvdir"]):
            os.startfile(self.projectPathDict["venvdir"])

    def setVesionFromVenv(self):
        path = os.path.join(self.projectPathDict["venvdir"], 'pyvenv.cfg')
        tempList = []
        with open(path, 'r') as file:
            for i in file.readlines():
                v = i.strip()
                if v == '':
                    pass
                else:
                    tempList.append(tuple(v.split(' = ')))
        settings = dict(tempList)
        return settings['version']

    def newFileSystemModel(self):
        fileSystemModel = QFileSystemModel()
        fileSystemModel.setRootPath(QDir.rootPath())
        fileSystemModel.setNameFilterDisables(False)
        fileSystemModel.setIconProvider(self.iconProvider)

        return fileSystemModel

    def install(self):
        if os.path.exists(self.projectPathDict["venvdir"]):
            QMessageBox.information(
                self, "Install", "Virtual environment already installed.")
            return
        reply = QMessageBox.warning(self, "Install",
                                         "This will install a new virtual environment.\n\nProceed?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 0:
                QMessageBox.information(
                    self, "Install", "There is no Python installation to install against.\n\nPlease make sure Python is installed.")
                return
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 1:
                pythonPath = self.useData.SETTINGS["InstalledInterpreters"][0]
            else:
                pythonPath = SelectBox(
                    "Choose Python installation", self.useData.SETTINGS["InstalledInterpreters"], self)
                if pythonPath.accepted:
                    pythonPath = pythonPath.item
                else:
                    return
            try:
                builder = EnvBuilder(pythonPath)
                builder.create(self.projectPathDict["venvdir"])
                self.treeView.setModel(self.newFileSystemModel())
                self.treeView.setRootIndex(
                    self.treeView.model().index(self.packagesPath))
                self.currentVersionLabel.setText(self.setVesionFromVenv())

                QMessageBox.information(
                    self, "Install", "Install virtual environment completed.")
            except Exception as err:
                QMessageBox.warning(
                    self, "Failed Install", str(err))
        else:
            return

    def upgrade(self):
        if not os.path.exists(self.projectPathDict["venvdir"]):
            QMessageBox.information(
                self, "Install", "No virtual environment to upgrade.")
            return
        reply = QMessageBox.warning(self, "Install",
                                         "This will upgrade the current the virtual environment.\n\nProceed?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 0:
                QMessageBox.information(
                    self, "Install", "There is no Python installation to install against.\n\nPlease make sure Python is installed.")
                return
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 1:
                pythonPath = self.useData.SETTINGS["InstalledInterpreters"][0]
            else:
                pythonPath = SelectBox(
                    "Choose Python installation", self.useData.SETTINGS["InstalledInterpreters"], self)
                if pythonPath.accepted:
                    pythonPath = pythonPath.item
                else:
                    return
            try:
                builder = EnvBuilder(pythonPath, upgrade=True)
                builder.create(self.projectPathDict["venvdir"])
                self.treeView.setModel(self.newFileSystemModel())
                self.treeView.setRootIndex(
                    self.treeView.model().index(self.packagesPath))
                self.currentVersionLabel.setText(self.setVesionFromVenv())
                QMessageBox.information(
                    self, "Upgrade", "Upgrade virtual environment completed.")
            except Exception as err:
                QMessageBox.warning(
                    self, "Failed Upgrade", str(err))
        else:
            return

    def uninstall(self):
        if not os.path.exists(self.projectPathDict["venvdir"]):
            QMessageBox.information(
                self, "Uninstall", "No virtual environment to uninstall.")
            return
        reply = QMessageBox.warning(self, "Uninstall",
                                         "This will uninstall the current virtual environment.\n\nProceed?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.treeView.setModel(self.newFileSystemModel())
                if os.path.exists(self.projectPathDict["venvdir"]):
                    shutil.rmtree(self.projectPathDict["venvdir"])
                self.currentVersionLabel.clear()
                QMessageBox.information(
                    self, "Uninstall", "Uninstall virtual environment completed.")
            except Exception as err:
                QMessageBox.warning(
                    self, "Failed Uninstall", str(err))
        else:
            return


class BuildConfig(QWidget):

    def __init__(self, projectPathDict, useData, parent=None):
        QWidget.__init__(self, parent)

        self.projectPathDict = projectPathDict
        self.useData = useData
        
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.lists = {"Includes": [],
                      "Excludes": [],
                      "Constants Modules": [],
                      "Packages": [],
                      "Replace Paths": [],
                      "Bin Includes": [],
                      "Bin Excludes": [],
                      "Bin Path Includes": [],
                      "Bin Path Excludes": [],
                      "Zip Includes": [],
                      "Include Files": [],
                      "Namespace Packages": []}

        self.profileData = self.load()
        
        self.tabWidget = QTabWidget()
        self.tabWidget.setObjectName("buildTab")
        mainLayout.addWidget(self.tabWidget)

        versionWidget = QWidget()
        self.tabWidget.addTab(versionWidget,
                        QIcon(os.path.join("Resources", "images", "arrow-045")),
                            "Version Information")

        versionLayout = QFormLayout()
        versionWidget.setLayout(versionLayout)

        self.itemLine = QLineEdit()
        self.itemLine.setText(self.profileData["name"])
        versionLayout.addRow("Name", self.itemLine)

        self.authorLine = QLineEdit()
        self.authorLine.setText(self.profileData["author"])
        versionLayout.addRow("Author", self.authorLine)

        self.versionLine = QLineEdit()
        self.versionLine.setText(self.profileData["version"])
        versionLayout.addRow("Version", self.versionLine)

        self.descriptionLine = QLineEdit()
        self.descriptionLine.setText(self.profileData["description"])
        versionLayout.addRow("Description", self.descriptionLine)

        self.commentsLine = QLineEdit()
        self.commentsLine.setText(self.profileData["comments"])
        versionLayout.addRow("Comments", self.commentsLine)

        self.companyLine = QLineEdit()
        self.companyLine.setText(self.profileData["company"])
        versionLayout.addRow("Company", self.companyLine)

        self.copyrightLine = QLineEdit()
        self.copyrightLine.setText(self.profileData["copyright"])
        versionLayout.addRow("Copyright", self.copyrightLine)

        self.trademarksLine = QLineEdit()
        versionLayout.addRow("Trademarks", self.trademarksLine)

        self.productLine = QLineEdit()
        self.productLine.setText(self.profileData["product"])
        versionLayout.addRow("Product", self.productLine)

        #-------------------------------------------------------------------

        optionsWidget = QWidget()
        self.tabWidget.addTab(optionsWidget, QIcon(
            os.path.join("Resources", "images", "arrow-045")), "Options")

        optionsLayout = QFormLayout()
        optionsWidget.setLayout(optionsLayout)

        self.optimizeBox = QComboBox()
        self.optimizeBox.addItem("Don't Optimize")
        self.optimizeBox.addItem("Optimize")
        self.optimizeBox.addItem("Optimize (Remove Doc Strings)")
        self.optimizeBox.setCurrentIndex(
            self.optimizeBox.findText(self.profileData["optimize"]))
        optionsLayout.addRow('', self.optimizeBox)

        self.compressBox = QComboBox()
        self.compressBox.addItem("Compress")
        self.compressBox.addItem("Don't Compress")
        optionsLayout.addRow('',  self.compressBox)

        self.copyDepsBox = QComboBox()
        self.copyDepsBox.addItem("Copy Dependencies")
        self.copyDepsBox.addItem("Don't Copy Dependencies")
        self.copyDepsBox.setCurrentIndex(
            self.copyDepsBox.findText(self.profileData["copydeps"]))
        optionsLayout.addRow('', self.copyDepsBox)

        self.appendScriptToExeBox = QComboBox()
        self.appendScriptToExeBox.addItem("Append Script to Exe")
        self.appendScriptToExeBox.addItem("Don't Append Script to Exe")
        self.appendScriptToExeBox.setCurrentIndex(
            self.appendScriptToExeBox.findText(self.profileData["appendscripttoexe"]))
        optionsLayout.addRow('', self.appendScriptToExeBox)

        self.appendScriptToLibraryBox = QComboBox()
        self.appendScriptToLibraryBox.addItem("Append Script to Library")
        self.appendScriptToLibraryBox.addItem("Don't Append Script to Library")
        self.appendScriptToLibraryBox.setCurrentIndex(
            self.appendScriptToLibraryBox.findText(self.profileData["appendscripttolibrary"]))
        optionsLayout.addRow('', self.appendScriptToLibraryBox)

        self.windowTypeBox = QComboBox()
        self.windowTypeBox.addItem("GUI")
        self.windowTypeBox.addItem("Console")
        if self.profileData["base"] == "Win32GUI.exe":
            self.windowTypeBox.setCurrentIndex(0)
        elif self.profileData["base"] == "Console.exe":
            self.windowTypeBox.setCurrentIndex(1)
        optionsLayout.addRow("Window Type", self.windowTypeBox)

        hbox = QHBoxLayout()
        self.iconBox = QComboBox()
        self.updateIconBox()
        f = self.iconBox.findText(self.profileData["icon"])
        if f != -1:
            self.iconBox.setCurrentIndex(f)
        hbox.addWidget(self.iconBox)

        self.addButton = QToolButton()
        self.addButton.setAutoRaise(True)
        self.addButton.setToolTip("Add")
        self.addButton.setIcon(
            QIcon(os.path.join("Resources", "images", "add")))
        self.addButton.clicked.connect(self.addIcon)
        hbox.addWidget(self.addButton)

        self.removeButton = QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setToolTip("Remove")
        self.removeButton.setIcon(
            QIcon(os.path.join("Resources", "images", "minus")))
        self.removeButton.clicked.connect(self.removeIcon)
        hbox.addWidget(self.removeButton)

        optionsLayout.addRow("Icon", hbox)

        #-------------------------------------------------------------------

        advancedWidget = QWidget()
        self.tabWidget.addTab(advancedWidget, QIcon(
            os.path.join("Resources", "images", "arrow-045")), "Advanced")

        advancedLayout = QVBoxLayout()
        advancedWidget.setLayout(advancedLayout)

        self.listSelectorBox = QComboBox()
        for i in self.lists:
            self.listSelectorBox.addItem(i)
        self.listSelectorBox.activated.connect(self.viewList)
        self.listSelectorBox.currentIndexChanged.connect(self.viewList)
        advancedLayout.addWidget(self.listSelectorBox)

        self.listWidget = QListWidget()
        advancedLayout.addWidget(self.listWidget)

        self.helpDict = {
            "Includes": "List of modules to include",
            "Excludes": "List of modules to exclude",
            "Constants Modules": "List of constants to include",
            "Packages": "List of packages to include",
            "Replace Paths": (
                "Replace all the paths in modules found in the given paths "
                "with the given replacement string; each value "
                "is of the form path=replacement_string; path can be * "
                "which means all paths not already specified"),
            "Include Files": "List of files to include",
            "Zip Includes": (
                "Name of file to add to the zip file or a specification of "
                "the form name=arcname which will specify the archive name "
                "to use"),
            "Namespace Packages": "List of packages to include",
            "Bin Includes": (
                "Libraries that need not be included because"
                "they would normally be expected to be found on the target system or"
                "because they are part of a package which requires independent"
                "installation anyway."),
            "Bin Excludes": (
                "File names of libraries which must be included for the"
                "frozen executable to work."),
            "Bin Path Includes": (
                "Paths of directories which contain files that should "
                "be included."),
            "Bin Path Excludes": (
                "Paths of directories which contain files that should not"
                "be included, generally because they contain standard system libraries."),
            }

        hbox = QHBoxLayout()
        advancedLayout.addLayout(hbox)

        self.itemLine = QLineEdit()
        self.itemLine.selectAll()
        self.itemLine.textChanged.connect(self.enableAddButton)
        hbox.addWidget(self.itemLine)

        self.addButton = QPushButton()
        self.addButton.setIcon(
            QIcon(os.path.join("Resources", "images", "add")))
        self.addButton.clicked.connect(self.appendToList)
        hbox.addWidget(self.addButton)

        self.removeButton = QPushButton()
        self.removeButton.setIcon(
            QIcon(os.path.join("Resources", "images", "minus")))
        self.removeButton.clicked.connect(self.removeItem)
        hbox.addWidget(self.removeButton)
        self.enableAddButton()

        self.docLabel = QLabel()
        self.docLabel.setWordWrap(True)
        advancedLayout.addWidget(self.docLabel)

        self.viewList()
        
        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.save)
        hbox.addWidget(self.saveButton)

    def updateIconBox(self):
        self.iconBox.clear()
        for i in os.listdir(self.projectPathDict['iconsdir']):
            path = os.path.join(self.projectPathDict['iconsdir'], i)
            self.iconBox.addItem(QIcon(path), i)

    def enableAddButton(self):
        text = self.itemLine.text().strip()
        if text == '':
            self.addButton.setDisabled(True)
        elif text in self.lists[self.listSelectorBox.currentText()]:
            self.addButton.setDisabled(True)
        else:
            self.addButton.setDisabled(False)

    def viewList(self):
        self.docLabel.setText(self.helpDict[
                              self.listSelectorBox.currentText()])
        self.listWidget.clear()
        for i in self.lists[self.listSelectorBox.currentText()]:
            self.listWidget.addItem(QListWidgetItem(i))

    def updateList(self):
        itemsList = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            itemsList.append(item.text())
        self.lists[self.listSelectorBox.currentText()] = itemsList

    def appendToList(self):
        item = self.itemLine.text()
        self.listWidget.addItem(QListWidgetItem(item))
        self.updateList()
        self.enableAddButton()

    def removeItem(self):
        self.listWidget.takeItem(self.listWidget.currentRow())
        self.updateList()
        self.enableAddButton()

    def addIcon(self):
        if sys.platform == "win32":
            filter = "Icon Files (*.ico)"
        elif sys.platform == "darwin":
            filter = "Icon Files (*.icns)"
        else:
            filter = "Icon Files (*.png)"
        filePath = file_dialog_path(QFileDialog.getOpenFileName(
            self,
            "Select Icon", self.useData.getLastOpenedDir(),
            filter,
        ))
        if filePath:
            destPath = os.path.join(self.projectPathDict['iconsdir'],
                                   os.path.basename(filePath))
            if os.path.exists(destPath):
                reply = QMessageBox.warning(self, "Add Icon",
                                                 "Icon with same name already exists. Replace?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    pass
                else:
                    return
            shutil.copyfile(filePath, destPath)
            self.updateIconBox()
            f = self.iconBox.findText(os.path.basename(filePath))
            if f != -1:
                self.iconBox.setCurrentIndex(f)
            self.useData.saveLastOpenedDir(os.path.dirname(filePath))

    def removeIcon(self):
        currentIcon = self.iconBox.currentText()
        if currentIcon != '':
            path = os.path.join(self.projectPathDict['iconsdir'], currentIcon)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    self.updateIconBox()
                except Exception as err:
                    QMessageBox.warning(
                        self, "Failed Remove", str(err))

    def _scalars_from_ui(self):
        return {
            "name": self.itemLine.text().strip(),
            "author": self.authorLine.text().strip(),
            "version": self.versionLine.text().strip(),
            "comments": self.commentsLine.text().strip(),
            "description": self.descriptionLine.text().strip(),
            "company": self.companyLine.text().strip(),
            "copyright": self.copyrightLine.text().strip(),
            "trademarks": self.trademarksLine.text().strip(),
            "product": self.productLine.text().strip(),
            "base": self.windowTypeBox.currentText(),
            "icon": self.iconBox.currentText(),
            "compress": self.compressBox.currentText(),
            "optimize": self.optimizeBox.currentText(),
            "copydeps": self.copyDepsBox.currentText(),
            "appendscripttoexe": self.appendScriptToExeBox.currentText(),
            "appendscripttolibrary": self.appendScriptToLibraryBox.currentText(),
        }

    def save(self):
        from Extensions.BuildProfile import save as save_build_profile
        build_folder = os.path.dirname(self.projectPathDict["buildprofile"])
        try:
            save_build_profile(build_folder, self._scalars_from_ui(), self.lists)
        except Exception:
            QMessageBox.warning(
                self, "Save Profile", "Saving failed!")

    def load(self):
        from Extensions.BuildProfile import load as load_build_profile
        build_folder = os.path.dirname(self.projectPathDict["buildprofile"])
        data = load_build_profile(build_folder)
        for key in self.lists:
            self.lists[key] = list(data.get(key, []))
        return data


class ConfigureProject(QLabel):

    def __init__(self, projectPathDict, projectSettings, useData, parent=None):
        QLabel.__init__(self, parent)

        self.setBackgroundRole(QPalette.ColorRole.Window)
        self.setAutoFillBackground(True)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.setMinimumSize(500, 350)
        self.pagesList = []

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QLabel("Project Configuration")
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)
        
        hbox.addStretch(1)
        
        self.hideButton = QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.tabWidget = QTabWidget()

        if projectPathDict["type"] == "Desktop Application":
            self.buildConfig = BuildConfig(projectPathDict, useData)
            self.tabWidget.addTab(self.buildConfig,
                                  QIcon(os.path.join("Resources", "images", "build")), "Build")

        self.venvSetup = VenvSetup(projectPathDict, projectSettings, useData)
        self.tabWidget.addTab(self.venvSetup,
                                  QIcon(os.path.join("Resources", "images", "script_grey")), "Virtual Environment")

        self.refactorConfig = RopeConfig(projectPathDict, useData)
        # self.tabWidget.addTab(self.refactorConfig,
                              # QIcon(os.path.join("Resources", "images", "erase"), "Refactor")
#        self.pagesList.append(self.libraries)

        mainLayout.addWidget(self.tabWidget)
