import Extensions.qscintilla_compat  # noqa: F401 — before any Qsci editor import

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel, QMessageBox,
    QSplashScreen, QStackedWidget, QStyledItemDelegate, QToolButton,
    QVBoxLayout, QWidget,
)

import sys
import os
import logging

from Extensions.screen_utils import primary_screen_geometry

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
from Extensions.QuickOpen import QuickOpen, index_project_files


class Pcode(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        self.app = app

        self.setWindowIcon(
            QIcon(os.path.join("Resources", "images", "Icon")))
        self.setWindowTitle("Pcode - Loading...")

        screen = primary_screen_geometry()
        self.resize(screen.width() - 200, screen.height() - 200)
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))
        self.lastWindowGeometry = self.geometry()

        mainLayout = QVBoxLayout()
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

        if self.useData.SETTINGS.get("UI") == "System":
            StyleSheet.apply_system(app)
        else:
            StyleSheet.apply_theme(
                app, StyleSheet.active_theme_name(self.useData.SETTINGS))
        StyleSheet.apply_ui_font_scale(
            app, self.useData.SETTINGS.get("UIFontScale", "100"))

        self.projectWindowStack = QStackedWidget()
        self.projectWindowStack.setAccessibleName("Project windows")

        self.projectTitleBox = QComboBox()
        self.projectTitleBox.setAccessibleName("Open projects")
        self.projectTitleBox.setMinimumWidth(160)
        self.projectTitleBox.setMaximumWidth(280)
        self.projectTitleBox.setItemDelegate(QStyledItemDelegate())
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

        hbox = QHBoxLayout()
        hbox.setContentsMargins(8, 4, 8, 4)
        hbox.setSpacing(6)
        mainLayout.addLayout(hbox)

        self.logoLabel = QLabel()
        self.logoLabel.setAccessibleName("Pcode logo")
        logoPix = QPixmap(os.path.join("Resources", "images", "Icon"))
        if not logoPix.isNull():
            self.logoLabel.setPixmap(logoPix.scaled(
                20, 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        hbox.addWidget(self.logoLabel)

        self.titleLabel = QLabel("Pcode")
        self.titleLabel.setAccessibleName("Pcode")
        titleFont = self.titleLabel.font()
        titleFont.setBold(True)
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setContentsMargins(2, 0, 10, 0)
        hbox.addWidget(self.titleLabel)

        hbox.addWidget(self.projectTitleBox)

        hbox.addStretch(1)

        self.pagesStack = QStackedWidget()
        mainLayout.addWidget(self.pagesStack)

        self.projectSwitcher = StackSwitcher(self.pagesStack)
        self.projectSwitcher.setObjectName("pageSwitcher")
        hbox.addWidget(self.projectSwitcher)

        self.addPage(self.projectWindowStack, "EDITOR", QIcon(
            os.path.join("Resources", "images", "hire-me")),
            toolTip="Editor", showText=False)

        self.addPage(self.library, "LIBRARY", QIcon(
            os.path.join("Resources", "images", "library")),
            toolTip="Library", showText=False)
        self.projectSwitcher.setDefault()

        self.settingsButton = QToolButton()
        self.settingsButton.setAutoRaise(True)
        self.settingsButton.setDefaultAction(self.settingsAct)
        self.settingsButton.setToolTip("Settings")
        self.settingsButton.setAccessibleName("Settings")
        hbox.addWidget(self.settingsButton)

        self.fullScreenButton = QToolButton()
        self.fullScreenButton.setAutoRaise(True)
        self.fullScreenButton.setDefaultAction(self.showFullScreenAct)
        self.fullScreenButton.setToolTip("Toggle fullscreen")
        self.fullScreenButton.setAccessibleName("Toggle fullscreen")
        hbox.addWidget(self.fullScreenButton)

        self.aboutButton = QToolButton()
        self.aboutButton.setAutoRaise(True)
        self.aboutButton.setDefaultAction(self.aboutAct)
        self.aboutButton.setToolTip("About Pcode")
        self.aboutButton.setAccessibleName("About Pcode")
        hbox.addWidget(self.aboutButton)

        self.commandPalette = CommandPalette(self)
        self.quickOpen = QuickOpen(self)

        self.setKeymap()
        self.refreshChromeStyles()
        self._connectSystemThemeWatcher()

        if self.useData.bootstrap_bool("firstRun", True):
            self.showMaximized()
        else:
            self.restoreUiState()

        self.useData.settings["running"] = 'True'
        self.useData.settings["firstRun"] = 'False'
        self.useData.saveSettings()

    def createActions(self):
        self.aboutAct = QAction(
            QIcon(os.path.join("Resources", "images", "properties")),
            "About Pcode", self, statusTip="About Pcode",
            triggered=self.showAbout)

        self.showFullScreenAct = \
            QAction(
                QIcon(os.path.join("Resources", "images", "fullscreen")),
                "Fullscreen", self,
                statusTip="Fullscreen",
                          triggered=self.showFullScreenMode)

        self.settingsAct = QAction(
            QIcon(os.path.join("Resources", "images", "config")),
            "Settings", self,
            statusTip="Settings", triggered=self.showSettings)

    def addPage(self, pageWidget, name, iconPath, toolTip=None, showText=True):
        self.projectSwitcher.addButton(
            name=name, icon=iconPath, toolTip=toolTip or name, showText=showText)
        self.pagesStack.addWidget(pageWidget)

    def loadProject(self, path, show=False, new=False):
        self.projects.loadProject(path, show, new)

    def newProject(self):
        self.projects.newProjectDialog.exec()

    def showProject(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(
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
            self.projectTitleBox.insertItem(0, QIcon(
                os.path.join("Resources", "images", "project")), name, [window, type])
        else:
            self.projectTitleBox.insertItem(0, QIcon(
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
        settings = QSettings("Clean Code Inc.", "Pcode")
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.geometry())
        settings.setValue("lsplitter", self.library.mainSplitter.saveState())
        settings.setValue("snippetsMainsplitter",
                          self.settingsWidget.snippetEditor.mainSplitter.saveState())
        settings.setValue("windowMaximized", self.isMaximized())
        settings.endGroup()

    def restoreUiState(self):
        settings = QSettings("Clean Code Inc.", "Pcode")
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

        self.shortFullscreen = QShortcut(
            shortcuts["Ide"]["Fullscreen"], self)
        self.shortFullscreen.activated.connect(self.showFullScreenMode)

        self.shortCommandPalette = QShortcut(
            QKeySequence("Ctrl+Shift+P"), self)
        self.shortCommandPalette.activated.connect(self.showCommandPalette)

        self.shortQuickOpen = QShortcut(
            QKeySequence("Ctrl+P"), self)
        self.shortQuickOpen.activated.connect(self.showQuickOpen)

    def showCommandPalette(self):
        self.commandPalette.setCommands(self.buildCommands())
        self.commandPalette.launch()

    def showQuickOpen(self):
        window = self._activeProjectWindow()
        if window is None:
            return
        root = window.projectPathDict.get("sourcedir") or ""
        files = index_project_files(root)
        etw = window.editorTabWidget
        self.quickOpen.launch(files, etw.loadfile)

    def _activeProjectWindow(self):
        window = self.projectWindowStack.currentWidget()
        if window is not None and hasattr(window, "editorTabWidget"):
            return window
        return None

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
        window = self._activeProjectWindow()
        if window is not None:
            etw = window.editorTabWidget
            sw = window.bottomStackSwitcher
            commands.extend([
                ("Quick Open\u2026", self.showQuickOpen),
                ("Save All", window.saveAll),
                ("Save File", etw.save),
                ("Run Project", window.runProject),
                ("Run File", window.runFile),
                ("Close Project", window.closeProject),
                ("Find", window.showFinderWidget),
                ("Replace", window.showReplaceWidget),
                ("Find in Files", window.showFindInFilesWidget),
                ("Toggle Outline", window.toggleOutline),
                ("Go to Line", lambda: window.gotoLineAct.trigger()),
                ("Go to Definition", etw.refactor.findDefinition),
                ("Configure Project", lambda: window.configureAct.trigger()),
                ("Rename Symbol", etw.refactor.renameAttribute),
                ("Panel: Output",
                 lambda: sw.setCurrentWidget(window.runWidget)),
                ("Panel: Alerts",
                 lambda: sw.setCurrentWidget(window.assistantWidget)),
                ("Panel: Messages",
                 lambda: sw.setCurrentWidget(window.messagesWidget)),
                ("Panel: Bookmarks",
                 lambda: sw.setCurrentWidget(window.bookmarkWidget)),
                ("Panel: Tasks",
                 lambda: sw.setCurrentWidget(window.tasksWidget)),
                ("Git: Refresh", lambda: window.gitPanel.refresh()),
                ("Git: Stage File", lambda: window.gitPanel.stage_selected()),
                ("Git: Commit", lambda: window.gitPanel.commit()),
                ("Git: Amend", lambda: window.gitPanel.amend()),
                ("Git: Fetch", lambda: window.gitPanel.fetch()),
                ("Git: Pull", lambda: window.gitPanel.pull()),
                ("Git: Push", lambda: window.gitPanel.push()),
                ("Git: Log", lambda: window.gitPanel.show_log()),
                ("Git: Diff at Cursor", lambda: window.gitPanel.diff_at_cursor()),
                ("Debug: Continue", window.debugContinue),
                ("Debug: Step Over", window.debugStepOver),
                ("Debug: Step Into", window.debugStepInto),
                ("Debug: Step Out", window.debugStepOut),
            ])
            if window.projectPathDict.get("type") == "Desktop Application":
                commands.append(("Build Project", window.buildProject))
            for path in window.projectData.get("recentfiles", [])[:8]:
                if not path:
                    continue
                label = "Recent File: {0}".format(os.path.basename(path))
                commands.append(
                    (label, lambda p=path: etw.loadfile(p)))
            keymap_dispatch = {
                "Find": window.showFinderWidget,
                "Replace": window.showReplaceWidget,
                "Go-to-Line": lambda: window.gotoLineAct.trigger(),
                "Save-File": etw.save,
                "Save-All": window.saveAll,
                "Run-Project": window.runProject,
                "Run-File": window.runFile,
            }
            for name, shortcut in self.useData.CUSTOM_SHORTCUTS.get("Ide", {}).items():
                handler = keymap_dispatch.get(name)
                if shortcut and handler is not None:
                    label = "Keymap: {0} ({1})".format(
                        name.replace("-", " "), shortcut)
                    commands.append((label, handler))
            editor_dispatch = {
                "Comment": etw.comment,
                "Uncomment": etw.unComment,
            }
            for name, value in self.useData.CUSTOM_SHORTCUTS.get(
                    "Editor", {}).items():
                shortcut = value[0] if isinstance(value, (list, tuple)) else value
                handler = editor_dispatch.get(name)
                if shortcut and handler is not None:
                    label = "Keymap (Editor): {0} ({1})".format(
                        name.replace("-", " "), shortcut)
                    commands.append((label, handler))
        for i in range(self.projectWindowStack.count() - 1):
            proj_window = self.projectWindowStack.widget(i)
            if not hasattr(proj_window, "projectPathDict"):
                continue
            root = proj_window.projectPathDict["root"]
            pname = proj_window.projectPathDict.get(
                "name", os.path.basename(root))
            commands.append(
                ("Switch Project: {0}".format(pname),
                 lambda idx=i: self.projectTitleBox.setCurrentIndex(idx)))
        for path in self.useData.OPENED_PROJECTS[:5]:
            name = os.path.basename(path)
            commands.append(
                ("Recent: {0}".format(name),
                 lambda p=path: self.loadProject(p, True)))
        return commands

    def applyTheme(self, name):
        self.useData.SETTINGS["Theme"] = name
        # Theme picker only drives chrome when UI is Custom (incl. Theme=System).
        if self.useData.SETTINGS.get("UI", "Custom") != "Custom":
            return
        StyleSheet.apply_theme(self.app, name)
        self.refreshChromeStyles()
        try:
            self.settingsWidget.colorScheme.restyleAllEditors()
        except Exception:
            pass

    def applyUiMode(self, mode):
        """Apply Custom or System chrome. ``mode`` is ``Custom`` or ``System``."""
        if mode == "Native":
            mode = "System"
        self.useData.SETTINGS["UI"] = mode
        StyleSheet.apply_theme(
            self.app, StyleSheet.active_theme_name(self.useData.SETTINGS))
        self.refreshChromeStyles()
        uses_chrome = StyleSheet.uses_themed_chrome(self.useData.SETTINGS)
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            if hasattr(window, "editorTabWidget"):
                window.editorTabWidget.adjustToStyleSheet(uses_chrome)
        try:
            self.settingsWidget.colorScheme.restyleAllEditors()
        except Exception:
            pass

    def refreshChromeStyles(self):
        """Apply or clear per-widget chrome stylesheets for the current UI mode."""
        custom = StyleSheet.uses_themed_chrome(self.useData.SETTINGS)
        self.projectTitleBox.setStyleSheet(
            StyleSheet.chrome_style("projectTitleBoxStyle", custom))
        self.projectSwitcher.setStyleSheet(
            StyleSheet.chrome_style("mainMenuStyle", custom))
        # Quiet monochrome icons for top-bar page switcher + utilities.
        try:
            from Extensions.Icons import tinted_icon
            for button, name in zip(
                    self.projectSwitcher.buttonGroup.buttons(),
                    ("hire-me", "library")):
                button.setIcon(tinted_icon(name))
            self.settingsButton.setIcon(tinted_icon("config"))
            self.fullScreenButton.setIcon(tinted_icon("Fullscreen"))
            self.aboutButton.setIcon(tinted_icon("properties"))
        except Exception:
            pass
        for i in range(self.projectWindowStack.count()):
            window = self.projectWindowStack.widget(i)
            if hasattr(window, "refreshChromeStyles"):
                window.refreshChromeStyles(custom)
            elif hasattr(window, "bottomStackSwitcher"):
                window.bottomStackSwitcher.setStyleSheet(
                    StyleSheet.chrome_style("bottomSwitcherStyle", custom))

    def _connectSystemThemeWatcher(self):
        """Re-apply System theme when the OS light/dark preference changes."""
        try:
            hints = self.app.styleHints()
            if hints is None:
                return
            hints.colorSchemeChanged.connect(self._onSystemColorSchemeChanged)
        except Exception:
            pass

    def _onSystemColorSchemeChanged(self, _scheme=None):
        follows_system = (
            self.useData.SETTINGS.get("UI") == "System"
            or (
                self.useData.SETTINGS.get("UI", "Custom") == "Custom"
                and self.useData.SETTINGS.get("Theme") == "System"
            )
        )
        if not follows_system:
            return
        StyleSheet.apply_theme(
            self.app, StyleSheet.active_theme_name(self.useData.SETTINGS))
        self.refreshChromeStyles()
        try:
            self.settingsWidget.colorScheme.restyleAllEditors()
        except Exception:
            pass

    def openProjectDialog(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Project Folder", self.useData.getLastOpenedDir(),
            QFileDialog.Option.ShowDirsOnly
            | QFileDialog.Option.DontResolveSymlinks)
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

    app = QApplication(sys.argv)

    from Extensions import ErrorHandler
    ErrorHandler.install()

    splash = QSplashScreen(
        QPixmap(os.path.join("Resources", "images", "splash")))
    splash.show()

    window = Pcode()

    splash.finish(window)

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
