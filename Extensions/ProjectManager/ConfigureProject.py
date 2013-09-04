import os
from PyQt4 import QtCore, QtGui, QtXml


class GetText(QtGui.QDialog):

    def __init__(self, caption, format, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        mainLayout = QtGui.QVBoxLayout()

        mainLayout.addWidget(QtGui.QLabel(format))

        self.nameLine = QtGui.QLineEdit()
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QtGui.QHBoxLayout()

        self.statusLabel = QtGui.QLabel()
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.acceptButton = QtGui.QPushButton("Ok")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel)
        hbox.addWidget(self.cancelButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.resize(400, 20)
        self.enableAcceptButton()

        self.exec_()

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


class RopeConfig(QtGui.QWidget):

    def __init__(self, pathDict, useData, parent=None):
        QtGui.QWidget.__init__(self, parent)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        self.ignoreSyntaxErrorsBox = QtGui.QComboBox()
        self.ignoreSyntaxErrorsBox.addItem("Ignore Syntax Errors")
        self.ignoreSyntaxErrorsBox.addItem("Don't Ignore Syntax Errors")
#        self.ignoreSyntaxErrorsBox.setCurrentIndex(
# self.ignoreSyntaxErrorsBox.findText(profileData["appendscripttolibrary"]))
        mainLayout.addWidget(self.ignoreSyntaxErrorsBox)

        self.ignoreBadImportsBox = QtGui.QComboBox()
        self.ignoreBadImportsBox.addItem("Ignore Bad Imports")
        self.ignoreBadImportsBox.addItem("Don't Ignore Bad Imports")
#        self.ignoreBadImportsBox.setCurrentIndex(
# self.ignoreBadImportsBox.findText(profileData["appendscripttolibrary"]))
        mainLayout.addWidget(self.ignoreBadImportsBox)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addWidget(QtGui.QLabel("Max History Items: "))
        self.maxHistoryBox = QtGui.QSpinBox()
        hbox.addWidget(self.maxHistoryBox)

        frame = QtGui.QFrame()
        frame.setGeometry(1, 1, 1, 2)
        frame.setFrameShape(frame.HLine)
        frame.setFrameShadow(frame.Sunken)
        mainLayout.addWidget(frame)

        self.listSelectorBox = QtGui.QComboBox()
        self.listSelectorBox.addItem("Extensions")
        self.listSelectorBox.addItem("Ignored Resources")
        self.listSelectorBox.addItem("Custom Folders")
#        self.listSelectorBox.activated.connect(self.viewList)
#        self.listSelectorBox.currentIndexChanged.connect(self.viewList)
        mainLayout.addWidget(self.listSelectorBox)

        self.listWidget = QtGui.QListWidget()
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

        self.docLabel = QtGui.QLabel()
        self.docLabel.setWordWrap(True)
        mainLayout.addWidget(self.docLabel)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        mainLayout.addLayout(hbox)

        self.addButton = QtGui.QPushButton()
        self.addButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "add")))
#        self.addButton.clicked.connect(self.appendToList)
        hbox.addWidget(self.addButton)

        self.removeButton = QtGui.QPushButton()
        self.removeButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "minus")))
#        self.removeButton.clicked.connect(self.removeItem)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

    def save(self):
        fileName = self.pathDict["ropeprofile"]

        dom_document = QtXml.QDomDocument("rope_profile")

        main_data = dom_document.createElement("rope")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("ignoresyntaxerrors")
        attrib = dom_document.createTextNode(
            self.ignoreSyntaxErrorsBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("ignorebadimports")
        attrib = dom_document.createTextNode(
            self.ignoreBadImportsBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("maxhistoryitems")
        attrib = dom_document.createTextNode(str(self.maxHistoryBox.value()))
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("Extensions")
        main_data.appendChild(root)

        defExt = ['*.py', '*.pyw']
        for i in defExt:
            tag = dom_document.createElement("item")
            root.appendChild(tag)

            t = dom_document.createTextNode(i)
            tag.appendChild(t)

        root = dom_document.createElement("IgnoredResources")
        main_data.appendChild(root)

        defIgnore = ["*.pyc", "*~", ".ropeproject",
                     ".hg", ".svn", "_svn", ".git", "__pycache__"]
        for i in defIgnore:
            tag = dom_document.createElement("item")
            root.appendChild(tag)

            t = dom_document.createTextNode(i)
            tag.appendChild(t)

        root = dom_document.createElement("CustomFolders")
        main_data.appendChild(root)

        file = open(fileName, "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()


class LibrariesConfig(QtGui.QWidget):

    def __init__(self, pathDict, useData, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.pathDict = pathDict
        self.useData = useData

        self.libraries = {
            "PyQt4": ["PyQt4", "PyQt4.QtGui", "QtGui", "PyQt4.QtCore", "QtCore",
                      "PyQt4.QtScript", "QtScript"],
            "wxPython": ["wxPython", "wx"],
            "numpy": ["numpy"],
            "scipy": ["scipy"],
            "OpenGL": ["OpenGL"],
            "gc": ["gc"]
        }

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        self.listWidget = QtGui.QListWidget()
        for i, v in self.libraries.items():
            item = QtGui.QListWidgetItem(i)
            item.setCheckState(False)
            self.listWidget.addItem(item)
        mainLayout.addWidget(self.listWidget)


class BuildConfig(QtGui.QTabWidget):

    def __init__(self, pathDict, useData, parent=None):
        QtGui.QTabWidget.__init__(self, parent)

        self.pathDict = pathDict
        self.useData = useData

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

        profileData = self.load()

        versionWidget = QtGui.QWidget()
        self.addTab(versionWidget,
                    QtGui.QIcon(
                    os.path.join("Resources", "images", "arrow-045")),
                    "Version Information")

        versionLayout = QtGui.QFormLayout()
        versionLayout.setMargin(0)
        versionWidget.setLayout(versionLayout)

        self.nameLine = QtGui.QLineEdit()
        self.nameLine.setText(profileData["name"])
        versionLayout.addRow("Name", self.nameLine)

        self.authorLine = QtGui.QLineEdit()
        self.authorLine.setText(profileData["author"])
        versionLayout.addRow("Author", self.authorLine)

        self.versionLine = QtGui.QLineEdit()
        self.versionLine.setText(profileData["version"])
        versionLayout.addRow("Version", self.versionLine)

        self.descriptionLine = QtGui.QLineEdit()
        self.descriptionLine.setText(profileData["description"])
        versionLayout.addRow("Description", self.descriptionLine)

        self.commentsLine = QtGui.QLineEdit()
        self.commentsLine.setText(profileData["comments"])
        versionLayout.addRow("Comments", self.commentsLine)

        self.companyLine = QtGui.QLineEdit()
        self.companyLine.setText(profileData["company"])
        versionLayout.addRow("Company", self.companyLine)

        self.copyrightLine = QtGui.QLineEdit()
        self.copyrightLine.setText(profileData["copyright"])
        versionLayout.addRow("Copyright", self.copyrightLine)

        self.trademarksLine = QtGui.QLineEdit()
        versionLayout.addRow("Trademarks", self.trademarksLine)

        self.productLine = QtGui.QLineEdit()
        self.productLine.setText(profileData["product"])
        versionLayout.addRow("Product", self.productLine)

        #-------------------------------------------------------------------

        optionsWidget = QtGui.QWidget()
        self.addTab(optionsWidget, QtGui.QIcon(
            os.path.join("Resources", "images", "arrow-045")), "Options")

        optionsLayout = QtGui.QFormLayout()
        optionsLayout.setMargin(0)
        optionsWidget.setLayout(optionsLayout)

        self.optimizeBox = QtGui.QComboBox()
        self.optimizeBox.addItem("Don't Optimize")
        self.optimizeBox.addItem("Optimize")
        self.optimizeBox.addItem("Optimize (Remove Doc Strings)")
        self.optimizeBox.setCurrentIndex(
            self.optimizeBox.findText(profileData["optimize"]))
        optionsLayout.addRow('', self.optimizeBox)

        self.compressBox = QtGui.QComboBox()
        self.compressBox.addItem("Compress")
        self.compressBox.addItem("Don't Compress")
        optionsLayout.addRow('',  self.compressBox)

        self.copyDepsBox = QtGui.QComboBox()
        self.copyDepsBox.addItem("Copy Dependencies")
        self.copyDepsBox.addItem("Don't Copy Dependencies")
        self.copyDepsBox.setCurrentIndex(
            self.copyDepsBox.findText(profileData["copydeps"]))
        optionsLayout.addRow('', self.copyDepsBox)

        self.appendScriptToExeBox = QtGui.QComboBox()
        self.appendScriptToExeBox.addItem("Append Script to Exe")
        self.appendScriptToExeBox.addItem("Don't Append Script to Exe")
        self.appendScriptToExeBox.setCurrentIndex(
            self.appendScriptToExeBox.findText(profileData["appendscripttoexe"]))
        optionsLayout.addRow('', self.appendScriptToExeBox)

        self.appendScriptToLibraryBox = QtGui.QComboBox()
        self.appendScriptToLibraryBox.addItem("Append Script to Library")
        self.appendScriptToLibraryBox.addItem("Don't Append Script to Library")
        self.appendScriptToLibraryBox.setCurrentIndex(
            self.appendScriptToLibraryBox.findText(profileData["appendscripttolibrary"]))
        optionsLayout.addRow('', self.appendScriptToLibraryBox)

        self.baseBox = QtGui.QComboBox()
        for i in os.listdir(os.path.join("Build", "bases")):
            self.baseBox.addItem(i)
        self.baseBox.setCurrentIndex(
            self.baseBox.findText(profileData["base"]))
        optionsLayout.addRow("Base", self.baseBox)

        self.initScriptBox = QtGui.QComboBox()
        for i in os.listdir(os.path.join("Build", "initscripts")):
            self.initScriptBox.addItem(i)
        self.initScriptBox.setCurrentIndex(
            self.initScriptBox.findText(profileData["initscript"]))
        optionsLayout.addRow("Init Script", self.initScriptBox)

        hbox = QtGui.QHBoxLayout()
        self.iconLine = QtGui.QLineEdit()
        self.iconLine.setText(profileData["icon"])
        hbox.addWidget(self.iconLine)

        self.browseIconButton = QtGui.QPushButton("Browse")
        self.browseIconButton.clicked.connect(self.selectIcon)
        hbox.addWidget(self.browseIconButton)

        optionsLayout.addRow("Icon", hbox)

        #-------------------------------------------------------------------

        advancedWidget = QtGui.QWidget()
        self.addTab(advancedWidget, QtGui.QIcon(
            os.path.join("Resources", "images", "arrow-045")), "Advanced")

        advancedLayout = QtGui.QVBoxLayout()
        advancedLayout.setMargin(0)
        advancedWidget.setLayout(advancedLayout)

        self.listSelectorBox = QtGui.QComboBox()
        for i in self.lists:
            self.listSelectorBox.addItem(i)
        self.listSelectorBox.activated.connect(self.viewList)
        self.listSelectorBox.currentIndexChanged.connect(self.viewList)
        advancedLayout.addWidget(self.listSelectorBox)

        self.listWidget = QtGui.QListWidget()
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

        self.docLabel = QtGui.QLabel()
        self.docLabel.setWordWrap(True)
        advancedLayout.addWidget(self.docLabel)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        advancedLayout.addLayout(hbox)

        self.addButton = QtGui.QPushButton()
        self.addButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "add")))
        self.addButton.clicked.connect(self.appendToList)
        hbox.addWidget(self.addButton)

        self.removeButton = QtGui.QPushButton()
        self.removeButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "minus")))
        self.removeButton.clicked.connect(self.removeItem)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

        self.viewList()

    def viewList(self):
        self.docLabel.setText(self.helpDict[
                              self.listSelectorBox.currentText()])
        self.listWidget.clear()
        for i in self.lists[self.listSelectorBox.currentText()]:
            self.listWidget.addItem(QtGui.QListWidgetItem(i))

    def updateList(self):
        itemsList = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            itemsList.append(item.text())
        self.lists[self.listSelectorBox.currentText()] = itemsList

    def appendToList(self):
        name = GetText("Add", "Item:", self)
        if name.accepted:
            if name.text in self.lists[self.listSelectorBox.currentText()]:
                message = QtGui.QMessageBox.warning(
                    self, "Add", "Item already exists! Choose a different one.")
                self.appendToList()
                return
            self.listWidget.addItem(QtGui.QListWidgetItem(name.text))
            self.updateList()

    def removeItem(self):
        self.listWidget.takeItem(self.listWidget.currentRow())
        self.updateList()

    def selectIcon(self):
        options = QtGui.QFileDialog.Options()
        file = QtGui.QFileDialog.getOpenFileName(self,
                                                 "Select Icon", self.useData.getLastOpenedDir(
                                                 ),
                                                 "Icon Files (*.ico)", options)
        if file:
            file = os.path.normpath(file)
            self.iconLine.setText(file)
            self.useData.saveLastOpenedDir(os.path.dirname(file))

    def save(self):
        fileName = self.pathDict["buildprofile"]

        dom_document = QtXml.QDomDocument("build_profile")

        main_data = dom_document.createElement("build")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("name")
        attrib = dom_document.createTextNode(self.nameLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("author")
        attrib = dom_document.createTextNode(self.authorLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("version")
        attrib = dom_document.createTextNode(self.versionLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("comments")
        attrib = dom_document.createTextNode(self.commentsLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("description")
        attrib = dom_document.createTextNode(
            self.descriptionLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("company")
        attrib = dom_document.createTextNode(self.companyLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copyright")
        attrib = dom_document.createTextNode(self.copyrightLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("trademarks")
        attrib = dom_document.createTextNode(
            self.trademarksLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("product")
        attrib = dom_document.createTextNode(self.productLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("base")
        attrib = dom_document.createTextNode(self.baseBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("icon")
        attrib = dom_document.createTextNode(self.iconLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("compress")
        attrib = dom_document.createTextNode(self.compressBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("optimize")
        attrib = dom_document.createTextNode(self.optimizeBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copydeps")
        attrib = dom_document.createTextNode(self.copyDepsBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttoexe")
        attrib = dom_document.createTextNode(
            self.appendScriptToExeBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttolibrary")
        attrib = dom_document.createTextNode(
            self.appendScriptToLibraryBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("initscript")
        attrib = dom_document.createTextNode(self.initScriptBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        for key, value in self.lists.items():
            root = dom_document.createElement(key.replace(' ', '-'))
            main_data.appendChild(root)
            for i in value:
                tag = dom_document.createElement("item")
                root.appendChild(tag)

                t = dom_document.createTextNode(i)
                tag.appendChild(t)

        try:
            file = open(fileName, "w")
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(dom_document.toString())
            file.close()
        except:
            message = QtGui.QMessageBox.warning(
                self, "Save Profile", "Saving failed!")

    def load(self):
        dom_document = QtXml.QDomDocument()
        file = open(self.pathDict["buildprofile"], "r")
        dom_document.setContent(file.read())
        file.close()

        dataDict = {}

        elements = dom_document.documentElement()
        node = elements.firstChild()
        while node.isNull() is False:
            name = node.nodeName()
            expandedName = name.replace('-', ' ')
            if expandedName in self.lists:
                sub_node = node.firstChild()
                while sub_node.isNull() is False:
                    sub_prop = sub_node.toElement()
                    self.lists[expandedName].append(sub_prop.text())
                    sub_node = sub_node.nextSibling()
                dataDict[expandedName] = self.lists[expandedName]
            else:
                sub_prop = node.toElement()
                dataDict[name] = sub_prop.text()
            node = node.nextSibling()
        return dataDict


class ConfigureProject(QtGui.QLabel):

    def __init__(self, pathDict, useData, parent=None):
        QtGui.QLabel.__init__(self, parent)

        self.setBackgroundRole(QtGui.QPalette.Background)
        self.setAutoFillBackground(True)

        self.setMinimumSize(500, 360)
        self.pagesList = []

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        label = QtGui.QLabel("Project Configuration")
        label.setStyleSheet("font: 14px; color: grey;")
        mainLayout.addWidget(label)

        self.tabWidget = QtGui.QTabWidget()

        if pathDict["type"] == "Desktop Application":
            self.buildConfig = BuildConfig(pathDict, useData)
            self.tabWidget.addTab(self.buildConfig,
                                  QtGui.QIcon(os.path.join("Resources", "images", "build")), "Build")
            self.pagesList.append(self.buildConfig)

        self.libraries = LibrariesConfig(pathDict, useData)
        self.tabWidget.addTab(self.libraries,
                              QtGui.QIcon(os.path.join("Resources", "images", "erase")), "Libraries")
#        self.pagesList.append(self.libraries)

        self.refactorConfig = RopeConfig(pathDict, useData)
        # self.tabWidget.addTab(self.refactorConfig,
                              # QtGui.QIcon(os.path.join("Resources", "images", "erase"), "Refactor")
#        self.pagesList.append(self.libraries)

        mainLayout.addWidget(self.tabWidget)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addWidget(
            QtGui.QLabel("The module 're' must be imported for frozen scripts to work.\nThis is a glitch in cxFreeze."))

        hbox.addStretch(1)

        self.saveButton = QtGui.QPushButton("Save")
        self.saveButton.clicked.connect(self.save)
        hbox.addWidget(self.saveButton)

        self.closeButton = QtGui.QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        hbox.addWidget(self.closeButton)

    def save(self):
        for page in self.pagesList:
            page.save()
