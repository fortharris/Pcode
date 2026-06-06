import os
import ctypes
import shutil
from Extensions.settings_utils import to_bool

from Extensions import Global
from Extensions.file_dialog_utils import file_dialog_path, file_dialog_paths
from Extensions.Projects.ProjectManager.ProjectView.ProgressWidget import ProgressWidget
from PyQt6.QtCore import QDir, QMimeData, Qt, QThread, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QColor, QFileSystemModel, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QFileIconProvider, QHBoxLayout, QLabel,
    QLineEdit, QMenu, QMessageBox, QProgressBar, QPushButton, QStackedWidget,
    QToolButton, QTreeView, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)
from PyQt6.QtXml import QDomDocument


class GetName(QDialog):

    def __init__(self, caption, path, parent=None):
        QDialog.__init__(self, parent, Qt.WindowType.Window |
                               Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        self.path = path

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(QLabel("Name:"))

        self.nameLine = QLineEdit()
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

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

        self.resize(300, 20)
        self.enableAcceptButton()

        self.exec()

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


class CopyThread(QThread):

    currentJobChanged = pyqtSignal(str)
    copyingSizeChanged = pyqtSignal(int)

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
        cancelled = False
        with open(source, 'rb') as sourceFile, open(dest, 'wb') as destFile:
            while True:
                if self.stopThread is not False:
                    cancelled = True
                    break
                chunk = sourceFile.read(1024)
                if len(chunk) == 0:
                    break
                destFile.write(chunk)
                self.totalChunkCopied += len(chunk)

                value = self.totalChunkCopied * 100 / self.totalSize
                self.copyingSizeChanged.emit(value)
        if cancelled:
            os.remove(dest)

    def getTotalSize(self, itemList):
        # calculate size of items in the list
        totalSize = 0
        for item in itemList:
            if os.path.isfile(item):
                try:
                    size = os.path.getsize(item)
                    totalSize += size
                except Exception:
                    pass
            else:
                for root, dirs, files in os.walk(item):
                    for i in files:
                        try:
                            size = os.path.getsize(os.path.join(root, i))
                            totalSize += size
                        except Exception:
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


class IconProvider(QFileIconProvider):

    def __init__(self, parent=None):
        QFileIconProvider.__init__(self)

    def icon(self, icontype_or_qfileinfo):
        """Reimplement Qt method"""
        if isinstance(icontype_or_qfileinfo, QFileIconProvider.IconType):
            return super(IconProvider, self).icon(icontype_or_qfileinfo)
        else:
            qfileinfo = icontype_or_qfileinfo
            fname = os.path.normpath(qfileinfo.absoluteFilePath())
            if os.path.isdir(fname):
                dir = QDir(fname)
                dirList = dir.entryList(QDir.Filter.Files)
                if "__init__.py" in dirList:
                    icon = QIcon(
                        os.path.join("Resources", "images", "box"))
                else:
                    icon = QIcon(
                        os.path.join("Resources", "images", "folder-horizontal"))
                return icon
            else:
                if os.path.basename(fname) == "__init__.py":
                    return QIcon(os.path.join("Resources", "images", "haiku-wide"))
                ext = os.path.splitext(fname)[1][1:]
                if ext == "py" or ext == "pyw":
                    return QIcon(os.path.join("Resources", "images", "gear"))
                else:
                    return super(IconProvider, self).icon(qfileinfo)


class ProjectTree(QTreeView):

    fileActivated = pyqtSignal(str)

    def __init__(self, editorTabWidget, root, app, projectSettings, progressWidget, parent):
        QTreeView.__init__(self, parent)

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

        self.fileSystemModel = QFileSystemModel()
        self.fileSystemModel.setRootPath(QDir.rootPath())
        self.fileSystemModel.setNameFilterDisables(False)
        self.fileSystemModel.setIconProvider(iconProvider)
        self.setModel(self.fileSystemModel)
        self.setColumnWidth(0, 300)

        self.createActions()
        self.loadShortcut(self.root)

        if not to_bool(self.projectSettings.get("ShowAllFiles"), True):
            self.fileSystemModel.setNameFilters(['*.py', '*.pyw'])
        self.showAllFilesAct.setChecked(
            to_bool(self.projectSettings.get("ShowAllFiles"), True))

    def contextMenuEvent(self, event):
        indexList = self.selectedIndexes()
        selection = len(indexList) != 0

        self.contextMenu = QMenu()
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

        self.contextMenu.exec(event.globalPos())

    def createActions(self):
        self.addFileAct = QAction(
            "File", self,
            statusTip="File", triggered=self.newFile)

        self.addDirAct = QAction(
            "Directory", self,
            statusTip="Directory", triggered=self.newDirectory)

        self.addPackageAct = QAction(
            QIcon(os.path.join("Resources", "images", "box")),
            "Package", self,
            statusTip="Package", triggered=self.newPackage)

        self.copyAct = QAction(
            "Copy", self, shortcut=QKeySequence.StandardKey.Copy,
            statusTip="Copy", triggered=self.copyItem)

        self.pasteAct = QAction(
            "Paste", self, shortcut=QKeySequence.StandardKey.Paste,
            statusTip="Paste", triggered=self.pasteItem)

        self.deleteAct = QAction(
            "Delete", self, shortcut=QKeySequence.StandardKey.Delete,
            statusTip="Delete Selection", triggered=self.deleteItem)

        self.addExistingFilesAct = \
            QAction(
                "Files", self,
                statusTip="Files", triggered=self.addExistingFiles)

        self.addExistingDirectoriesAct = \
            QAction(
                "Directory", self,
                statusTip="Directory", triggered=self.addExistingDirectory)

        self.mainScriptsAct = QAction(
            QIcon(os.path.join("Resources", "images", "location")),
            "Set as Main Script", self, statusTip="Set as Main Script",
            triggered=self.setMainScript)

        self.collapseAllAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "collapse")),
                "Collapse All", self,
                statusTip="Collapse Tree", triggered=self.collapseAll)

        self.expandAllAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "expand")),
                "Expand All", self,
                statusTip="Expand Tree", triggered=self.expandAll)

        self.showAllFilesAct = \
            QAction(
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
        url = QUrl.fromLocalFile(path)
        data = QMimeData()
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
                    reply = QMessageBox.warning(self, "Paste",
                                                      "'" + os.path.basename(
                                                          dest) + "' already exists in the destination directory.\n\nWould you like to replace it?",
                                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
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
                with open(path, 'w'):
                    pass
                self.editorTabWidget.loadfile(path)
            except Exception:
                QMessageBox.warning(self, "New File",
                                                    "File creation failed!")

    def newDirectory(self):
        path = self.getCurrentDirectory()
        dirName = GetName("New Directory", path, self)
        if dirName.accepted:
            path = os.path.join(path, dirName.text)
            try:
                os.mkdir(path)
            except Exception:
                QMessageBox.warning(self, "New Directory",
                                                    "Failed to create directory!")

    def newPackage(self):
        path = self.getCurrentDirectory()
        packageName = GetName("New Package", path, self)
        if packageName.accepted:
            path = os.path.join(path, packageName.text)
            try:
                os.mkdir(path)
                f = os.path.join(path, "__init__.py")
                with open(f, "w"):
                    pass
                self.editorTabWidget.loadfile(f)
            except Exception:
                QMessageBox.warning(self, "New Package",
                                                    "Package creation failed!")

    def addExistingFiles(self):
        files = file_dialog_paths(QFileDialog.getOpenFileNames(
            self,
            "Select Files", QDir.homePath(),
            "All Files (*);;Text Files (*.txt)",
        ))
        if files:
            destDir = self.getCurrentDirectory()
            pathList = []
            for file in files:
                destPathName = os.path.join(destDir, os.path.basename(file))
                if os.path.exists(destPathName):
                    reply = QMessageBox.warning(
                        self, "Add Existing Files",
                        "'" + os.path.basename(
                            destPathName) + "' already exists in the destination directory.\n\nWould you like to replace it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        pass
                    else:
                        continue
                pathList.append(file)
            self.copyThread.copy(pathList, destDir)
            self.progressWidget.showBusy(True, "Preparing to copy...")

    def addExistingDirectory(self):
        options = (QFileDialog.Option.DontResolveSymlinks
                   | QFileDialog.Option.ShowDirsOnly)
        directory = file_dialog_path(QFileDialog.getExistingDirectory(
            self, "Select Directory", QDir.homePath(), options=options))
        if directory:
            destDir = self.getCurrentDirectory()
            destPathName = os.path.join(destDir, os.path.basename(directory))
            if os.path.exists(destPathName):
                reply = QMessageBox.warning(
                    self, "Add Existing Directory",
                                                  "'" + os.path.basename(
                                                      destPathName) + "' already exists in the destination directory.\n\nWould you like to replace it?",
                                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
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
            QMessageBox.warning(
                    self, "Add Existing Items", "Failed to complete copy!\n\n" + str(self.copyThread.errors))

    def deleteItem(self):
        path = self.getCurrentFilePath()
        reply = QMessageBox.warning(self, "Delete",
                                          "Permanently delete '" + os.path.basename(
                                              path) + "' from the project?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as err:
                QMessageBox.warning(self, "Delete",
                                                    "Failed to delete item!\n\n" + str(err))
        else:
            return

    def loadShortcut(self, path):
        if os.path.exists(path):
            self.setRootIndex(self.fileSystemModel.index(path))
        else:
            QMessageBox.warning(self, "Open",
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

        dom_document = QDomDocument()
        with open(self.projectPathDict["projectmainfile"], "r") as file:
            dom_document.setContent(file.read())

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
        dom_document = QDomDocument("Project")
        properties = dom_document.createElement("properties")
        dom_document.appendChild(properties)

        tag = dom_document.createElement("pcode_project")
        for key, value in settingsDict.items():
            tag.setAttribute(key, value)
        properties.appendChild(tag)

        with open(self.projectPathDict["projectmainfile"], "w") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(dom_document.toString())


class SearchThread(QThread):

    foundList = pyqtSignal(dict)

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


class LineEdit(QLineEdit):

    fileActivated = pyqtSignal(str)

    def __init__(self, viewStack, searchResultsTree, parent=None):
        QWidget.__init__(self, parent)

        self.searchResultsTree = searchResultsTree
        self.viewStack = viewStack

        self.setPlaceholderText("Search")

        hbox = QHBoxLayout()
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.addStretch(1)
        self.setLayout(hbox)

        self.clearButton = QToolButton()
        self.clearButton.setAutoRaise(True)
        self.clearButton.setIcon(
            QIcon(os.path.join("Resources", "images", "disabled")))
        self.clearButton.clicked.connect(self.clearSearch)
        hbox.addWidget(self.clearButton)

    def keyPressEvent(self, event):
        key = event.key()

        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        alt = event.modifiers() & Qt.KeyboardModifier.AltModifier
        event.modifiers() & Qt.KeyboardModifier.ShiftModifier

        if ctrl:
            pass
        elif alt:
            pass
        elif key == Qt.Key.Key_Up:
            currentItem = self.currentItem()
            if currentItem is not None:
                itemAbove = self.searchResultsTree.itemAbove(currentItem)
                if itemAbove is None:
                    return
                self.searchResultsTree.setCurrentItem(itemAbove)
                self.setFocus()
        elif key == Qt.Key.Key_Down:
            currentItem = self.currentItem()
            if currentItem is not None:
                itemBelow = self.searchResultsTree.itemBelow(currentItem)
                if itemBelow is None:
                    return
                self.searchResultsTree.setCurrentItem(itemBelow)
                self.setFocus()
        else:
            QLineEdit.keyPressEvent(self, event)

    def clearSearch(self):
        self.clear()
        self.viewStack.setCurrentIndex(0)

    def currentItem(self):
        if self.searchResultsTree.topLevelItemCount() > 0:
            item = self.searchResultsTree.selectedItems()[0]
            return item
        else:
            return None


class ProjectView(QWidget):

    fileActivated = pyqtSignal(str)

    def __init__(self, editorTabWidget, root, app, projectSettings, parent=None):
        QWidget.__init__(self, parent)

        self.refactor = editorTabWidget.refactor
        self.root = root

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 2, 2)
        self.setLayout(mainLayout)

        self.progressWidget = ProgressWidget()
        mainLayout.addWidget(self.progressWidget)
        self.progressWidget.hide()

        self.viewStack = QStackedWidget()
        mainLayout.addWidget(self.viewStack)

        self.projectTree = ProjectTree(
            editorTabWidget, root, app, projectSettings, self.progressWidget, self)
        self.viewStack.addWidget(self.projectTree)

        self.searchResultsTree = QTreeWidget(self)
        self.searchResultsTree.setObjectName("sidebarItem")
        self.searchResultsTree.setHeaderItem(
            QTreeWidgetItem(["Search Results:"]))
        self.searchResultsTree.activated.connect(self.loadFile)
        self.viewStack.addWidget(self.searchResultsTree)

        self.searchThread = SearchThread()
        self.searchThread.foundList.connect(self.updateSearchTree)

        self.searchTimer = QTimer()
        self.searchTimer.setSingleShot(True)
        self.searchTimer.timeout.connect(self.search)
        
        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        mainLayout.addLayout(vbox)

        self.searchLine = LineEdit(self.viewStack, self.searchResultsTree)
        self.searchLine.textChanged.connect(self.startSearchTimer)
        self.searchLine.returnPressed.connect(self.loadFile)
        vbox.addWidget(self.searchLine)

        self.progressBar = QProgressBar()
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
                folderItem = QTreeWidgetItem(self.searchResultsTree)
                pathRelativeToProject = folder.partition(
                    self.root + os.path.sep)[-1]
                folderItem.setText(0, pathRelativeToProject)
                folderItem.setForeground(0, QBrush(
                    QColor("#003366")))
                for i in fileList:
                    fileItem = QTreeWidgetItem(folderItem)
                    icon = Global.iconFromPath(os.path.join(folder, i))
                    fileItem.setText(0, i)
                    fileItem.setIcon(0, QIcon(icon))
                folderItem.setExpanded(True)

            item = self.searchResultsTree.topLevelItem(0)
            self.searchResultsTree.setCurrentItem(item.child(0))
        else:
            folderItem = QTreeWidgetItem()
            item = QTreeWidgetItem()
            item.setText(0, "<No results found>")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            folderItem.addChild(item)
            self.searchResultsTree.addTopLevelItem(folderItem)
            folderItem.setExpanded(True)
