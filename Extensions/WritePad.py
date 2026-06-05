from Extensions.qt_bindings import QtCore, QtGui, primary_screen_geometry


class WritePad(QtGui.QMainWindow):

    def __init__(self, path, name, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.setWindowTitle(name + " - Notes")
        self.resize(600, 300)
        screen = primary_screen_geometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

        self.path = path
        self.setObjectName("writePad")

        self.noteSaveTimer = QtCore.QTimer()
        self.noteSaveTimer.setSingleShot(True)
        self.noteSaveTimer.timeout.connect(self.saveNotes)

        self.writePad = QtGui.QPlainTextEdit()
        self.writePad.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        _font = QtGui.QFont("Ms Reference Sans Serif")
        _font.setPointSizeF(10.9)
        self.writePad.setFont(_font)
        self.setCentralWidget(self.writePad)

        # load notes
        try:
            with open(self.path, "r") as file:
                self.writePad.setPlainText(file.read())
        except Exception:
            with open(path, "w"):
                pass

        self.writePad.textChanged.connect(self.startSaveTimer)
        
    def startSaveTimer(self):
        self.noteSaveTimer.start(1000)

    def saveNotes(self):
        with open(self.path, "w") as file:
            file.write(self.writePad.toPlainText())
