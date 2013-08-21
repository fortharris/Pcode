import os
import shutil
from PyQt4 import QtCore, QtGui

from Extensions.ProjectManager.ProjectViewer import ProjectViewer
from Extensions.ProjectManager.Build import Build


class ExportThread(QtCore.QThread):

    def run(self):
        self.error = None
        try:
            shutil.make_archive(self.fileName, "zip", self.path)
        except Exception as err:
            self.error = str(err)

    def export(self, fileName, path):
        self.fileName = fileName
        self.path = path

        self.start()


class ProjectManager(QtGui.QWidget):

    def __init__(
        self, editorTabWidget, messagesWidget, pathDict, projectSettings, useData, app,
            busyWidget, buildStatusWidget, parent):
        QtGui.QWidget.__init__(self, parent)

        self.busyWidget = busyWidget
        self.editorTabWidget = editorTabWidget

        self.useData = useData
        self.projects = parent

        self.configDialog = editorTabWidget.configDialog

        if pathDict["type"] == "Desktop Application":
            self.build = Build(
                buildStatusWidget, messagesWidget, pathDict, projectSettings, useData,
                self.configDialog.buildConfig, editorTabWidget, self)

        self.exportThread = ExportThread()
        self.exportThread.finished.connect(self.finishExport)

        self.projectViewer = ProjectViewer(
            self.editorTabWidget, pathDict["sourcedir"], app)

    def buildProject(self):
        if self.editorTabWidget.errorsInProject():
            reply = QtGui.QMessageBox.warning(self, "Build",
                                              "Errors exist in your project. Build anyway?",
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.build.build()
            else:
                return
        else:
            self.build.build()

    def configureProject(self):
        self.configDialog.exec_()

    def openBuild(self):
        self.build.openDir()

    def exportProject(self):
        curren_window = self.projects.projectWindowStack.currentWidget()
        name = curren_window.pathDict["name"]
        path = curren_window.pathDict["root"]

        options = QtGui.QFileDialog.Options()
        savepath = os.path.join(self.useData.getLastOpenedDir(), name)
        savepath = os.path.normpath(savepath)
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Export", savepath,
                                                     "All files (*)", options)
        if fileName:
            self.useData.saveLastOpenedDir(os.path.split(fileName)[0])

            self.exportThread.export(fileName, path)
            self.busyWidget.showBusy(True, "Exporting project... please wait!")

    def finishExport(self):
        self.busyWidget.showBusy(False)
        if self.exportThread.error is not None:
            message = QtGui.QMessageBox.warning(
                self, "Export Failed", self.exportThread.error)
