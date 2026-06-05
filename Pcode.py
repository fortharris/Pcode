import sys
import os
import logging

from Extensions.qt_bindings import QtCore, QtGui, primary_screen_geometry

from Extensions.UseData import UseData
from Extensions.Library.Library import Library
from Extensions.About import About
from Extensions.Settings.SettingsWidget import SettingsWidget
from Extensions.Projects.Projects import Projects
from Extensions.BusyWidget import BusyWidget
from Extensions import StyleSheet
from Extensions.Start import Start
from Extensions.StackSwitcher import StackSwitcher
from Extensions.CommandPalette import CommandPalette


class Pcode(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        app = QtGui.QApplication.instance()
        if app is None:
            app = QtGui.QApplication(sys.argv)
        self.app = app

        self.setWindowIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "Icon")))
        self.setWindowTitle("Pcode - Loading...")

        screen = primary_screen_geometry()
        self.resize(screen.width() - 200, screen.height() - 200)
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))
        self.lastWindowGeometry = self.geometry()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.useData = UseData()

        # Re-point logging from the early startup log (configured in main())
        # to the workspace log now that the workspace path is known.
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=self.useData.appPathDict["logfile"],
                            level=logging.DEBUG, force=True)
        if sys.version_info.major < 3:
            logging.error("This application requires Python 3")
            sys.exit(1)

        self.library = Library(self.useData)
        self.busyWidget = BusyWidget(app, self.useData, self)

        if self.useData.SETTINGS["UI"] == "Custom":
            StyleSheet.apply_theme(app, self.useData.SETTINGS.get("Theme", "Light"))

        self.projectWindowStack = QtGui.QStackedWidget()

        self.projectTitleBox = QtGui.QComboBox()
        self.projectTitleBox.setMinimumWidth(180)
        self.projectTitleBox.setStyleSheet(StyleSheet.projectTitleBoxStyle)
        self.projectTitleBox.setItemDelegate(QtGui.QStyledItemDelegate())
        self.projectTitleBox.currentIndexChanged.connect(self.projectChanged)
        self.projectTitleBox.activated.connect(self.projectChanged)

        self.settingsWidget = SettingsWidget(self.useData, app,
                                             self.projectWindowStack, self.library.codeViewer, self)
        self.settingsWidget.colorScheme.styleEditor(self.library.codeViewer)

        startWindow = Start(self.useData, self)
        self.addProject(startWindow, "Start",
                        "Start", os.path.join("Resources", "images", "flag-green"))

        self.projects = Projects(self.useData, self.busyWidget,
                                 self.library, self.settingsWidget, app,
                                 self.projectWindowStack, self.projectTitleBox, self)

        self.createActions()

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(5, 3, 5, 3)
        mainLayout.addLayout(hbox)

        self.logoLabel = QtGui.QLabel()
        logoPix = QtGui.QPixmap(os.path.join("Resources", "images", "Icon"))
        if not logoPix.isNull():
            self.logoLabel.setPixmap(logoPix.scaled(
                22, 22,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation))
        hbox.addWidget(self.logoLabel)

        self.titleLabel = QtGui.QLabel("Pcode")
        titleFont = self.titleLabel.font()
        titleFont.setBold(True)
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setContentsMargins(4, 0, 8, 0)
        hbox.addWidget(self.titleLabel)

        hbox.addStretch(1)

        self.pagesStack = QtGui.QStackedWidget()
        mainLayout.addWidget(self.pagesStack)

        self.projectSwitcher = StackSwitcher(self.pagesStack)
        self.projectSwitcher.setStyleSheet(StyleSheet.mainMenuStyle)
        hbox.addWidget(self.projectSwitcher)

        self.addPage(self.projectWindowStack, "EDITOR", QtGui.QIcon(
            os.path.join("Resources", "images", "hire-me")))

        self.addPage(self.library, "LIBRARY", QtGui.QIcon(
            os.path.join("Resources", "images", "library")))
        self.projectSwitcher.setDefault()

        hbox.addWidget(self.projectTitleBox)
        hbox.setSpacing(5)

        self.settingsButton = QtGui.QToolButton()
        self.settingsButton.setAutoRaise(True)
        self.settingsButton.setDefaultAction(self.settingsAct)
        self.settingsButton.setToolTip("Settings")
        hbox.addWidget(self.settingsButton)

        self.fullScreenButton = QtGui.QToolButton()
        self.fullScreenButton.setAutoRaise(True)
        self.fullScreenButton.setDefaultAction(self.showFullScreenAct)
        self.fullScreenButton.setToolTip("Toggle fullscreen")
        hbox.addWidget(self.fullScreenButton)

        self.aboutButton = QtGui.QToolButton()
        self.aboutButton.setAutoRaise(True)
        self.aboutButton.setDefaultAction(self.aboutAct)
        self.aboutButton.setToolTip("About Pcode")
        hbox.addWidget(self.aboutButton)

        self.commandPalette = CommandPalette(self)

        self.setKeymap()

        if self.useData.settings["firstRun"] == 'True':
            self.showMaximized()
        else:
            self.restoreUiState()

        self.useData.settings["running"] = 'True'
        self.useData.settings["firstRun"] = 'False'
        self.useData.saveSettings()

    def createActions(self):
        self.aboutAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "properties")),
            "About Pcode", self, statusTip="About Pcode",
            triggered=self.showAbout)

        self.showFullScreenAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "fullscreen")),
                "Fullscreen", self,
                statusTip="Fullscreen",
                          triggered=self.showFullScreenMode)

        self.settingsAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "config")),
            "Settings", self,
            statusTip="Settings", triggered=self.showSettings)

    def addPage(self, pageWidget, name, iconPath):
        self.projectSwitcher.addButton(name=name, icon=iconPath)
        self.pagesStack.addWidget(pageWidget)

    def loadProject(self, path, show=False, new=False):
        self.projects.loadProject(path, show, new)

    def newProject(self):
        self.projects.newProjectDialog.exec()

    def showProject(self, path):
        if not os.path.exists(path):
            message = QtGui.QMessageBox.warning(
                self, "Open Project", "Project cannot be be found!")
        else:
            if path in self.useData.OPENED_PROJECTS:
                for i in range(self.projectWindowStack.count() - 1):
                    window = self.projectWindowStack.widget(i)
                    p_path = window.projectPathDict["root"]
                    if os.path.samefile(path, p_path):
                        self.projectTitleBox.setCurrentIndex(i)
                        return True
        return False

    def addProject(self, window, name, type='Project', iconPath=None):
        self.projectWindowStack.insertWidget(0, window)
        if type == 'Project':
            self.projectTitleBox.insertItem(0, QtGui.QIcon(
                os.path.join("Resources", "images", "project")), name, [window, type])
        else:
            self.projectTitleBox.insertItem(0, QtGui.QIcon(
                iconPath), name, [window, type])

    def projectChanged(self, index):
        data = self.projectTitleBox.itemData(index)
        window = data[0]
        windowType = data[1]
        if windowType == "Start":
            self.setWindowTitle("Pcode - Start")
        elif windowType == "Project":
            title = window.editorTabWidget.getEditorData("filePath")
            self.updateWindowTitle(title)
        self.projectWindowStack.setCurrentWidget(window)

    def removeProject(self, window):
        for index in range(self.projectTitleBox.count() - 1):
            data = self.projectTitleBox.itemData(index)
            windowWidget = data[0]
            if windowWidget == window:
                self.projectWindowStack.removeWidget(window)
                self.projectTitleBox.removeItem(index)

    def updateWindowTitle(self, title):
        if title is None:
            title = "Pcode - " + "Unsaved"
        else:
            window = self.projectTitleBox.itemData(
                self.projectTitleBox.currentIndex())[0]
            if title.startswith(window.projectPathDict["sourcedir"]):
                src_dir = window.projectPathDict["sourcedir"]
                n = title.partition(src_dir)[-1]
                title = 'Pcode - ' + n
            else:
                title = "Pcode - " + title
        self.setWindowTitle(title)

    def showAbout(self):
        aboutPane = About(self)
        aboutPane.exec()

    def showSettings(self):
        self.settingsWidget.show()

    def showFullScreenMode(self):
        if self.isFullScreen():
            self.showNormal()
            self.setGeometry(self.lastWindowGeometry)
        else:
            # get current size ahd show Fullscreen
            # so we can later restore to proper position
            self.lastWindowGeometry = self.geometry()
            self.showFullScreen()

    def saveUiState(self):
        settings = QtCore.QSettings("Clean Code Inc.", "Pcode")
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.geometry())
        settings.setValue("lsplitter", self.library.mainSplitter.saveState())
        settings.setValue("snippetsMainsplitter",
                          self.settingsWidget.snippetEditor.mainSplitter.saveState())
        settings.setValue("windowMaximized", self.isMaximized())
        settings.endGroup()

    def restoreUiState(self):
        settings = QtCore.QSettings("Clean Code Inc.", "Pcode")
        settings.beginGroup("MainWindow")
        if settings.value("windowMaximized", True, type=bool):
            self.showMaximized()
        else:
            self.setGeometry(settings.value("geometry"))
            self.show()
        self.library.mainSplitter.restoreState(settings.value("lsplitter"))
        self.settingsWidget.snippetEditor.mainSplitter.restoreState(
            settings.value("snippetsMainsplitter"))
        settings.endGroup()

    def closeEvent(self, event):
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            closed = window.closeWindow()
            if not closed:
                self.projectTitleBox.setCurrentIndex(i)
                event.ignore()
                return
            else:
                pass
        self.saveUiState()
        self.useData.saveUseData()
        self.app.closeAllWindows()

        event.accept()

    def setKeymap(self):
        shortcuts = self.useData.CUSTOM_SHORTCUTS

        self.shortFullscreen = QtGui.QShortcut(
            shortcuts["Ide"]["Fullscreen"], self)
        self.shortFullscreen.activated.connect(self.showFullScreenMode)

        self.shortCommandPalette = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+Shift+P"), self)
        self.shortCommandPalette.activated.connect(self.showCommandPalette)

    def showCommandPalette(self):
        self.commandPalette.setCommands(self.buildCommands())
        self.commandPalette.launch()

    def buildCommands(self):
        commands = [
            ("New Project", self.newProject),
            ("Open Project\u2026", self.openProjectDialog),
            ("Settings", self.showSettings),
            ("Toggle Fullscreen", self.showFullScreenMode),
            ("Go to Editor", lambda: self.projectSwitcher.setButton("EDITOR")),
            ("Go to Library", lambda: self.projectSwitcher.setButton("LIBRARY")),
            ("Theme: Light", lambda: self.applyTheme("Light")),
            ("Theme: Dark", lambda: self.applyTheme("Dark")),
            ("Theme: System", lambda: self.applyTheme("System")),
            ("About Pcode", self.showAbout),
        ]
        return commands

    def applyTheme(self, name):
        self.useData.SETTINGS["Theme"] = name
        if self.useData.SETTINGS["UI"] == "Custom":
            StyleSheet.apply_theme(self.app, name)

    def openProjectDialog(self):
        directory = QtGui.QFileDialog.getExistingDirectory(
            self, "Project Folder", self.useData.getLastOpenedDir(),
            QtGui.QFileDialog.ShowDirsOnly
            | QtGui.QFileDialog.DontResolveSymlinks)
        if directory:
            directory = os.path.normpath(directory)
            self.useData.saveLastOpenedDir(directory)
            self.loadProject(directory, True)

def main():
    # Resources are resolved relative to the working directory, so anchor it to
    # this file's location regardless of where the entry point is launched from.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Configure logging before anything else so errors during early startup
    # (before the workspace log path is known) are still captured. Pcode
    # re-points this to the workspace LOG.txt once UseData has loaded.
    import tempfile
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=os.path.join(tempfile.gettempdir(), "pcode-startup.log"),
        level=logging.DEBUG)

    app = QtGui.QApplication(sys.argv)

    from Extensions import ErrorHandler
    ErrorHandler.install()

    splash = QtGui.QSplashScreen(
        QtGui.QPixmap(os.path.join("Resources", "images", "splash")))
    splash.show()

    window = Pcode()

    splash.finish(window)

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
