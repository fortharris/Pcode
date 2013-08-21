from PyQt4 import QtGui


class Notification(QtGui.QLabel):

    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)

        self.setMinimumHeight(25)
        self.setMargin(5)

        self.setStyleSheet("""background: #1A1A1A;
                                color: white;
                                border: 1px solid #72A4CE;
                                border-radius: 0px;
                                border-left: 5px solid #72A4CE;
                            """)

    def mousePressEvent(self, event):
        self.hide()

    def showMessage(self, mess):
        self.setText(mess)
        self.show()
        self.adjustSize()
