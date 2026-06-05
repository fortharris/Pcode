"""
Manages all opened projects such as the creation and closing of projects
"""

import os
import sys
import shutil
import traceback
import logging
from Extensions.qt_bindings import QtCore, QtGui

from Extensions.EditorWindow.EditorWindow import EditorWindow
from Extensions.Projects.NewProjectDialog import NewProjectDialog


class CreateProjectThread(QtCore.QThread):

    def run(self):
        self.error = False
        try:
            self.projectPath = os.path.join(self.projDataDict["location"],
                                            self.projDataDict["name"])
            os.mkdir(self.projectPath)

            data = os.path.join(self.projectPath, "Data")
            os.mkdir(data)
            with open(os.path.join(data, "wpad.txt"), "w"):
                pass

            ropeFolder = os.path.join(self.projectPath, "Rope")
            os.mkdir(ropeFolder)
            shutil.copy(os.path.join("Resources", "default_config.py"),
                        os.path.join(ropeFolder, "config.py"))

            os.mkdir(os.path.join(self.projectPath, "Resources"))
            os.mkdir(os.path.join(self.projectPath, "Resources", "VirtualEnv"))
            os.mkdir(
                os.path.join(self.projectPath, "Resources", "VirtualEnv", "Linux"))
            os.mkdir(
                os.path.join(self.projectPath, "Resources", "VirtualEnv", "Mac"))
            os.mkdir(
                os.path.join(self.projectPath, "Resources", "VirtualEnv", "Windows"))
            os.mkdir(os.path.join(self.projectPath, "Resources", "Icons"))

            os.mkdir(os.path.join(self.projectPath, "temp"))
            os.mkdir(os.path.join(self.projectPath, "temp", "Backup"))
            os.mkdir(os.path.join(self.projectPath, "temp", "Backup", "Files"))

            sourceDir = os.path.join(self.projectPath, "src")
            if self.projDataDict["importdir"] != '':
                shutil.copytree(self.projDataDict["importdir"], sourceDir)
            else:
                os.mkdir(os.path.join(self.projectPath, "src"))

            if self.projDataDict["type"] == "Desktop Application":
                build = os.path.join(self.projectPath, "Build")
                os.mkdir(build)
                os.mkdir(os.path.join(build, "Linux"))
                os.mkdir(os.path.join(build, "Mac"))
                os.mkdir(os.path.join(build, "Windows"))

            self.mainScript = os.path.join(self.projectPath, "src",
                                           self.projDataDict["mainscript"])
            main_template = (
                '"""Main entry point for {name}."""\n\n\n'
                'def main():\n'
                '    print("Hello from Pcode")\n\n\n'
                'if __name__ == "__main__":\n'
                '    main()\n'
            ).format(name=self.projDataDict["name"])
            with open(self.mainScript, 'w', encoding='utf-8') as main_file:
                main_file.write(main_template)

            if self.projDataDict["type"] == "Desktop Application":
                self.writeBuildProfile()
            self.writeDefaultSession()
            self.writeProjectData()
            self.writePyproject()
            self.writeRopeProfile()
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
            self.error = str(err)

    def writeProjectData(self):
        from Extensions.ProjectData import save as save_project_data
        from Extensions.ProjectManifest import write as write_manifest

        write_manifest(
            self.projectPath,
            self.projDataDict["name"],
            self.projDataDict["type"],
            self.projDataDict["mainscript"],
        )
        defaults = {
            'ClearOutputWindowOnRun': 'False',
            'LastOpenedPath': '',
            'RunType': 'Run',
            'BufferSize': '900',
            'RunArguments': '',
            'DefaultInterpreter': '',
            'TraceType': '3',
            'RunWithArguments': 'False',
            'RunInternal': 'True',
            'UseVirtualEnv': 'False',
            'Closed': 'True',
            'Icon': '',
            'ShowAllFiles': 'True',
            'LastCloseSuccessful': 'True',
            'DebugWait': 'False',
        }
        save_project_data(self.projectPath, {
            "shortcuts": [],
            "recentfiles": [],
            "favourites": [],
            "launchers": {},
            "settings": defaults,
        })

    def writePyproject(self):
        name = self.projDataDict["name"].replace('"', '\\"')
        content = (
            '[project]\n'
            'name = "{name}"\n'
            'version = "0.1.0"\n'
            'requires-python = ">=3.10"\n'
            'description = "Pcode project"\n'
        ).format(name=name)
        with open(os.path.join(self.projectPath, "pyproject.toml"), "w",
                  encoding="utf-8") as file:
            file.write(content)

    def writeDefaultSession(self):
        from Extensions.SessionData import write_empty_session
        write_empty_session(self.projectPath)

    def writeRopeProfile(self):
        from Extensions.RopeProfile import default_profile, save as save_rope_profile
        save_rope_profile(os.path.join(self.projectPath, "Rope"), default_profile())

    def writeBuildProfile(self):
        from Extensions.BuildProfile import default_profile, save as save_build_profile
        build_dir = os.path.join(self.projectPath, "Build")
        profile = default_profile(self.projDataDict["windowtype"])
        scalars = {k: v for k, v in profile.items() if k != "lists"}
        save_build_profile(build_dir, scalars, profile["lists"])

    def create(self, data):
        self.projDataDict = data

        self.start()


class Projects(QtGui.QWidget):

    def __init__(self, useData, busyWidget, library, settingsWidget, app,
                 projectWindowStack, projectTitleBox, parent):
        QtGui.QWidget.__init__(self, parent)

        self.createProjectThread = CreateProjectThread()
        self.createProjectThread.finished.connect(self.finalizeNewProject)

        self.newProjectDialog = NewProjectDialog(useData, self)
        self.newProjectDialog.projectDataReady.connect(self.createProject)

        self.busyWidget = busyWidget
        self.useData = useData
        self.app = app
        self.projectWindowStack = projectWindowStack
        self.projectTitleBox = projectTitleBox
        self.library = library
        self.settingsWidget = settingsWidget
        self.pcode = parent

    def closeProgram(self):
        self.pcode.close()

    def readProject(self, path):
        from Extensions.ProjectManifest import read as read_manifest

        json_file = os.path.join(path, "project.json")
        xml_file = os.path.join(path, "project.xml")
        if not os.path.isfile(json_file) and not os.path.isfile(xml_file):
            return False
        return read_manifest(path)

    def loadProject(self, path, show, new):
        if not self.pcode.showProject(path):
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            projectPathDict = {
                "notes": os.path.join(path, "Data", "wpad.txt"),
                "session": os.path.join(path, "Data", "session.json"),
                "session_xml": os.path.join(path, "Data", "session.xml"),
                "windata": os.path.join(path, "Data", "windata.json"),
                "projectdata": os.path.join(path, "Data", "projectdata.json"),
                "projectdata_xml": os.path.join(path, "Data", "projectdata.xml"),
                "snippetsdir": os.path.join(path, "Data", "templates"),
                "tempdir": os.path.join(path, "temp"),
                "backupdir": os.path.join(path, "temp", "Backup", "Files"),
                "backupfile": os.path.join(path, "temp", "Backup", "bak"),
                "sourcedir": os.path.join(path, "src"),
                "ropeFolder": os.path.join(path, "Rope"),
                "buildprofile": os.path.join(path, "Build", "profile.json"),
                "buildprofile_xml": os.path.join(path, "Build", "profile.xml"),
                "ropeprofile": os.path.join(path, "Rope", "profile.json"),
                "ropeprofile_xml": os.path.join(path, "Rope", "profile.xml"),
                "projectmainfile": os.path.join(path, "project.json"),
                "iconsdir": os.path.join(path, "Resources", "Icons"),
                "root": path
                }

            if sys.platform == 'win32':
                projectPathDict["venvdir"] = os.path.join(path,
                               "Resources", "VirtualEnv", "Windows", "Venv")
            elif sys.platform == 'darwin':
                projectPathDict["venvdir"] = os.path.join(path,
                               "Resources", "VirtualEnv", "Mac", "Venv")
            else:
                projectPathDict["venvdir"] = os.path.join(path,
                               "Resources", "VirtualEnv", "Linux", "Venv")

            try:
                project_data = self.readProject(path)
                if project_data is False:
                    QtGui.QApplication.restoreOverrideCursor()
                    QtGui.QMessageBox.warning(self, "Open Project",
                                                        "Failed:\n\n" + path)
                    return
                projectPathDict["name"] = project_data[1]["Name"]
                projectPathDict["type"] = project_data[1]["Type"]
                projectPathDict["mainscript"] = os.path.join(path, "src",
                               project_data[1]["MainScript"])
                if sys.platform == 'win32':
                    projectPathDict["builddir"] = os.path.join(
                        path, "Build", "Windows")
                elif sys.platform == 'darwin':
                    projectPathDict["builddir"] = os.path.join(
                        path, "Build", "Mac")
                else:
                    projectPathDict["builddir"] = os.path.join(
                        path, "Build", "Linux")

                p_name = os.path.basename(path)

                projectWindow = EditorWindow(projectPathDict, self.library,
                                             self.busyWidget, self.settingsWidget.colorScheme,
                                             self.useData, self.app, self)
                if new:
                    projectWindow.editorTabWidget.loadfile(
                        projectPathDict["mainscript"])
                else:
                    projectWindow.restoreSession()
                projectWindow.editorTabWidget.updateWindowTitle.connect(
                    self.pcode.updateWindowTitle)

                self.pcode.addProject(projectWindow, p_name)

                if path in self.useData.OPENED_PROJECTS:
                    self.useData.OPENED_PROJECTS.remove(path)
                    self.useData.OPENED_PROJECTS.insert(0, path)
                else:
                    self.useData.OPENED_PROJECTS.insert(0, path)
                if show:
                    self.pcode.showProject(path)
            except Exception as err:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(
                    repr(traceback.format_exception(exc_type, exc_value,
                             exc_traceback)))
                QtGui.QApplication.restoreOverrideCursor()
                QtGui.QMessageBox.warning(self, "Failed Open",
                                                    "Problem opening project: \n\n" + str(err))
            QtGui.QApplication.restoreOverrideCursor()

    def closeProject(self):
        window = self.projectWindowStack.currentWidget()
        path = window.projectPathDict["root"]
        closed = window.closeWindow()
        if closed:
            self.pcode.removeProject(window)
            self.useData.OPENED_PROJECTS.remove(path)

    def createProject(self, data):
        self.createProjectThread.create(data)
        self.busyWidget.showBusy(True, "Creating project... please wait!")

    def finalizeNewProject(self):
        self.busyWidget.showBusy(False)
        if self.createProjectThread.error is not False:
            QtGui.QMessageBox.warning(self, "New Project",
                                                "Failed to create project:\n\n" + self.createProjectThread.error)
        else:
            projectPath = os.path.normpath(
                self.createProjectThread.projectPath)  # otherwise an error will occur in rope
            self.loadProject(projectPath, True, True)
