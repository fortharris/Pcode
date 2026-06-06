from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QPlainTextEdit

from Extensions.screen_utils import primary_screen_geometry


class WritePad(QMainWindow):

    def __init__(self, path, name, parent=None):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle(name + " - Notes")
        self.resize(600, 300)
        screen = primary_screen_geometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

        self.path = path
        self.setObjectName("writePad")

        self.noteSaveTimer = QTimer()
        self.noteSaveTimer.setSingleShot(True)
        self.noteSaveTimer.timeout.connect(self.saveNotes)

        self.writePad = QPlainTextEdit()
        self.writePad.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        _font = QFont("Ms Reference Sans Serif")
        _font.setPointSizeF(10.9)
        self.writePad.setFont(_font)
        self.setCentralWidget(self.writePad)

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                self.writePad.setPlainText(file.read())
        except Exception:
            with open(path, "w", encoding="utf-8"):
                pass

        self.writePad.textChanged.connect(self.startSaveTimer)

    def startSaveTimer(self):
        self.noteSaveTimer.start(1000)

    def saveNotes(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(self.writePad.toPlainText())
