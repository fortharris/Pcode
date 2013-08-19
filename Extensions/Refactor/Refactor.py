import os
from PyQt4 import QtGui, QtCore

# rope
from rope.refactor.rename import Rename
from rope.refactor.topackage import ModuleToPackage
from rope.refactor import inline
from rope.refactor.localtofield import LocalToField
from rope.base.project import Project
from rope.base import libutils
from rope.contrib import codeassist
from rope.contrib.findit import (find_occurrences, find_implementations,
                                 find_definition)
from Extensions.Refactor.UsageDialog import UsageDialog

class GetName(QtGui.QDialog):
    def __init__(self, caption, defaultText, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        mainLayout = QtGui.QVBoxLayout()

        mainLayout.addWidget(QtGui.QLabel("New name:"))

        self.nameLine = QtGui.QLineEdit()
        self.nameLine.setText(defaultText)
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

        self.resize(300, 20)
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


class FindUsageThread(QtCore.QThread):
    def run(self):
        self.error = None
        self.foundList = []
        try:
            resource = self.ropeProject.get_file(self.path)
            result = find_occurrences(self.ropeProject, resource, self.offset)
            self.itemsDict = {}
            if len(result) == 0:
                self.error = "No usages found."
            else:
                for i in result:
                    line = i.lineno
                    path = i.resource.path
                    if path in self.itemsDict:
                        self.itemsDict[path].append(line)
                    else:
                        self.itemsDict[path] = [line]
        except Exception as err:
            self.error = str(err)

    def find(self, path, ropeProject, offset):
        self.path = path
        self.ropeProject = ropeProject
        self.offset = offset

        self.start()


class RenameThread(QtCore.QThread):
    def run(self):
        self.error = None
        self.changedFiles = []
        try:
            self.ropeProject.validate()
            rename = Rename(self.ropeProject, libutils.path_to_resource(
                self.ropeProject, self.path), self.offset)
            changes = rename.get_changes(self.new_name, docs=True)
            self.ropeProject.do(changes)
            changed = changes.get_changed_resources()
            # changed is a set
            for i in changed:
                self.changedFiles.append(i.real_path)
        except Exception as err:
            self.error = str(err)

    def rename(self, new_name, path, ropeProject, offset):
        self.new_name = new_name
        self.path = path
        self.ropeProject = ropeProject
        self.offset = offset

        self.start()


class InlineThread(QtCore.QThread):
    def run(self):
        self.error = None
        self.changedFiles = []
        try:
            inlined = inline.create_inline(
                self.ropeProject, self.resource, self.offset)
            changes = inlined.get_changes()
            self.ropeProject.do(changes)
            changed = changes.get_changed_resources()
            # changed is a set
            for i in changed:
                self.changedFiles.append(i.real_path)
        except Exception as err:
            self.error = str(err)

    def inline(self, project, resource, offset):
        self.resource = resource
        self.ropeProject = project
        self.offset = offset

        self.start()


class LocalToFieldThread(QtCore.QThread):
    def run(self):
        self.error = None
        self.changedFiles = []
        try:
            convert = LocalToField(
                self.ropeProject, self.resource, self.offset)
            changes = convert.get_changes()
            self.ropeProject.do(changes)
            changed = changes.get_changed_resources()
            # changed is a set
            for i in changed:
                self.changedFiles.append(i.real_path)
        except Exception as err:
            self.error = str(err)

    def convert(self, project, resource, offset):
        self.resource = resource
        self.ropeProject = project
        self.offset = offset

        self.start()


class ModuleToPackageThread(QtCore.QThread):
    def run(self):
        self.error = None
        try:
            convert = ModuleToPackage(self.ropeProject,
                                      libutils.path_to_resource(self.ropeProject, self.path))
            changes = convert.get_changes()
            self.ropeProject.do(changes)
        except Exception as err:
            self.error = str(err)

    def convert(self, path, ropeProject):
        self.path = path
        self.ropeProject = ropeProject

        self.start()


class Refactor(QtGui.QWidget):
    def __init__(self, editorTabWidget, busyWidget, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.editorTabWidget = editorTabWidget
        self.busyWidget = busyWidget
        self.root = editorTabWidget.pathDict["sourcedir"]
        ropeFolder = editorTabWidget.pathDict["ropeFolder"]

        prefs = {
                'ignored_resources': ['*.pyc', '*~', '.ropeproject',
                                      '.hg', '.svn', '_svn', '.git',
                                      '__pycache__'],
                'python_files': ['*.py'],
                'save_objectdb': True,
                'compress_objectdb': False,
                'automatic_soa': True,
                'soa_followed_calls': 0,
                'perform_doa': True,
                'validate_objectdb': True,
                'max_history_items': 32,
                'save_history': True,
                'compress_history': False,
                'indent_size': 4,
                'extension_modules': [
                                    "PyQt4", "PyQt4.QtGui", "QtGui", "PyQt4.QtCore", "QtCore",
                                    "PyQt4.QtScript", "QtScript", "os.path", "numpy", "scipy", "PIL",
                                    "OpenGL", "array", "audioop", "binascii", "cPickle", "cStringIO",
                                    "cmath", "collections", "datetime", "errno", "exceptions", "gc",
                                    "imageop", "imp", "itertools", "marshal", "math", "mmap", "msvcrt",
                                    "nt", "operator", "os", "parser", "rgbimg", "signal", "strop", "sys",
                                    "thread", "time", "wx", "wxPython", "xxsubtype", "zipimport", "zlib"
                                    ],
                'import_dynload_stdmods': True,
                'ignore_syntax_errors': True,
                'ignore_bad_imports': True
                }

        self.ropeProject = Project(
            projectroot=self.root, ropefolder=ropeFolder, **prefs)
        self.ropeProject.prefs.add('python_path', 'c:/Python33')
        self.ropeProject.prefs.add('source_folders', 'c:/Python33/Lib')
        self.ropeProject.validate()

        self.noProject = Project(projectroot="temp", ropefolder=None)

        self.findThread = FindUsageThread()
        self.findThread.finished.connect(self.findOccurrencesFinished)

        self.renameThread = RenameThread()
        self.renameThread.finished.connect(self.renameFinished)

        self.inlineThread = InlineThread()
        self.inlineThread.finished.connect(self.inlineFinished)

        self.localToFieldThread = LocalToFieldThread()
        self.localToFieldThread.finished.connect(self.localToFieldFinished)

        self.moduleToPackageThread = ModuleToPackageThread()
        self.moduleToPackageThread.finished.connect(
            self.moduleToPackageFinished)

        self.createActions()

        self.refactorMenu = QtGui.QMenu("Refactor")
        self.refactorMenu.addAction(self.renameAttributeAct)
        self.refactorMenu.addAction(self.inlineAct)
        self.refactorMenu.addAction(self.localToFieldAct)

    def close(self):
        self.ropeProject.close()

    def createActions(self):
        self.findDefAct = \
            QtGui.QAction(QtGui.QIcon(os.path.join("Resources","images","map_marker")),
                          "Go-to Definition", self, statusTip="Go-to Definition",
                          triggered=self.findDefinition)

        self.findOccurrencesAct = \
            QtGui.QAction("Usages", self, statusTip="Usages",
                          triggered=self.findOccurrences)

        self.moduleToPackageAct = \
            QtGui.QAction(
                "Convert to Package", self, statusTip="Convert to Package",
                triggered=self.moduleToPackage)

        self.renameModuleAct = \
            QtGui.QAction("Rename", self, statusTip="Rename",
                          triggered=self.renameModule)

        self.renameAttributeAct = \
            QtGui.QAction("Rename", self, statusTip="Rename",
                          triggered=self.renameAttribute)

        self.inlineAct = \
            QtGui.QAction("Inline", self, statusTip="Inline",
                          triggered=self.inline)

        self.localToFieldAct = \
            QtGui.QAction("Local-to-Field", self, statusTip="Local-to-Field",
                          triggered=self.localToField)

        self.getDocAct = \
            QtGui.QAction("Documentation", self, statusTip="Documentation",
                          triggered=self.getDoc)

        self.getCallTipAct = \
            QtGui.QAction("CallTip", self, statusTip="CallTip",
                          triggered=self.getCallTip)

    def renameModule(self):
        index = self.editorTabWidget.currentIndex()
        moduleName = self.editorTabWidget.tabText(index)
        moduleName = os.path.splitext(moduleName)[0]
        newName = GetName("Rename", moduleName, self)
        project = self.getProject()
        if newName.accepted:
            saved = self.editorTabWidget.saveProject()
            if saved:
                path = self.editorTabWidget.getEditorData("filePath")
                self.renameThread.rename(newName.text, path, project, None)
                self.busyWidget.showBusy(True, "Renaming... please wait!")

    def renameAttribute(self):
        objectName = self.editorTabWidget.get_current_word()
        newName = GetName("Rename", objectName, self)
        if newName.accepted:
            project = self.getProject()
            saved = self.editorTabWidget.saveProject()
            if saved:
                offset = self.getOffset()
                path = self.editorTabWidget.getEditorData("filePath")
                self.renameThread.rename(newName.text, path, project, offset)
                self.busyWidget.showBusy(True, "Renaming... please wait!")

    def renameFinished(self):
        self.busyWidget.showBusy(False)
        if self.renameThread.error != None:
            message = QtGui.QMessageBox.warning(self, "Failed Rename",
                                                self.renameThread.error)
            return
        if self.renameThread.offset is None:
            # filename has been changed
            oldPath = self.editorTabWidget.getEditorData("filePath")
            ext = os.path.splitext(oldPath)[1]
            newPath = os.path.join(os.path.dirname(oldPath),
                                   self.renameThread.new_name + ext)
            self.editorTabWidget.updateEditorData("filePath", newPath)
        else:
            if len(self.renameThread.changedFiles) > 0:
                self.editorTabWidget.reloadModules(
                    self.renameThread.changedFiles)

    def inline(self):
        offset = self.getOffset()
        path = self.editorTabWidget.getEditorData("filePath")
        project = self.getProject()
        resource = project.get_file(path)
        saved = self.editorTabWidget.saveProject()
        if saved:
            self.inlineThread.inline(project, resource, offset)
            self.busyWidget.showBusy(True, "Inlining... please wait!")

    def inlineFinished(self):
        self.busyWidget.showBusy(False)
        if self.inlineThread.error != None:
            message = QtGui.QMessageBox.warning(self, "Failed Inline",
                                                self.inlineThread.error)
            return
        if len(self.inlineThread.changedFiles) > 0:
            self.editorTabWidget.reloadModules(self.inlineThread.changedFiles)

    def localToField(self):
        offset = self.getOffset()
        path = self.editorTabWidget.getEditorData("filePath")
        project = self.getProject()
        resource = project.get_file(path)
        saved = self.editorTabWidget.saveProject()
        if saved:
            self.localToFieldThread.convert(project, resource, offset)
            self.busyWidget.showBusy(True, "Converting Local to Field... please wait!")

    def localToFieldFinished(self):
        self.busyWidget.showBusy(False)
        if self.localToFieldThread.error != None:
            message = QtGui.QMessageBox.warning(self, "Failed Local-to-Field",
                                                self.localToFieldThread.error)
            return
        if len(self.localToFieldThread.changedFiles) > 0:
            self.editorTabWidget.reloadModules(
                self.localToFieldThread.changedFiles)

    def findDefinition(self):
        saved = self.editorTabWidget.saveProject()
        if saved:
            offset = self.getOffset()
            path = self.editorTabWidget.getEditorData("filePath")
            project = self.getProject()
            resource = project.get_file(path)
            try:
                result = find_definition(project,
                                         self.editorTabWidget.getSource(), offset, resource)
                if result is None:
                    self.editorTabWidget.showNotification(
                        "No definition found.")
                else:
                    start, end = result.region
                    offset = result.offset
                    line = result.lineno
                    result_path = result.resource.path
                    sourcePath = self.editorTabWidget.pathDict["sourcedir"]
                    if not os.path.isabs(result_path):
                        result_path = os.path.join(sourcePath, result_path)
                    if os.path.samefile(result_path, path):
                        pass
                    else:
                        self.editorTabWidget.loadfile(result_path)
                    editor = self.editorTabWidget.focusedEditor()
                    start = editor.lineIndexFromPosition(start)
                    end = editor.lineIndexFromPosition(end)
                    editor.setSelection(start[0], start[1], end[0], end[1])
                    editor.ensureLineVisible(line - 1)
            except Exception as err:
                self.editorTabWidget.showNotification(str(err))

    def moduleToPackage(self):
        path = self.editorTabWidget.getEditorData("filePath")
        project = self.getProject()
        saved = self.editorTabWidget.saveProject()
        if saved:
            self.moduleToPackageThread.convert(path, project)
            self.busyWidget.showBusy(True, "Converting... please wait!")

    def moduleToPackageFinished(self):
        self.busyWidget.showBusy(False)
        if self.moduleToPackageThread.error != None:
            message = QtGui.QMessageBox.warning(self, "Failed to convert",
                                                self.moduleToPackageThread.error)

    def findOccurrences(self):
        offset = self.getOffset()
        project = self.getProject()
        saved = self.editorTabWidget.saveProject()
        if saved:
            path = self.editorTabWidget.getEditorData("filePath")
            self.objectName = self.editorTabWidget.get_current_word()
            self.findThread.find(path, project, offset)
            self.busyWidget.showBusy(True, "Finding usages... please wait!")

    def findOccurrencesFinished(self):
        self.busyWidget.showBusy(False)
        if self.findThread.error != None:
            self.editorTabWidget.showNotification(self.findThread.error)
            return
        if len(self.findThread.itemsDict) > 0:
            foundList = []
            for parent, lines in self.findThread.itemsDict.items():
                parentItem = QtGui.QTreeWidgetItem()
                parentItem.setForeground(0, QtGui.QBrush(
                    QtGui.QColor("#003366")))
                parentItem.setText(0, parent)
                for line in lines:
                    childItem = QtGui.QTreeWidgetItem()
                    childItem.setText(0, str(line))
                    childItem.setFirstColumnSpanned(True)
                    parentItem.addChild(childItem)
                    foundList.append(parentItem)
            usageDialog = UsageDialog(self.editorTabWidget, "Usages: " + self.objectName, foundList, self)
        else:
            self.editorTabWidget.showNotification("No usages found.")

    def getOffset(self):
        return self.editorTabWidget.getOffset()

    def get_absolute_coordinates(self):
        editor = self.editorTabWidget.focusedEditor()
        point = editor.get_absolute_coordinates()
        return point

    def getCompletions(self):
        offset = self.getOffset()
        project = self.getProject()
        proposals = codeassist.code_assist(project,
                                           self.editorTabWidget.getSource(), offset)
        proposals = codeassist.sorted_proposals(proposals)
        if len(proposals) > 0:
            cmpl = []
            for i in proposals:
                cmpl.append(str(i))

            return cmpl
        else:
            return []

    def getDoc(self, offset=None):
        if offset is None:
            offset = self.getOffset()
        project = self.getProject()
        try:
            doc = codeassist.get_doc(project,
                                     self.editorTabWidget.getSource(), offset)
            return doc
        except Exception as err:
            return None

    def getCallTip(self, offset=None):
        if offset is None:
            offset = self.getOffset()
        project = self.getProject()
        try:
            calltip = codeassist.get_calltip(project,
                                             self.editorTabWidget.getSource(), offset)

            return calltip
        except Exception as err:
            return None

    def getProject(self):
        path = self.editorTabWidget.getEditorData("filePath")
        if path is None:
            return self.noProject
        if path.startswith(self.editorTabWidget.pathDict["sourcedir"]):
            return self.ropeProject
        else:
            return self.noProject
