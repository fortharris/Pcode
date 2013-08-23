import os
import ctypes
import shutil
from PyQt4 import QtGui, QtCore, QtXml


class GetName(QtGui.QDialog):

    def __init__(self, caption, path, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        self.path = path

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(QtGui.QLabel("Name:"))

        self.nameLine = QtGui.QLineEdit()
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

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

        self.resize(300, 20)
        self.enableAcceptButton()

        self.exec_()

    def enableAcceptButton(self):
        text = self.nameLine.text().strip()
        if text == '':
            self.acceptButton.setDisabled(True)
        else:
            preExistNames = os.listdir(self.path)
            if text in preExistNames:
                self.statusLabel.setText("Unavailable")
                self.acceptButton.setDisabled(True)
            else:
                self.statusLabel.setText("Available")
                self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.text = self.nameLine.text().strip()
        self.close()

    def cancel(self):
        self.accepted = False
        self.close()


class IconProvider(QtGui.QFileIconProvider):

    def __init__(self, parent=None):
        QtGui.QFileIconProvider.__init__(self)

    def icon(self, icontype_or_qfileinfo):
        """Reimplement Qt method"""
        if isinstance(icontype_or_qfileinfo, QtGui.QFileIconProvider.IconType):
            return super(IconProvider, self).icon(icontype_or_qfileinfo)
        else:
            qfileinfo = icontype_or_qfileinfo
            fname = os.path.normpath(qfileinfo.absoluteFilePath())
            if os.path.isdir(fname):
                dir = QtCore.QDir(fname)
                dirList = dir.entryList(QtCore.QDir.Files)
                if "__init__.py" in dirList:
                    icon = QtGui.QIcon(
                        os.path.join("Resources", "images", "box"))
                else:
                    icon = QtGui.QIcon(
                        os.path.join("Resources", "images", "folder-horizontal"))
                return icon
            else:
                if os.path.basename(fname) == "__init__.py":
                    return QtGui.QIcon(os.path.join("Resources", "images", "haiku-wide"))
                ext = os.path.splitext(fname)[1][1:]
                if ext == "py" or ext == "pyw":
                    return QtGui.QIcon(os.path.join("Resources", "images", "gear"))
                else:
                    return super(IconProvider, self).icon(qfileinfo)


class ProjectTree(QtGui.QTreeView):

    fileActivated = QtCore.pyqtSignal(str)

    def __init__(self, editorTabWidget, root, app, parent):
        QtGui.QTreeView.__init__(self, parent)

        self.root = root
        self.app = app
        self.editorTabWidget = editorTabWidget
        self.refactor = editorTabWidget.refactor
        self.parent = parent
        self.pathDict = self.editorTabWidget.pathDict

        self.setAcceptDrops(True)
        self.setAnimated(True)
        self.setAutoScroll(True)
        self.activated.connect(self.treeItemActivated)

        iconProvider = IconProvider()

        self.fileSystemModel = QtGui.QFileSystemModel()
        self.fileSystemModel.setRootPath(QtCore.QDir.rootPath())
        self.fileSystemModel.setNameFilters(['*.py', '*.pyw'])
        self.fileSystemModel.setNameFilterDisables(False)
        self.fileSystemModel.setIconProvider(iconProvider)
        self.setModel(self.fileSystemModel)
        self.setColumnWidth(0, 300)

        self.createActions()
        self.loadShortcut(self.root)

    def contextMenuEvent(self, event):
        indexList = self.selectedIndexes()
        selection = len(indexList) != 0

        self.contextMenu = QtGui.QMenu()
        self.newMenu = self.contextMenu.addMenu("New...")
        self.newMenu.addAction(self.addFileAct)
        self.newMenu.addAction(self.addDirAct)
        self.newMenu.addAction(self.addPackageAct)
        self.contextMenu.addAction(self.addExistingItems)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.disableFilterAct)
        self.contextMenu.addAction(self.expandAllAct)
        self.contextMenu.addAction(self.collapseAllAct)
        self.contextMenu.addSeparator()

        if selection:
            self.contextMenu.addAction(self.copyAct)
            self.contextMenu.addAction(self.pasteAct)
            self.contextMenu.addAction(self.deleteAct)

        dir = self.getCurrentDirectory()
        if '__init__.py' not in os.listdir(dir):
            self.contextMenu.addSeparator()
            self.contextMenu.addAction(self.convertToPackageAct)

        if selection:
            path_index = indexList[0]
            if self.fileSystemModel.isDir(path_index):
                pass
            else:
                path = \
                    os.path.normpath(self.fileSystemModel.filePath(path_index))
                if path.endswith((".py", ".pyw")):
                    self.contextMenu.addSeparator()
                    self.contextMenu.addAction(self.mainScriptsAct)

        self.contextMenu.exec_(event.globalPos())

    def createActions(self):
        self.addFileAct = QtGui.QAction(
            "File", self,
            statusTip="File", triggered=self.newFile)

        self.addDirAct = QtGui.QAction(
            "Directory", self,
            statusTip="Directory", triggered=self.newDirectory)

        self.addPackageAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "box")),
            "Package", self,
            statusTip="Package", triggered=self.newPackage)

        self.copyAct = QtGui.QAction(
            "Copy", self, shortcut=QtGui.QKeySequence.Copy,
            statusTip="Copy", triggered=self.copyItem)

        self.pasteAct = QtGui.QAction(
            "Paste", self, shortcut=QtGui.QKeySequence.Paste,
            statusTip="Paste", triggered=self.pasteItem)

        self.deleteAct = QtGui.QAction(
            "Delete", self, shortcut=QtGui.QKeySequence.Delete,
            statusTip="Delete Selection", triggered=self.deleteItem)

        self.convertToPackageAct = QtGui.QAction("Convert to Package", self,
                                                 statusTip="Convert to Package", triggered=self.dirToPackage)

        self.addExistingItems = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "login")),
                "Add Existing items", self,
                statusTip="Add Existing items", triggered=self.addExistingItems)

        self.mainScriptsAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "location")),
            "Set as Main Script", self, statusTip="Set as Main Script",
            triggered=self.setMainScript)

        self.collapseAllAct = \
            QtGui.QAction(
                "Collapse All", self,
                statusTip="Collapse Tree", triggered=self.collapseAll)

        self.expandAllAct = \
            QtGui.QAction(
                "Expand All", self,
                statusTip="Expand Tree", triggered=self.expandAll)

        self.disableFilterAct = \
            QtGui.QAction(
                "Disable Filter", self, statusTip="Disable Filter",
                triggered=self.disableFilter)
        self.disableFilterAct.setCheckable(True)

    def getCurrentFilePath(self):
        indexList = self.selectedIndexes()
        path_index = indexList[0]
        path = \
            os.path.normpath(self.fileSystemModel.filePath(path_index))
        return path

    def getCurrentDirectory(self):
        indexList = self.selectedIndexes()
        if len(indexList) == 0:
            path = self.root
        else:
            path_index = indexList[0]
            if self.fileSystemModel.isDir(path_index):
                pass
            else:
                path_index = path_index.parent()
            path = \
                os.path.normpath(self.fileSystemModel.filePath(path_index))
        return path

    def copyItem(self):
        path = self.getCurrentFilePath()
        url = QtCore.QUrl.fromLocalFile(path)
        data = QtCore.QMimeData()
        data.setUrls([url])

        cb = self.app.clipboard()
        cb.setMimeData(data)

    def pasteItem(self):
        destDir = self.getCurrentDirectory()
        cb = self.app.clipboard()
        mimeData = cb.mimeData()
        if mimeData.hasUrls():
            urls = mimeData.urls()
            for url in urls:
                path = url.toLocalFile()
                dest = os.path.join(destDir, os.path.basename(path))
                if os.path.exists(dest):
                    reply = QtGui.QMessageBox.warning(self, "Paste",
                                                      "'" + os.path.basename(
                                                          dest) + "' already exists in the destination directory.\n\nWould you like to replace it?",
                                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        if os.path.isdir(dest):
                            shutil.rmtree(dest)
                    else:
                        return
                try:
                    if os.path.isdir(path):
                        shutil.copytree(path, dest)
                    else:
                        shutil.copyfile(path, dest)
                except Exception as err:
                    message = QtGui.QMessageBox.warning(
                        self, "Paste", str(err))

    def dirToPackage(self):
        path = self.getCurrentDirectory()
        file = open(os.path.join(path, "__init__.py"), 'w')
        file.close()

    def newFile(self):
        path = self.getCurrentDirectory()
        fileName = GetName("New File", path, self)
        if fileName.accepted:
            path = os.path.join(path, fileName.text)
            try:
                file = open(path, 'w')
                file.close()
                self.editorTabWidget.loadfile(path)
            except:
                message = QtGui.QMessageBox.warning(self, "New File",
                                                    "File creation failed!")

    def newDirectory(self):
        path = self.getCurrentDirectory()
        dirName = GetName("New Directory", path, self)
        if dirName.accepted:
            path = os.path.join(path, dirName.text)
            try:
                os.mkdir(path)
            except:
                message = QtGui.QMessageBox.warning(self, "New Directory",
                                                    "Directory creation failed!")

    def newPackage(self):
        path = self.getCurrentDirectory()
        packageName = GetName("New Package", path, self)
        if packageName.accepted:
            path = os.path.join(path, packageName.text)
            try:
                os.mkdir(path)
                f = os.path.join(path, "__init__.py")
                file = open(f, "w")
                file.close()
            except:
                message = QtGui.QMessageBox.warning(self, "New Package",
                                                    "Directory creation failed!")

    def addExistingItems(self):
        options = QtGui.QFileDialog.Options()
        files = QtGui.QFileDialog.getOpenFileNames(self,
                                                   "Select Items", QtCore.QDir.homePath(), "All Files (*);", options)
        if files:
            dest = self.getCurrentDirectory()
            try:
                for path in files:
                    shutil.copyfile(path, os.path.join(
                        dest, os.path.basename(path)))
            except Exception as err:
                message = QtGui.QMessageBox.warning(
                    self, "Add Existing Items", "Failed to copy some items!\n\n" + str(err))

    def deleteItem(self):
        path = self.getCurrentFilePath()
        reply = QtGui.QMessageBox.warning(self, "Delete",
                                          "Permanently delete '" + os.path.basename(
                                              path) + "' from the project?",
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as err:
                message = QtGui.QMessageBox.warning(self, "Delete",
                                                    "Failed to delete item!\n\n" + str(err))
        else:
            return

    def loadShortcut(self, path):
        if os.path.exists(path):
            self.setRootIndex(self.fileSystemModel.index(path))
        else:
            message = QtGui.QMessageBox.warning(self, "Open",
                                                "Directory not found!")

    def disableFilter(self):
        if self.disableFilterAct.isChecked():
            self.fileSystemModel.setNameFilters([])
        else:
            self.fileSystemModel.setNameFilters(['*.py', '*.pyw'])

    def treeItemActivated(self, modelIndex):
        if self.fileSystemModel.isDir(modelIndex) is False:
            path = self.getCurrentFilePath()
            self.parent.fileActivated.emit(path)
        else:
            if self.isExpanded(modelIndex):
                self.collapse(modelIndex)
            else:
                self.expand(modelIndex)

    def openExternal(self):
        path = self.getCurrentDirectory()
        ctypes.windll.shell32.ShellExecuteW(None, 'open', 'explorer.exe',
                                            '/n,/select, ' + path, None, 1)

    def setMainScript(self):
        fileName = self.getCurrentFilePath()
        self.pathDict["mainscript"] = fileName

        dom_document = QtXml.QDomDocument()
        file = open(self.pathDict["projectmainfile"], "r")
        x = dom_document.setContent(file.read())
        file.close()

        elements = dom_document.documentElement()
        node = elements.firstChild()

        settingsDict = {}
        while node.isNull() is False:
            tag = node.toElement()

            settingsDict["Type"] = tag.attribute("Type")
            settingsDict["Name"] = tag.attribute("Name")
            settingsDict["MainScript"] = tag.attribute("MainScript")
            settingsDict["Version"] = tag.attribute("Version")

            node = node.nextSibling()

        settingsDict["MainScript"] = fileName

        # save data
        dom_document = QtXml.QDomDocument("Project")
        properties = dom_document.createElement("properties")
        dom_document.appendChild(properties)

        tag = dom_document.createElement("pcode_project")
        for key, value in settingsDict.items():
            tag.setAttribute(key, value)
        properties.appendChild(tag)

        file = open(self.pathDict["projectmainfile"], "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()


class SearchThread(QtCore.QThread):

    foundList = QtCore.pyqtSignal(dict)

    def run(self):
        resultsDict = {}
        for file in self.pycore.get_python_files():
            path = file.path
            folder = os.path.normpath(os.path.dirname(path))
            name = file.name
            if name.startswith(self.searchName):
                if folder in resultsDict:
                    resultsDict[folder].append(name)
                else:
                    resultsDict[folder] = [name]
        self.foundList.emit(resultsDict)

    def search(self, searchName, pycore):
        self.pycore = pycore
        self.searchName = searchName
        self.start()


class ProjectViewer(QtGui.QWidget):

    fileActivated = QtCore.pyqtSignal(str)

    def __init__(self, editorTabWidget, root, app, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.refactor = editorTabWidget.refactor
        self.root = root

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 5)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.viewStack = QtGui.QStackedWidget()
        mainLayout.addWidget(self.viewStack)

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.performSearch)

        self.searchLine = QtGui.QLineEdit()
        self.searchLine.setPlaceholderText("Search")
        self.searchLine.textChanged.connect(self.timer.start)
        mainLayout.addWidget(self.searchLine)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(1)
        hbox.addStretch(1)
        self.searchLine.setLayout(hbox)

        self.clearButton = QtGui.QToolButton()
        self.clearButton.setAutoRaise(True)
        self.clearButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "disabled")))
        self.clearButton.clicked.connect(self.clearSearch)
        hbox.addWidget(self.clearButton)

        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setMaximumHeight(2)
        self.progressBar.setStyleSheet(
            """

                  QProgressBar {
                     border: None;
                     text-align: center;
                     padding: 0px;
                     border-radius: 0px;
                     background-color: Transparent;
                 }

                 QProgressBar::chunk {
                      color: black;
                      border-radius: 0px;
                      background-color: #6570EA;
                 }

            """
        )
        self.progressBar.setRange(0, 0)
        mainLayout.addWidget(self.progressBar)
        self.progressBar.hide()

        self.projectTree = ProjectTree(editorTabWidget, root, app, self)
        self.viewStack.addWidget(self.projectTree)

        self.searchResultsTree = QtGui.QTreeWidget(self)
        self.searchResultsTree.setHeaderItem(
            QtGui.QTreeWidgetItem(["Search Results:"]))
        self.searchResultsTree.activated.connect(self.loadFile)
        self.viewStack.addWidget(self.searchResultsTree)

        self.searchThread = SearchThread()
        self.searchThread.foundList.connect(self.updateSearch)

    def loadFile(self, item):
        item = self.searchResultsTree.selectedItems()[0]
        if item.parent() is None:
            pass
        else:
            dir = item.parent().text(0)
            path = os.path.join(self.root, os.path.join(dir, item.text(0)))
            self.fileActivated.emit(path)

    def clearSearch(self):
        self.searchLine.clear()
        self.viewStack.setCurrentIndex(0)

    def performSearch(self):
        text = self.searchLine.text().strip()
        if text == '':
            self.viewStack.setCurrentIndex(0)
            return
        pycore = self.refactor.ropeProject.pycore
        self.searchThread.search(text, pycore)
        self.progressBar.show()

    def updateSearch(self, resultsDict):
        self.progressBar.hide()
        self.searchResultsTree.clear()
        self.viewStack.setCurrentIndex(1)
        if len(resultsDict) > 0:
            for folder, fileList in resultsDict.items():
                parentItem = QtGui.QTreeWidgetItem()
                parentItem.setText(0, folder)
                parentItem.setForeground(0, QtGui.QBrush(
                    QtGui.QColor("#003366")))
                for i in fileList:
                    child = QtGui.QTreeWidgetItem()
                    child.setText(0, i)
                    parentItem.addChild(child)
                self.searchResultsTree.addTopLevelItem(parentItem)
                parentItem.setExpanded(True)
        else:
            parentItem = QtGui.QTreeWidgetItem()
            item = QtGui.QTreeWidgetItem()
            item.setText(0, "<No results found>")
            item.setFlags(QtCore.Qt.NoItemFlags)
            parentItem.addChild(item)
            self.searchResultsTree.addTopLevelItem(parentItem)
            parentItem.setExpanded(True)
