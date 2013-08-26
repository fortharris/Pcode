from PyQt4 import QtCore, QtGui


class WritePad(QtGui.QMainWindow):

    def __init__(self, path, name, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.setWindowTitle(name + " - Notes")
        self.resize(600, 300)
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                 (screen.height() - size.height()) / 2)

        self.path = path

        self.noteSaveTimer = QtCore.QTimer()
        self.noteSaveTimer.setSingleShot(True)
        self.noteSaveTimer.setInterval(1000)
        self.noteSaveTimer.timeout.connect(self.saveNotes)

        self.writePad = QtGui.QPlainTextEdit()
        self.writePad.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.writePad.setFont(QtGui.QFont("Ms Reference Sans Serif", 10.9))
        self.setCentralWidget(self.writePad)

        # load notes
        try:
            file = open(self.path, "r")
            self.writePad.setPlainText(file.read())
            file.close()
        except:
            file = open(path, "w")
            file.close()

        self.writePad.textChanged.connect(self.noteSaveTimer.start)
        
        self.setStyleSheet("""
        
                            QScrollBar:vertical{
                                padding: 0px;
                                border-left-width: 1px;
                                background: #ffffff;
                                width: 11px;
                            }

                            QScrollBar:horizontal{
                                padding: 0px;
                                border-top-width: 1px;
                                border-style:solid;
                                border: none;
                                background: #ffffff;
                                height: 10px;
                            }

                            QScrollBar::handle:vertical{
                                margin-top: 0px;
                                margin-bottom: 0px;
                                background: #B2B8BE;
                                border-radius: 0px;
                                border: none;
                                min-height: 30px;
                            }

                            QScrollBar::handle:horizontal{
                                margin-left: 0px;
                                margin-right: 0px;
                                background: #B2B8BE;
                                border-radius: 0px;
                                border: none;
                                min-width: 30px;
                            }
                            
                            QScrollBar::handle:hover{
                                background: #969ea7;
                            }
                            
                            QScrollBar::handle:pressed{
                                background: #717880;
                            }

                            QScrollBar::add-line:vertical,
                            QScrollBar::sub-line:vertical,
                            QScrollBar::add-page:vertical,
                            QScrollBar::sub-page:vertical,
                            QScrollBar::add-line:horizontal,
                            QScrollBar::sub-line:horizontal,
                            QScrollBar::add-page:horizontal,
                            QScrollBar::sub-page:horizontal{
                                background: none;
                                border: none;
                            }

                            QScrollBar::up-arrow:vertical {
                              border: none;
                              width: 10px;
                              height: 10px;
                              margin-left: 0px;
                              image: none;
                            }

                            QScrollBar::down-arrow:vertical {
                              border: none;
                              width: 10px;
                              height: 10px;
                              margin-left: 0px;
                              image: none;
                            }

                            QScrollBar::left-arrow:horizontal {
                              border: none;
                              width: 10px;
                              height: 10px;
                              image: none;
                            }

                            QScrollBar::right-arrow:horizontal {
                              border: none;
                              width: 10px;
                              height: 10px;
                              image: none;
                            }
                            
                            """)

    def saveNotes(self):
        file = open(self.path, "w")
        file.write(self.writePad.toPlainText())
        file.close()
