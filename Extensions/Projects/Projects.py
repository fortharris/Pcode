"""newProjectDialog
Manages all opened projects such as the creation and closing of projects
"""

import os
import sys
import shutil
from PyQt4 import QtCore, QtGui, QtXml

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
            file = open(os.path.join(data, "log.txt"), "w")
            file.close()
            file = open(os.path.join(data, "wpad.txt"), "w")
            file.close()

            ropeFolder = os.path.join(self.projectPath, "Rope")
            os.mkdir(ropeFolder)
            shutil.copy("Resources\\default_config.py",
                        os.path.join(ropeFolder, "config.py"))

            os.mkdir(os.path.join(self.projectPath, "temp"))
            os.mkdir(os.path.join(self.projectPath, "temp\\Backup"))
            os.mkdir(os.path.join(self.projectPath, "temp\\Backup\\Files"))

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
            file = open(self.mainScript, 'w')
            file.close()

            if self.projDataDict["type"] == "Desktop Application":
                self.writeBuildProfile()
            self.writeDefaultSession()
            self.writeProjectData()
            self.writeRopeProfile()
        except Exception as err:
            self.error = str(err)

    def writeProjectData(self):
        dom_document = QtXml.QDomDocument("Project")

        properties = dom_document.createElement("properties")
        dom_document.appendChild(properties)

        tag = dom_document.createElement("pcode_project")

        tag.setAttribute("Version", "0.1")
        tag.setAttribute("Name", self.projDataDict["name"])
        tag.setAttribute("Type", self.projDataDict["type"])
        tag.setAttribute("MainScript", self.projDataDict["mainscript"])

        properties.appendChild(tag)

        file = open(os.path.join(self.projectPath, "project.xml"), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

        domDocument = QtXml.QDomDocument("projectdata")

        projectdata = domDocument.createElement("projectdata")
        domDocument.appendChild(projectdata)

        root = domDocument.createElement("shortcuts")
        projectdata.appendChild(root)

        root = domDocument.createElement("recentfiles")
        projectdata.appendChild(root)

        root = domDocument.createElement("favourites")
        projectdata.appendChild(root)

        root = domDocument.createElement("settings")
        projectdata.appendChild(root)

        s = 0
        defaults = {

            'ClearOutputWindowOnRun': '2',
            'LastOpenedPath': '',
            'RunType': 'Run',
            'BufferSize': '900',
            'RunArguments': '',
            'DefaultInterpreter': '',
            'TraceType': '3',
            'RunWithArguments': 'False',
            'DefaultVenv': 'Default',
            'RunInternal': 'True',
            'UseVirtualEnv': 'True',
            'Closed': 'True',
            'LastCloseSuccessful': 'True'
        }
        for key, value in defaults.items():
            tag = domDocument.createElement("key")
            root.appendChild(tag)

            t = domDocument.createTextNode(key + '=' + value)
            tag.appendChild(t)
            s += 1

        path = os.path.join(self.projectPath, "Data\\projectdata.xml")
        file = open(path, "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(domDocument.toString())
        file.close()

    def writeDefaultSession(self):
        dom_document = QtXml.QDomDocument("session")

        session = dom_document.createElement("session")
        dom_document.appendChild(session)

        file = open(os.path.join(self.projectPath, "Data\\session.xml"), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

    def writeRopeProfile(self):
        dom_document = QtXml.QDomDocument("rope_profile")

        main_data = dom_document.createElement("rope")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("ignoresyntaxerrors")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("ignorebadimports")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("maxhistoryitems")
        attrib = dom_document.createTextNode('32')
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

        file = open(os.path.join(self.projectPath, 'Rope\\profile.xml'), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

    def writeBuildProfile(self):
        dom_document = QtXml.QDomDocument("build_profile")

        main_data = dom_document.createElement("build")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("name")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("author")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("version")
        attrib = dom_document.createTextNode('0.1')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("comments")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("description")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("company")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copyright")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("trademarks")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("product")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("base")
        attrib = dom_document.createTextNode('Win32GUI.exe')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("icon")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("compress")
        attrib = dom_document.createTextNode("Compress")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("optimize")
        attrib = dom_document.createTextNode("Optimize")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copydeps")
        attrib = dom_document.createTextNode("Copy Dependencies")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttoexe")
        attrib = dom_document.createTextNode("Append Script to Exe")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttolibrary")
        attrib = dom_document.createTextNode("Append Script to Library")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("initscript")
        attrib = dom_document.createTextNode("Console3.py")
        root.appendChild(attrib)
        main_data.appendChild(root)

        lists = ["Includes",
                 "Excludes",
                 "Constants Modules",
                 "Packages",
                 "Replace Paths",
                 "Bin Includes",
                 "Bin Excludes",
                 "Bin Path Includes",
                 "Bin Path Excludes",
                 "Zip Includes",
                 "Include Files",
                 "Namespace Packages"]

        for i in lists:
            root = dom_document.createElement(i.replace(' ', '-'))
            main_data.appendChild(root)

        file = open(os.path.join(self.projectPath, 'Build\\profile.xml'), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

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
        # validate project
        project_file = os.path.join(path, "project.xml")
        if os.path.exists(project_file) == False:
            return False
        dom_document = QtXml.QDomDocument()
        file = open(os.path.join(path, "project.xml"), "r")
        dom_document.setContent(file.read())
        file.close()

        data = {}

        elements = dom_document.documentElement()
        node = elements.firstChild()
        while node.isNull() == False:
            tag = node.toElement()
            name = tag.tagName()
            data["Version"] = tag.attribute("Version")
            data["Type"] = tag.attribute("Type")
            data["Name"] = tag.attribute("Name")
            data["MainScript"] = tag.attribute("MainScript")
            node = node.nextSibling()

        if name != "pcode_project":
            return False
        else:
            return name, data

    def loadProject(self, path, show, new):
        if not self.pcode.showProject(path):
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            pathDict = {
                "notes": os.path.join(path, "Data\\wpad.txt"),
                "log": os.path.join(path, "Data\\log.txt"),
                "session": os.path.join(path, "Data\\session.xml"),
                "usedata": os.path.join(path, "Data\\usedata.xml"),
                "windata": os.path.join(path, "Data\\windata.xml"),
                "projectdata": os.path.join(path, "Data\\projectdata.xml"),
                "snippetsdir": os.path.join(path, "Data\\templates"),
                "tempdir": os.path.join(path, "temp"),
                "backupdir": os.path.join(path, "temp\\Backup\\Files"),
                "backupfile": os.path.join(path, "temp\\Backup\\bak"),
                "sourcedir": os.path.join(path, "src"),
                "ropeFolder": os.path.join(path, "Rope"),
                "buildprofile": os.path.join(path, "Build\\profile.xml"),
                "ropeprofile": os.path.join(path, "Rope\\profile.xml"),
                "projectmainfile": os.path.join(path, "project.xml"),
                "root": path
            }
            if sys.platform == 'win32':
                pathDict["python"] = os.path.join(path,
                                                  "Venv\\Windows\\Scripts\\python.exe")
            elif sys.platform == 'darwin':  # needs fixing
                pathDict["python"] = os.path.join(path,
                                                  "Venv\\Mac\\Scripts\\python.exe")
            else:  # needs fixing
                pathDict["python"] = os.path.join(path,
                                                  "Venv\\Linux\\Scripts\\python.exe")

            try:
                project_data = self.readProject(path)
                if project_data == False:
                    QtGui.QApplication.restoreOverrideCursor()
                    message = QtGui.QMessageBox.warning(self, "Open Project",
                                                        "Failed:\n\n" + path)
                    return
                pathDict["name"] = project_data[1]["Name"]
                pathDict["type"] = project_data[1]["Type"]
                pathDict["mainscript"] = os.path.join(path, "src",
                                                      project_data[1]["MainScript"])
                if sys.platform == 'win32':
                    pathDict["builddir"] = os.path.join(path, "Build\\Windows")
                elif sys.platform == 'darwin':
                    pathDict["builddir"] = os.path.join(path, "Build\\Mac")
                else:
                    pathDict["builddir"] = os.path.join(path, "Build\\Linux")

                p_name = os.path.basename(path)

                projectWindow = EditorWindow(pathDict, self.library,
                                             self.busyWidget, self.settingsWidget.colorScheme,
                                             self.useData, self.app, self)
                if new:
                    projectWindow.editorTabWidget.loadfile(pathDict["mainscript"])
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
                QtGui.QApplication.restoreOverrideCursor()
                message = QtGui.QMessageBox.warning(self, "Failed Open",
                                                    "Problem opening project: \n\n" + str(err))
            QtGui.QApplication.restoreOverrideCursor()

    def closeProject(self):
        window = self.projectWindowStack.currentWidget()
        path = window.pathDict["root"]
        closed = window.closeWindow()
        if closed:
            self.pcode.removeProject(window)
            self.useData.OPENED_PROJECTS.remove(path)

    def createProject(self, data):
        self.createProjectThread.create(data)
        self.busyWidget.showBusy(True, "Creating project... please wait!")

    def finalizeNewProject(self):
        self.busyWidget.showBusy(False)
        if self.createProjectThread.error != False:
            message = QtGui.QMessageBox.warning(self, "New Project",
                                                "Failed to create project:\n\n" + self.createProjectThread.error)
        else:
            projectPath = os.path.normpath(
                self.createProjectThread.projectPath)  # otherwise an error will occur in rope
            self.loadProject(projectPath, True, True)
