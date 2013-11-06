import os
from PyQt4 import QtGui, QtCore


class Start(QtGui.QLabel):

    def __init__(self, useData,  parent):
        QtGui.QLabel.__init__(self)

        self.pcode = parent
        self.useData = useData

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.setMargin(0)
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
                            QListView {
                                 show-decoration-selected: 1; /* make the selection span the entire width of the view */
                                 border: none;
                            }

                            QListView::item:hover {
                                 border: none;
                                 background: #E3E3E3;
                            }

                            QListView::item:selected:!active {
                                 border: 1px solid white;
                                 background: #E3E3E3;
                            }

                            QListView::item:selected:active {
                                 color: white;
                                 background: #3F3F3F;
                            }""")
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
        label.setFont(QtGui.QFont("Consolas", 20))
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
        label.setFont(QtGui.QFont("Consolas", 10))
        centralLayout.addWidget(label)

        centralLayout.addStretch(1)

        label = QtGui.QLabel("Recent Projects:")
        label.setStyleSheet("color: #0063A6; font: 12px;")
        centralLayout.addWidget(label)

        self.recentProjectsListWidget = QtGui.QListWidget()
        for i in useData.OPENED_PROJECTS:
            self.recentProjectsListWidget.addItem(QtGui.QListWidgetItem(i))
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

        style = """
            QLabel#mainlabel {background: #565656;
                    }

            QLabel#centerlabel {border-radius: 2px;
                background: #FFFFFF;
                     }

            QPushButton {min-width: 105;}
            """

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
        self.pcode.loadProject(item.text(), True)
