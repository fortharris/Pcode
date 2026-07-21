import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import (
    QDesktopServices, QFont, QFontDatabase, QIcon, QPixmap,
)
from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout,
)

from Extensions import StyleSheet
from Extensions.version import GITHUB_URL, VERSION


def _ui_font(size, bold=False):
    """Prefer the app UI font; fall back to a fixed font if needed."""
    app_font = QFont()
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            app_font = QFont(app.font())
    except Exception:
        pass
    if app_font.pointSize() <= 0:
        try:
            app_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        except Exception:
            app_font = QFont("monospace")
    app_font.setPointSize(size)
    app_font.setBold(bold)
    return app_font


class Start(QLabel):

    def __init__(self, useData, parent):
        QLabel.__init__(self)

        self.pcode = parent
        self.useData = useData
        self.palette_ = StyleSheet.resolve_palette(
            StyleSheet.active_theme_name(useData.SETTINGS))

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setScaledContents(True)
        self.setObjectName("mainlabel")
        self.setAccessibleName("Start page")
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        vbox = QVBoxLayout()
        mainLayout.addLayout(vbox)

        vbox.addStretch(1)

        centerLabel = QLabel()
        centerLabel.setObjectName("centerlabel")
        centerLabel.setMinimumWidth(520)
        centerLabel.setMinimumHeight(320)
        centerLabel.setScaledContents(True)
        centerLabel.setAccessibleName("Getting started")
        centerLabel.setStyleSheet("""
                            QListView {{
                                 show-decoration-selected: 1;
                                 border: 1px solid {border};
                                 background: {card};
                                 color: {text};
                            }}

                            QListView::item {{ min-height: 22px; padding: 2px 4px; }}

                            QListView::item:hover {{
                                 border: none;
                                 background: {hover};
                            }}

                            QListView::item:selected:!active {{
                                 border: none;
                                 background: {hover};
                            }}

                            QListView::item:selected:active {{
                                 color: {accentText};
                                 background: {accent};
                            }}""".format(
            border=self.palette_["border"], card=self.palette_["panelAlt"],
            text=self.palette_["text"], hover=self.palette_["hover"],
            accent=self.palette_["accent"],
            accentText=self.palette_["accentText"]))
        vbox.addWidget(centerLabel)

        vbox.addStretch(2)

        centralLayout = QVBoxLayout()
        centralLayout.setContentsMargins(28, 24, 28, 24)
        centralLayout.setSpacing(10)
        centerLabel.setLayout(centralLayout)

        hbox = QHBoxLayout()
        centralLayout.addLayout(hbox)

        brand = QLabel("Pcode")
        brand.setFont(_ui_font(28, bold=True))
        brand.setAccessibleName("Pcode brand")
        hbox.addWidget(brand)

        hbox.addStretch(1)

        version = QLabel(VERSION)
        version.setFont(_ui_font(11))
        version.setStyleSheet("color: %s;" % self.palette_["textDim"])
        hbox.addWidget(version)

        label = QLabel()
        label.setScaledContents(True)
        label.setMaximumWidth(32)
        label.setMinimumWidth(32)
        label.setMaximumHeight(32)
        label.setMinimumHeight(32)
        label.setPixmap(QPixmap(os.path.join("Resources", "images", "compass")))
        hbox.addWidget(label)

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.HLine)
        frame.setFrameShadow(QFrame.Shadow.Plain)
        centralLayout.addWidget(frame)

        headline = QLabel("Open a project to start editing")
        headline.setFont(_ui_font(14, bold=True))
        centralLayout.addWidget(headline)

        label = QLabel(
            "Most tasks run in the context of a project. Create one or open "
            "an existing folder to edit, run, and manage your Python code.")
        label.setWordWrap(True)
        label.setFont(_ui_font(10))
        centralLayout.addWidget(label)

        centralLayout.addStretch(1)

        label = QLabel("Recent projects")
        label.setStyleSheet(
            "color: %s; font: bold 12px;" % self.palette_["accent"])
        centralLayout.addWidget(label)

        self.recentProjectsListWidget = QListWidget()
        self.recentProjectsListWidget.setAccessibleName("Recent projects")
        if useData.OPENED_PROJECTS:
            for path in useData.OPENED_PROJECTS:
                item = QListWidgetItem(os.path.basename(path))
                item.setToolTip(path)
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.recentProjectsListWidget.addItem(item)
        else:
            placeholder = QListWidgetItem(
                "No recent projects — create or open one to get started.")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.recentProjectsListWidget.addItem(placeholder)
        self.recentProjectsListWidget.itemDoubleClicked.connect(
            self.openProjectFromList)
        centralLayout.addWidget(self.recentProjectsListWidget)

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.HLine)
        frame.setFrameShadow(QFrame.Shadow.Plain)
        centralLayout.addWidget(frame)

        hbox = QHBoxLayout()
        centralLayout.addLayout(hbox)

        openButton = QPushButton("Open Project")
        openButton.setAccessibleName("Open project")
        openButton.setIcon(QIcon(os.path.join("Resources", "images", "wooden-box")))
        openButton.clicked.connect(self.openProject)
        hbox.addWidget(openButton)

        newButton = QPushButton("New Project")
        newButton.setAccessibleName("New project")
        newButton.setIcon(QIcon(os.path.join("Resources", "images", "inbox--plus")))
        newButton.clicked.connect(self.createProject)
        hbox.addWidget(newButton)

        hbox.addStretch(1)

        homePageButton = QPushButton("Homepage")
        homePageButton.setAccessibleName("Visit homepage")
        homePageButton.setIcon(QIcon(os.path.join("Resources", "images", "Web")))
        homePageButton.clicked.connect(self.visitHomepage)
        hbox.addWidget(homePageButton)

        mainLayout.addStretch(1)

        p = self.palette_
        style = """
            QLabel#mainlabel {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {bg}, stop:1 {panel});
            }}

            QLabel#centerlabel {{
                border: 1px solid {border};
                border-top: 3px solid {accent};
                background: {card};
                color: {text};
            }}

            QLabel#centerlabel QLabel {{ color: {text}; }}

            QPushButton {{
                min-width: 110px;
                padding: 5px 12px;
            }}
            """.format(
            bg=p["bg"], panel=p["panel"], border=p["border"],
            accent=p["accent"], card=p["panelAlt"], text=p["text"])

        self.setStyleSheet(style)

    def visitHomepage(self):
        QDesktopServices.openUrl(QUrl(GITHUB_URL))

    def createProject(self):
        self.pcode.newProject()

    def openProject(self):
        options = (QFileDialog.Option.DontResolveSymlinks
                   | QFileDialog.Option.ShowDirsOnly)
        directory = QFileDialog.getExistingDirectory(
            self, "Project Folder", self.useData.getLastOpenedDir(), options)
        if directory:
            directory = os.path.normpath(directory)
            self.useData.saveLastOpenedDir(directory)
            self.pcode.loadProject(directory, True)

    def openProjectFromList(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if not path:
            return
        self.pcode.loadProject(path, True)
