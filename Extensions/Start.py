import os
from Extensions.qt_bindings import QtGui, QtCore
from Extensions import StyleSheet


def _fixed_font(size):
    """A monospace font that exists on every platform (no hard-coded family)."""
    try:
        font = QtGui.QFontDatabase.systemFont(
            QtGui.QFontDatabase.SystemFont.FixedFont)
    except Exception:
        font = QtGui.QFont("monospace")
    font.setPointSize(size)
    return font


class Start(QtGui.QLabel):

    def __init__(self, useData,  parent):
        QtGui.QLabel.__init__(self)

        self.pcode = parent
        self.useData = useData
        self.palette_ = StyleSheet.resolve_palette(
            useData.SETTINGS.get("Theme", "Light"))

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setScaledContents(True)
        self.setObjectName("mainlabel")
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        vbox = QtGui.QVBoxLayout()
        mainLayout.addLayout(vbox)

        vbox.addStretch(1)

        centerLabel = QtGui.QLabel()
        centerLabel.setObjectName("centerlabel")
        centerLabel.setMinimumWidth(500)
        centerLabel.setMinimumHeight(300)
        centerLabel.setScaledContents(True)
        centerLabel.setStyleSheet("""
                            QListView {{
                                 show-decoration-selected: 1;
                                 border: 1px solid {border};
                                 background: {card};
                                 color: {text};
                            }}

                            QListView::item {{ min-height: 20px; }}

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

        shadowEffect = QtGui.QGraphicsDropShadowEffect()
        shadowEffect.setColor(QtGui.QColor("#000000"))
        shadowEffect.setXOffset(0)
        shadowEffect.setYOffset(0)
        shadowEffect.setBlurRadius(20)
        centerLabel.setGraphicsEffect(shadowEffect)

        centralLayout = QtGui.QVBoxLayout()
        centerLabel.setLayout(centralLayout)

        hbox = QtGui.QHBoxLayout()
        centralLayout.addLayout(hbox)

        label = QtGui.QLabel("Getting started...")
        label.setFont(_fixed_font(20))
        hbox.addWidget(label)

        hbox.addStretch(1)

        label = QtGui.QLabel()
        label.setScaledContents(True)
        label.setMaximumWidth(35)
        label.setMinimumWidth(35)
        label.setMaximumHeight(35)
        label.setMinimumHeight(35)
        label.setPixmap(QtGui.QPixmap(os.path.join("Resources", "images", "compass")))
        hbox.addWidget(label)

        frame = QtGui.QFrame()
        frame.setGeometry(1, 1, 1, 1)
        frame.setFrameShape(frame.HLine)
        frame.setFrameShadow(frame.Plain)
        centralLayout.addWidget(frame)

        label = QtGui.QLabel(
            "For the sake of convenience, most tasks are handled in the "
            "context of a project. Start editing your files by first "
            "creating a project or opening an existing one.")
        label.setWordWrap(True)
        label.setFont(_fixed_font(10))
        centralLayout.addWidget(label)

        centralLayout.addStretch(1)

        label = QtGui.QLabel("Recent Projects:")
        label.setStyleSheet(
            "color: %s; font: bold 12px;" % self.palette_["accent"])
        centralLayout.addWidget(label)

        self.recentProjectsListWidget = QtGui.QListWidget()
        if useData.OPENED_PROJECTS:
            for path in useData.OPENED_PROJECTS:
                item = QtGui.QListWidgetItem(os.path.basename(path))
                item.setToolTip(path)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, path)
                self.recentProjectsListWidget.addItem(item)
        else:
            placeholder = QtGui.QListWidgetItem(
                "No recent projects \u2014 create or open one to get started.")
            placeholder.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
            self.recentProjectsListWidget.addItem(placeholder)
        self.recentProjectsListWidget.itemDoubleClicked.connect(
            self.openProjectFromList)
        centralLayout.addWidget(self.recentProjectsListWidget)

        frame = QtGui.QFrame()
        frame.setGeometry(1, 1, 1, 1)
        frame.setFrameShape(frame.HLine)
        frame.setFrameShadow(frame.Plain)
        centralLayout.addWidget(frame)

        hbox = QtGui.QHBoxLayout()
        centralLayout.addLayout(hbox)

        openButton = QtGui.QPushButton("Open Project")
        openButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "wooden-box")))
        openButton.clicked.connect(self.openProject)
        hbox.addWidget(openButton)

        newButton = QtGui.QPushButton("New Project")
        newButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "inbox--plus")))
        newButton.clicked.connect(self.createProject)
        hbox.addWidget(newButton)

        hbox.addStretch(1)

        homePageButton = QtGui.QPushButton("Visit Homepage")
        homePageButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "Web")))
        homePageButton.clicked.connect(self.visitHomepage)
        hbox.addWidget(homePageButton)

        mainLayout.addStretch(1)

        p = self.palette_
        style = """
            QLabel#mainlabel {{ background: {bg}; }}

            QLabel#centerlabel {{
                border-radius: 4px;
                background: {card};
                color: {text};
            }}

            QLabel#centerlabel QLabel {{ color: {text}; }}

            QPushButton {{ min-width: 105px; }}
            """.format(bg=p["bg"], card=p["panelAlt"], text=p["text"])

        self.setStyleSheet(style)

    def visitHomepage(self):
        QtGui.QDesktopServices().openUrl(QtCore.QUrl(
            """https://github.com/fortharris/Pcode"""))

    def createProject(self):
        self.pcode.newProject()

    def openProject(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Project Folder", self.useData.getLastOpenedDir(), options)
        if directory:
            directory = os.path.normpath(directory)
            self.useData.saveLastOpenedDir(directory)
            self.pcode.loadProject(directory, True)

    def openProjectFromList(self, item):
        path = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if not path:
            return
        self.pcode.loadProject(path, True)
