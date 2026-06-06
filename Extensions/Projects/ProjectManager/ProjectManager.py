import logging
import os
import shutil
import traceback

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from Extensions.Projects.ProjectManager.ProjectView.ProjectView import ProjectView


class ExportThread(QThread):

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


class ProjectManager(QWidget):

    def __init__(
        self, editorTabWidget, messagesWidget, projectPathDict, projectSettings,
            useData, app,
            busyWidget, buildStatusWidget, parent):
        QWidget.__init__(self, parent)

        self.busyWidget = busyWidget
        self.editorTabWidget = editorTabWidget

        self.useData = useData
        self.projects = parent
        self.projects = parent

        self.configDialog = editorTabWidget.configDialog

        self.build = None
        if projectPathDict["type"] == "Desktop Application":
            try:
                from Extensions.Projects.ProjectManager.Build import Build
                self.build = Build(
                    buildStatusWidget, messagesWidget, projectPathDict, projectSettings, useData,
                    self.configDialog.buildConfig, editorTabWidget, self)
            except Exception:
                logging.error(traceback.format_exc())
                self.build = None

        self.exportThread = ExportThread()
        self.exportThread.finished.connect(self.finishExport)

        self.projectView = ProjectView(
            self.editorTabWidget, projectPathDict["sourcedir"], app, projectSettings)

    def buildProject(self):
        if self.editorTabWidget.errorsInProject():
            reply = QMessageBox.warning(
                self, "Build",
                "There are errors in your project. Build anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.build.build()
            else:
                return
        else:
            self.build.build()

    def configureProject(self):
        self.configDialog.exec()

    def openBuild(self):
        self.build.openDir()

    def exportProject(self):
        curren_window = self.projects.projectWindowStack.currentWidget()
        name = curren_window.projectPathDict["name"]
        path = curren_window.projectPathDict["root"]

        savepath = os.path.join(self.useData.getLastOpenedDir(), name)
        savepath = os.path.normpath(savepath)
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Export", savepath,
            "All files (*)")
        if fileName:
            self.useData.saveLastOpenedDir(os.path.split(fileName)[0])

            self.exportThread.export(fileName, path)
            self.busyWidget.showBusy(True, "Exporting project... please wait!")

    def finishExport(self):
        self.busyWidget.showBusy(False)
        if self.exportThread.error is not None:
            QMessageBox.warning(
                self, "Export Failed", self.exportThread.error)
