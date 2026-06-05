import os

from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPalette
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu, QMessageBox,
    QPushButton, QToolButton, QVBoxLayout,
)

from Extensions import StyleSheet


class Favourites(QLabel):

    showMe = pyqtSignal()
    openFile = pyqtSignal(str)

    def __init__(self, favouritesList, messagesWidget, parent=None):
        super(Favourites, self).__init__(parent)

        self.setMinimumSize(600, 230)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.setBackgroundRole(QPalette.ColorRole.Window)
        self.setAutoFillBackground(True)

        self.messagesWidget = messagesWidget
        self.favouritesList = favouritesList

        self.manageFavAct = QAction(
            QIcon(os.path.join("Resources", "images", "settings")),
            "Manage Favourites", self, statusTip="Manage Favourites",
            triggered=self.showMe.emit)

        mainLayout = QVBoxLayout()

        hbox = QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QLabel("Manage Favourites")
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)

        hbox.addStretch(1)

        self.hideButton = QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.favouritesListWidget = QListWidget()
        mainLayout.addWidget(self.favouritesListWidget)

        hbox = QHBoxLayout()

        self.removeButton = QPushButton("Remove")
        self.removeButton.clicked.connect(self.removeFavourite)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.favouritesMenu = QMenu("Favourites")
        self.favouritesMenu.setIcon(QIcon(
            os.path.join("Resources", "images", "bookmarked_url")))
        self.loadFavourites()

    def removeFavourite(self):
        row = self.favouritesListWidget.currentRow()
        del self.favouritesList[row]
        self.loadFavourites()

    def addToFavourites(self, path):
        if path in self.favouritesList:
            pass
        else:
            self.favouritesList.append(path)
            self.favouritesList.sort()
            self.loadFavourites()
            self.messagesWidget.addMessage(0, "Favourites",
                                           ["'{0}' added!".format(path)])

    def loadFavourites(self):
        self.favouritesMenu.clear()
        self.favouritesListWidget.clear()
        if len(self.favouritesList) > 0:
            self.favouritesActionGroup = QActionGroup(self)
            self.favouritesActionGroup.triggered.connect(
                self.favouriteActivated)
            for i in self.favouritesList:
                action = QAction(QIcon(
                    os.path.join("Resources", "images", "star")), i, self)
                self.favouritesActionGroup.addAction(action)
                self.favouritesMenu.addAction(action)

                item = QListWidgetItem(i.strip())
                item.setToolTip(i)
                item.setSizeHint(QSize(20, 20))
                self.favouritesListWidget.addItem(item)

            self.favouritesMenu.addSeparator()
            self.favouritesMenu.addAction(self.manageFavAct)
            self.removeButton.setDisabled(False)
        else:
            action = QAction("No Favourites", self)
            self.favouritesMenu.addAction(action)
            self.favouritesMenu.addAction(action)
            self.removeButton.setDisabled(True)

    def favouriteActivated(self, action):
        path = action.text()
        if os.path.exists(path):
            self.openFile.emit(path)
        else:
            QMessageBox.warning(self, "Open", "File is no longer available.")
