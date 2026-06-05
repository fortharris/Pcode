import os
import sys
import traceback
import logging
import cx_Freeze
from cx_Freeze import Freezer
from Extensions.qt_bindings import QtCore, QtGui


class BuildThread(QtCore.QThread):
    def _interpreter_search_paths(self, interpreter):
        """Return existing module-search directories for *interpreter*.

        A venv interpreter lives under ``Scripts/`` (Windows) or ``bin/`` (Unix);
        stdlib and site-packages live under the venv root, not next to the exe.
        Also include ``sys.base_prefix`` paths when the selected interpreter is
        a venv shim. Only directories that exist on disk are returned.
        """
        py_path = os.path.dirname(os.path.abspath(interpreter))
        venv_root = os.path.dirname(py_path)
        candidates = [
            self.projectPathDict['sourcedir'],
            py_path,
            os.path.join(venv_root, "Lib"),
            os.path.join(venv_root, "Lib", "site-packages"),
            os.path.join(venv_root, "Include"),
            os.path.join(venv_root, "include"),
            os.path.join(py_path, "DLLs"),
            os.path.join(py_path, "libs"),
            os.path.join(py_path, "Lib"),
            os.path.join(py_path, "Lib", "site-packages"),
            os.path.join(py_path, "include"),
        ]
        base = getattr(sys, "base_prefix", None)
        if base and os.path.normpath(base) != os.path.normpath(venv_root):
            candidates.extend([
                base,
                os.path.join(base, "DLLs"),
                os.path.join(base, "Lib"),
                os.path.join(base, "Lib", "site-packages"),
                os.path.join(base, "include"),
            ])
        seen = set()
        existing = []
        for item in candidates:
            item = os.path.normpath(item)
            if item and os.path.isdir(item) and item not in seen:
                seen.add(item)
                existing.append(item)
        return existing

    def run(self):
        self.error = None

        if self.profile["base"] == "Console":
            base = "console"
        else:
            base = "Win32GUI"
        initScript = None

        if self.profile["icon"] in os.listdir(self.projectPathDict['iconsdir']):
            iconPath = os.path.join(self.projectPathDict['iconsdir'], self.profile["icon"])
        else:
            iconPath = None

        if self.profile["compress"] == 'Compress':
            compress = True
        else:
            compress = False

        if self.profile["optimize"] == "Don't Optimize":
            optimizeFlag = 0
        elif self.profile["optimize"] == 'Optimize':
            optimizeFlag = 1
        elif self.profile["optimize"] == "Optimize (Remove Doc Strings)":
            optimizeFlag = 2

        includes = self.profile["Includes"]
        excludes = self.profile["Excludes"]
        replacePaths = self.profile["Replace Paths"]
        binIncludes = self.profile["Bin Includes"]
        binExcludes = self.profile["Bin Excludes"]
        binPathIncludes = self.profile["Bin Path Includes"]
        binPathExcludes = self.profile["Bin Path Excludes"]
        includeFiles = self.profile["Include Files"]
        zipIncludes = self.profile["Zip Includes"]
        namespacePackages = self.profile["Namespace Packages"]
        constantsModules = self.profile["Constants Modules"]
        packages = self.profile["Packages"]

        # Options accepted by cx_Freeze 4.x but removed in modern releases
        # (appendScriptToExe/appendScriptToLibrary/copyDependentFiles/
        # namespacePackages/initScript-at-Freezer-level) are intentionally
        # dropped here; modern cx_Freeze handles dependency copying itself.
        try:
            executables = [cx_Freeze.Executable(
                           self.projectPathDict['mainscript'],
                           init_script=initScript,
                           base=base,
                           icon=iconPath)]
            if self.projectSettings["UseVirtualEnv"] == "True":
                venv_path = self.projectPathDict["venvdir"]
                path = [p for p in [
                    self.projectPathDict['sourcedir'],
                    os.path.join(venv_path, "Scripts"),
                    os.path.join(venv_path, "bin"),
                    os.path.join(venv_path, "Lib"),
                    os.path.join(venv_path, "Lib", "site-packages"),
                    os.path.join(venv_path, "Include"),
                ] if os.path.isdir(p)]
            else:
                path = self._interpreter_search_paths(
                    self.projectSettings["DefaultInterpreter"])
            extraPathList = []
            for i in path:
                extraPathList.extend(self.pathListFromDir(i))
            path.extend(extraPathList)

            freezer_kwargs = dict(
                target_dir=self.projectPathDict['builddir'],
                path=path,
                compress=compress,
                optimize=optimizeFlag,
                includes=includes,
                excludes=excludes,
                packages=packages,
                replace_paths=replacePaths,
                bin_includes=binIncludes,
                bin_excludes=binExcludes,
                bin_path_includes=binPathIncludes,
                bin_path_excludes=binPathExcludes,
                include_files=includeFiles,
                zip_includes=zipIncludes,
                silent=True,
                include_msvcr=sys.platform.startswith("win"),
            )
            if constantsModules:
                freezer_kwargs["constants_module"] = constantsModules
            freezer = Freezer(executables, **freezer_kwargs)
            freezer.freeze()

            # Module finder attribute was renamed to snake_case in modern
            # cx_Freeze; fall back across versions.
            badModules = (getattr(freezer.finder, "_bad_modules", None)
                          or getattr(freezer.finder, "_badModules", {}))
            names = list(badModules.keys())
            names.sort()
            self.missing = []
            for name in names:
                callers = list(badModules[name].keys())
                callers.sort()
                self.missing.append("? {0} imported from {1}".format
                                   (name, ", ".join(callers)))
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                                      exc_traceback)))
            self.error = str(err)
            
    def pathListFromDir(self, dirPath):
        """
        This is to get the list of module search paths from .pth files
        """
        pathList = []
        if not os.path.isdir(dirPath):
            return pathList
        for i in os.listdir(dirPath):
            path = os.path.join(dirPath, i)
            if os.path.isfile(path):
                if i.endswith('.pth'):
                    with open(path, 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        lineText = line.rstrip()
                        if os.path.exists(lineText):
                            pathList.append(lineText)
                        else:
                            fullPath = os.path.join(dirPath, lineText)
                            if os.path.exists(fullPath):
                                pathList.append(fullPath)
                                
        return pathList

    def build(self, profile, projectPathDict, projectSettings, useData):
        self.profile = profile
        self.projectPathDict = projectPathDict
        self.useData = useData
        self.projectSettings = projectSettings

        self.start()


class Build(QtGui.QWidget):
    def __init__(self, busyWidget, messagesWidget, projectPathDict, projectSettings, useData,
                 buildConfig, editorTabWidget, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.useData = useData
        self.projectPathDict = projectPathDict
        self.buildConfig = buildConfig
        self.projectSettings = projectSettings

        self.messagesWidget = messagesWidget
        self.busyWidget = busyWidget
        self.editorTabWidget = editorTabWidget
        self.busyWidget.cancel.connect(self.cancelBuild)

        self.buildThread = BuildThread()
        self.buildThread.finished.connect(self.buildFinished)

        self.durationTime = QtCore.QTime()

    def openDir(self):
        if os.path.exists(self.projectPathDict["builddir"]):
            os.startfile(self.projectPathDict["builddir"], 'explore')
        else:
            message = QtGui.QMessageBox.critical(self, "Open",
                                                 "Build folder is missing!")

    def cancelBuild(self):
        self.buildThread.exit()

    def build(self):
        saved = self.editorTabWidget.saveProject()
        if saved:
            profile = self.buildConfig.load()
            self.durationTime.start()
            self.buildThread.build(profile, self.projectPathDict, self.projectSettings, self.useData)
            self.busyWidget.showBusy(True)

    def buildFinished(self):
        elapsed = self.durationTime.elapsed()
        if elapsed >= 60000:
            min = int(elapsed / 60000)
            sec = int((elapsed - (60000 * min)) / 1000)
            elapsed = "{0}m{1}s".format(str(min), str(sec))
        else:
            elapsed = str(round(elapsed / 1000, 1)) + 's'
        self.busyWidget.showBusy(False)
        if self.buildThread.error:
            self.messagesWidget.addMessage(
                1, "Build Completed in {0} [Errors]".format(str(elapsed)), 
                    [self.buildThread.error])
        else:
            if len(self.buildThread.missing) > 0:
                self.messagesWidget.addMessage(
                    1, "Build Completed in {0} [missing modules]".format(elapsed), 
                        self.buildThread.missing)
            else:
                self.messagesWidget.addMessage(
                    0, "Build Completed in {0} ".format(elapsed), 
                        ["Build Completed Successfully!"])
