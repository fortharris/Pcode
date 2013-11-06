import os
import ctypes
import shutil
from PyQt4 import QtGui, QtCore, QtXml

from Extensions import Global
from Extensions.Projects.ProjectManager.ProjectView.ProgressWidget import ProgressWidget


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


class CopyThread(QtCore.QThread):

    currentJobChanged = QtCore.pyqtSignal(str)
    copyingSizeChanged = QtCore.pyqtSignal(int)

    def run(self):
        try:
            for path in self.itemList:
                if self.stopThread is False:
                    destPath = os.path.join(
                        self.destDir, os.path.basename(path))
                    if os.path.isfile(path):
                        self.copyFile(path, destPath)
                    else:
                        self.copyDir(path, destPath)
                else:
                    break
        except Exception as err:
            self.errors = str(err)

    def copyDir(self, sourceDir, destDir):
        if not os.path.exists(destDir):
            os.mkdir(destDir)

        for i in os.listdir(sourceDir):
            path = os.path.join(sourceDir, i)
            if os.path.isfile(path):
                self.copyFile(path, os.path.join(destDir, i))
            else:
                self.copyDir(path, os.path.join(destDir, i))

    def copyFile(self, source, dest):
        self.currentJobChanged.emit(os.path.basename(source))
        sourceFile = open(source, 'rb')
        destFile = open(dest, 'wb')
        while True:
            if self.stopThread is not False:
                sourceFile.close()
                destFile.close()
                os.remove(dest)
                return
            chunk = sourceFile.read(1024)
            if len(chunk) == 0:
                sourceFile.close()
                destFile.close()
                break
            destFile.write(chunk)
            self.totalChunkCopied += len(chunk)

            value = self.totalChunkCopied * 100 / self.totalSize
            self.copyingSizeChanged.emit(value)

    def getTotalSize(self, itemList):
        # calculate size of items in the list
        totalSize = 0
        for item in itemList:
            if os.path.isfile(item):
                try:
                    size = os.path.getsize(item)
                    totalSize += size
                except:
                    pass
            else:
                for root, dirs, files in os.walk(item):
                    for i in files:
                        try:
                            size = os.path.getsize(os.path.join(root, i))
                            totalSize += size
                        except:
                            pass
        return totalSize

    def copy(self, itemList, destDir):
        self.itemList = itemList
        self.destDir = destDir

        self.totalChunkCopied = 0
        self.totalSize = self.getTotalSize(itemList)
        self.stopThread = False
        self.errors = None

        self.start()

    def stop(self):
        self.stopThread = True


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

    def __init__(self, editorTabWidget, root, app, projectSettings, progressWidget, parent):
        QtGui.QTreeView.__init__(self, parent)

        self.root = root
        self.app = app
        self.editorTabWidget = editorTabWidget
        self.refactor = editorTabWidget.refactor
        self.parent = parent
        self.progressWidget = progressWidget
        self.projectSettings = projectSettings
        self.projectPathDict = self.editorTabWidget.projectPathDict

        self.setObjectName("sidebarItem")

        self.setAcceptDrops(True)
        self.setAnimated(True)
        self.setAutoScroll(True)
        self.activated.connect(self.treeItemActivated)

        self.copyThread = CopyThread()
        self.copyThread.copyingSizeChanged.connect(self.updateCopySize)
        self.copyThread.currentJobChanged.connect(self.updateCurrentJob)
        self.copyThread.finished.connect(self.copyFinished)

        self.progressWidget.cancelButton.clicked.connect(
            self.copyThread.stop)

        iconProvider = IconProvider()

        self.fileSystemModel = QtGui.QFileSystemModel()
        self.fileSystemModel.setRootPath(QtCore.QDir.rootPath())
        self.fileSystemModel.setNameFilterDisables(False)
        self.fileSystemModel.setIconProvider(iconProvider)
        self.setModel(self.fileSystemModel)
        self.setColumnWidth(0, 300)

        self.createActions()
        self.loadShortcut(self.root)

        if self.projectSettings["ShowAllFiles"] == 'False':
            self.fileSystemModel.setNameFilters(['*.py', '*.pyw'])
        self.showAllFilesAct.setChecked(
            self.projectSettings["ShowAllFiles"] == 'True')

    def contextMenuEvent(self, event):
        indexList = self.selectedIndexes()
        selection = len(indexList) != 0

        self.contextMenu = QtGui.QMenu()
        self.newMenu = self.contextMenu.addMenu("New...")
        self.newMenu.addAction(self.addFileAct)
        self.newMenu.addAction(self.addDirAct)
        self.newMenu.addAction(self.addPackageAct)
        self.addExistingMenu = self.contextMenu.addMenu("Add Existing...")
        self.addExistingMenu.addAction(self.addExistingFilesAct)
        self.addExistingMenu.addAction(self.addExistingDirectoriesAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.showAllFilesAct)
        self.contextMenu.addAction(self.collapseAllAct)
        self.contextMenu.addAction(self.expandAllAct)
        self.contextMenu.addSeparator()

        if selection:
            self.contextMenu.addAction(self.copyAct)
            self.contextMenu.addAction(self.pasteAct)
            self.contextMenu.addAction(self.deleteAct)

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

        self.addExistingFilesAct = \
            QtGui.QAction(
                "Files", self,
                statusTip="Files", triggered=self.addExistingFiles)

        self.addExistingDirectoriesAct = \
            QtGui.QAction(
                "Directory", self,
                statusTip="Directory", triggered=self.addExistingDirectory)

        self.mainScriptsAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "location")),
            "Set as Main Script", self, statusTip="Set as Main Script",
            triggered=self.setMainScript)

        self.collapseAllAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "collapse")),
                "Collapse All", self,
                statusTip="Collapse Tree", triggered=self.collapseAll)

        self.expandAllAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "expand")),
                "Expand All", self,
                statusTip="Expand Tree", triggered=self.expandAll)

        self.showAllFilesAct = \
            QtGui.QAction(
                "Show All Files", self, statusTip="Show All Files",
                triggered=self.showAllFiles)
        self.showAllFilesAct.setCheckable(True)
        self.showAllFilesAct.setChecked(True)

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

        clipboard = self.app.clipboard()
        clipboard.setMimeData(data)

    def pasteItem(self):
        destDir = self.getCurrentDirectory()
        clipboard = self.app.clipboard()
        mimeData = clipboard.mimeData()
        if mimeData.hasUrls():
            urls = mimeData.urls()
            pathList = []
            for url in urls:
                path = url.toLocalFile()
                dest = os.path.join(destDir, os.path.basename(path))
                if os.path.exists(dest):
                    reply = QtGui.QMessageBox.warning(self, "Paste",
                                                      "'" + os.path.basename(
                                                          dest) + "' already exists in the destination directory.\n\nWould you like to replace it?",
                                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        pass
                    else:
                        continue
                pathList.append(path)
            self.copyThread.copy(pathList, destDir)
            self.progressWidget.showBusy(True, "Preparing to copy...")

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
                                                    "Failed to create directory!")

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
                self.editorTabWidget.loadfile(f)
            except:
                message = QtGui.QMessageBox.warning(self, "New Package",
                                                    "Package creation failed!")

    def addExistingFiles(self):
        options = QtGui.QFileDialog.Options()
        files = QtGui.QFileDialog.getOpenFileNames(self,
                                                  "Select Files", QtCore.QDir.homePath(
                                                  ),
            "All Files (*);;Text Files (*.txt)", options)
        if files:
            destDir = self.getCurrentDirectory()
            pathList = []
            for file in files:
                destPathName = os.path.join(destDir, os.path.basename(file))
                if os.path.exists(destPathName):
                    reply = QtGui.QMessageBox.warning(
                        self, "Add Existing Files",
                        "'" + os.path.basename(
                            destPathName) + "' already exists in the destination directory.\n\nWould you like to replace it?",
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        pass
                    else:
                        continue
                pathList.append(file)
            self.copyThread.copy(pathList, destDir)
            self.progressWidget.showBusy(True, "Preparing to copy...")

    def addExistingDirectory(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                          "Select Directory", QtCore.QDir.homePath(
                                                          ), options)
        if directory:
            destDir = self.getCurrentDirectory()
            destPathName = os.path.join(destDir, os.path.basename(directory))
            if os.path.exists(destPathName):
                reply = QtGui.QMessageBox.warning(
                    self, "Add Existing Directory",
                                                  "'" + os.path.basename(
                                                      destPathName) + "' already exists in the destination directory.\n\nWould you like to replace it?",
                                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    pass
                else:
                    return
            self.copyThread.copy([directory], destDir)
            self.progressWidget.showBusy(True, "Preparing to copy...")

    def updateCopySize(self, value):
        self.progressWidget.updateValue(value)

    def updateCurrentJob(self, job):
        self.progressWidget.updateCurrentJob(job)

    def copyFinished(self):
        self.progressWidget.showBusy(False)
        if self.copyThread.errors is not None:
            message = QtGui.QMessageBox.warning(
                    self, "Add Existing Items", "Failed to complete copy!\n\n" + str(self.copyThread.errors))

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

    def showAllFiles(self):
        checked = self.showAllFilesAct.isChecked()
        self.projectSettings["ShowAllFiles"] = str(checked)
        if checked:
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
        self.projectPathDict["mainscript"] = fileName

        dom_document = QtXml.QDomDocument()
        file = open(self.projectPathDict["projectmainfile"], "r")
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

        file = open(self.projectPathDict["projectmainfile"], "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()


class SearchThread(QtCore.QThread):

    foundList = QtCore.pyqtSignal(dict)

    def run(self):
        resultsDict = {}

        for root, dirs, files in os.walk(self.projectDir):
            for i in files:
                if not self.filterDisabled:
                    if not i.endswith('.py') or i.endswith('.pyw'):
                        continue

                if i.startswith(self.searchName):
                    if root in resultsDict:
                        resultsDict[root].append(i)
                    else:
                        resultsDict[root] = [i]
        self.foundList.emit(resultsDict)

    def search(self, searchItem, projectDir, filterEnabled):
        self.projectDir = projectDir
        self.searchName = searchItem
        self.filterDisabled = filterEnabled

        self.start()


class LineEdit(QtGui.QLineEdit):

    fileActivated = QtCore.pyqtSignal(str)

    def __init__(self, viewStack, searchResultsTree, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.searchResultsTree = searchResultsTree
        self.viewStack = viewStack

        self.setPlaceholderText("Search")

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(1)
        hbox.addStretch(1)
        self.setLayout(hbox)

        self.clearButton = QtGui.QToolButton()
        self.clearButton.setAutoRaise(True)
        self.clearButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "disabled")))
        self.clearButton.clicked.connect(self.clearSearch)
        hbox.addWidget(self.clearButton)

    def keyPressEvent(self, event):
        key = event.key()

        ctrl = event.modifiers() & QtCore.Qt.ControlModifier
        alt = event.modifiers() & QtCore.Qt.AltModifier
        shift_down = event.modifiers() & QtCore.Qt.ShiftModifier

        if ctrl:
            pass
        elif alt:
            pass
        elif key == QtCore.Qt.Key_Up:
            currentItem = self.currentItem()
            if currentItem is not None:
                itemAbove = self.searchResultsTree.itemAbove(currentItem)
                if itemAbove is None:
                    return
                self.searchResultsTree.setCurrentItem(itemAbove)
                self.setFocus(True)
        elif key == QtCore.Qt.Key_Down:
            currentItem = self.currentItem()
            if currentItem is not None:
                itemBelow = self.searchResultsTree.itemBelow(currentItem)
                if itemBelow is None:
                    return
                self.searchResultsTree.setCurrentItem(itemBelow)
                self.setFocus(True)
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)

    def clearSearch(self):
        self.clear()
        self.viewStack.setCurrentIndex(0)

    def currentItem(self):
        if self.searchResultsTree.topLevelItemCount() > 0:
            item = self.searchResultsTree.selectedItems()[0]
            return item
        else:
            return None


class ProjectView(QtGui.QWidget):

    fileActivated = QtCore.pyqtSignal(str)

    def __init__(self, editorTabWidget, root, app, projectSettings, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.refactor = editorTabWidget.refactor
        self.root = root

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 2, 2)
        self.setLayout(mainLayout)

        self.progressWidget = ProgressWidget()
        mainLayout.addWidget(self.progressWidget)
        self.progressWidget.hide()

        self.viewStack = QtGui.QStackedWidget()
        mainLayout.addWidget(self.viewStack)

        self.projectTree = ProjectTree(
            editorTabWidget, root, app, projectSettings, self.progressWidget, self)
        self.viewStack.addWidget(self.projectTree)

        self.searchResultsTree = QtGui.QTreeWidget(self)
        self.searchResultsTree.setObjectName("sidebarItem")
        self.searchResultsTree.setHeaderItem(
            QtGui.QTreeWidgetItem(["Search Results:"]))
        self.searchResultsTree.activated.connect(self.loadFile)
        self.viewStack.addWidget(self.searchResultsTree)

        self.searchThread = SearchThread()
        self.searchThread.foundList.connect(self.updateSearchTree)

        self.searchTimer = QtCore.QTimer()
        self.searchTimer.setSingleShot(True)
        self.searchTimer.timeout.connect(self.search)
        
        vbox = QtGui.QVBoxLayout()
        vbox.setSpacing(0)
        mainLayout.addLayout(vbox)

        self.searchLine = LineEdit(self.viewStack, self.searchResultsTree)
        self.searchLine.textChanged.connect(self.startSearchTimer)
        self.searchLine.returnPressed.connect(self.loadFile)
        vbox.addWidget(self.searchLine)

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
                                      background-color: #65B0EA;
                                 }

                                """
            )
        self.progressBar.setRange(0, 0)
        vbox.addWidget(self.progressBar)
        self.progressBar.hide()
        
    def startSearchTimer(self):
        self.searchTimer.start(300)

    def loadFile(self):
        if len(self.searchResultsTree.selectedItems()) > 0:
            item = self.searchResultsTree.selectedItems()[0]
            if item.parent() is None:
                pass
            else:
                parentDir = item.parent().text(0)
                path = os.path.join(self.root, parentDir, item.text(0))
                self.fileActivated.emit(path)

    def search(self):
        text = self.searchLine.text().strip()
        if text == '':
            self.viewStack.setCurrentIndex(0)
            return
        self.searchThread.search(text, self.refactor.root,
                                self.projectTree.showAllFilesAct.isChecked())
        self.progressBar.show()

    def updateSearchTree(self, resultsDict):
        self.progressBar.hide()
        self.searchResultsTree.clear()
        self.viewStack.setCurrentIndex(1)
        if len(resultsDict) > 0:
            for folder, fileList in resultsDict.items():
                folderItem = QtGui.QTreeWidgetItem(self.searchResultsTree)
                pathRelativeToProject = folder.partition(
                    self.root + os.path.sep)[-1]
                folderItem.setText(0, pathRelativeToProject)
                folderItem.setForeground(0, QtGui.QBrush(
                    QtGui.QColor("#003366")))
                for i in fileList:
                    fileItem = QtGui.QTreeWidgetItem(folderItem)
                    icon = Global.iconFromPath(os.path.join(folder, i))
                    fileItem.setText(0, i)
                    fileItem.setIcon(0, QtGui.QIcon(icon))
                folderItem.setExpanded(True)

            item = self.searchResultsTree.topLevelItem(0)
            self.searchResultsTree.setCurrentItem(item.child(0))
        else:
            folderItem = QtGui.QTreeWidgetItem()
            item = QtGui.QTreeWidgetItem()
            item.setText(0, "<No results found>")
            item.setFlags(QtCore.Qt.NoItemFlags)
            folderItem.addChild(item)
            self.searchResultsTree.addTopLevelItem(folderItem)
            folderItem.setExpanded(True)
