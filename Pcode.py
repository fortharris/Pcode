import sys
import os
from PyQt4 import QtCore, QtGui

from Extensions.UseData import UseData
from Extensions.Library.Library import Library
from Extensions.About import About
from Extensions.Settings.SettingsWidget import SettingsWidget
from Extensions.Projects.Projects import Projects
from Extensions.BusyWidget import BusyWidget
from Extensions import StyleSheet
from Extensions.Start import Start
from Extensions.StackSwitcher import StackSwitcher


class Pcode(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowIcon(QtGui.QIcon(os.path.join("Resources","images","Icon")))
        self.setWindowTitle("Pcode - Loading...")

        screen = QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width() - 200, screen.height() - 400)
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (
            screen.height() - size.height()) / 2)
        self.lastWindowGeometry = self.geometry()

        self.setBaseColor()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing(0)
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        self.useData = UseData()
        self.library = Library(self.useData)
        self.busyWidget = BusyWidget(app, self.useData, self)

        self.projectWindowStack = QtGui.QStackedWidget()

        self.projectTitleBox = QtGui.QComboBox()
        self.projectTitleBox.setMinimumWidth(180)
        self.projectTitleBox.setStyleSheet(StyleSheet.projectTitleBoxStyle)
        self.projectTitleBox.setItemDelegate(QtGui.QStyledItemDelegate())
        self.projectTitleBox.currentIndexChanged.connect(self.projectChanged)
        self.projectTitleBox.activated.connect(self.projectChanged)

        self.settingsWidget = SettingsWidget(self.useData,
                                             self.projectWindowStack, self.library.codeViewer, self)
        self.settingsWidget.colorScheme.styleEditor(self.library.codeViewer)

        startWindow = Start(self.useData, self)
        self.addProject(startWindow, "Start",
                        "Start", os.path.join("Resources","images","flag-green"))

        self.projects = Projects(self.useData, self.busyWidget,
                                 self.library, self.settingsWidget, app,
                                 self.projectWindowStack, self.projectTitleBox, self)

        self.createActions()

        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(5, 3, 5, 3)
        mainLayout.addLayout(hbox)

        hbox.addStretch(1)

        self.pagesStack = QtGui.QStackedWidget()
        mainLayout.addWidget(self.pagesStack)

        self.projectSwitcher = StackSwitcher(self.pagesStack)
        self.projectSwitcher.setStyleSheet(StyleSheet.mainMenuStyle)
        hbox.addWidget(self.projectSwitcher)

        self.addPage(self.projectWindowStack, "EDITOR", QtGui.QIcon(
            os.path.join("Resources","images","hire-me")))

        self.addPage(self.library, "LIBRARY", QtGui.QIcon(
            os.path.join("Resources","images","library")))
        self.projectSwitcher.setDefault()

        hbox.addWidget(self.projectTitleBox)
        hbox.setSpacing(5)

        self.settingsButton = QtGui.QToolButton()
        self.settingsButton.setAutoRaise(True)
        self.settingsButton.setDefaultAction(self.settingsAct)
        hbox.addWidget(self.settingsButton)

        self.fullScreenButton = QtGui.QToolButton()
        self.fullScreenButton.setAutoRaise(True)
        self.fullScreenButton.setDefaultAction(self.showFullScreenAct)
        hbox.addWidget(self.fullScreenButton)

        self.aboutButton = QtGui.QToolButton()
        self.aboutButton.setAutoRaise(True)
        self.aboutButton.setDefaultAction(self.aboutAct)
        hbox.addWidget(self.aboutButton)

        self.install_shortcuts()

        if self.useData.settings["firstRun"] == 'False':
            self.restoreUiState()
        self.show()

        self.useData.settings["running"] = 'True'
        self.useData.settings["firstRun"] = 'False'
        self.useData.saveSettings()

    def createActions(self):
        self.aboutAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources","images","properties")),
            "About Pcode", self, statusTip="About Pcode",
            triggered=self.showAbout)

        self.showFullScreenAct = \
            QtGui.QAction(QtGui.QIcon(os.path.join("Resources","images","fullscreen")),
                          "Fullscreen", self,
                          statusTip="Fullscreen",
                          triggered=self.showFullScreenMode)

        self.settingsAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources","images","config")),
            "Settings", self,
            statusTip="Settings", triggered=self.showSettings)

    def addPage(self, pageWidget, name, iconPath):
        self.projectSwitcher.addButton(name=name, icon=iconPath)
        self.pagesStack.addWidget(pageWidget)

    def loadProject(self, path, show=False, new=False):
        self.projects.loadProject(path, show, new)

    def newProject(self):
        self.projects.newProjectDialog.exec_()

    def showProject(self, path):
        if not os.path.exists(path):
            message = QtGui.QMessageBox.warning(
                self, "Open Project", "Project cannot be be found!")
        else:
            if path in self.useData.OPENED_PROJECTS:
                for i in range(self.projectWindowStack.count() - 1):
                    window = self.projectWindowStack.widget(i)
                    p_path = window.pathDict["root"]
                    if os.path.samefile(path, p_path):
                        self.projectTitleBox.setCurrentIndex(i)
                        return True
        return False

    def addProject(self, window, name, type='Project', iconPath=None):
        self.projectWindowStack.insertWidget(0, window)
        if type == 'Project':
            self.projectTitleBox.insertItem(0, QtGui.QIcon(
                os.path.join("Resources","images","project")), name, [window, type])
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
            if title.startswith(window.pathDict["sourcedir"]):
                src_dir = window.pathDict["sourcedir"]
                n = title.partition(src_dir)[-1]
                title = 'Pcode - ' + n
            else:
                title = "Pcode - " + title
        self.setWindowTitle(title)

    def showAbout(self):
        aboutPane = About(self)
        aboutPane.exec_()

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
            self.setWindowState(QtCore.Qt.WindowMaximized)
        else:
            self.setGeometry(settings.value("geometry"))
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
        app.closeAllWindows()

        event.accept()

    def setBaseColor(self):
        baseColor = "#EFEFF2"

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(baseColor))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(baseColor))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(baseColor))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(baseColor))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(baseColor))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.setPalette(palette)

    def install_shortcuts(self):
        shortcuts = self.useData.CUSTOM_DEFAULT_SHORTCUTS

        self.shortFullscreen = QtGui.QShortcut(
            shortcuts["Ide"]["Fullscreen"][0], self)
        self.shortFullscreen.activated.connect(self.showFullScreenMode)

app = QtGui.QApplication(sys.argv)
app.setStyleSheet(StyleSheet.globalStyle)

splash = QtGui.QSplashScreen(QtGui.QPixmap(os.path.join("Resources","images","splash")))
splash.show()

main = Pcode()

splash.finish(main)

sys.exit(app.exec_())
