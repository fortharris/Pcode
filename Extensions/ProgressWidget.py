from PyQt4 import QtCore, QtGui


class ProgressWidget(QtGui.QDialog):

    updateProgress = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.setFixedSize(220, 60)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMargin(0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        mainLabel = QtGui.QLabel()
        mainLabel.setStyleSheet("""
                  QLabel  {
                  border-radius: 5px;
                  background: black;
                  color: white;
                  border: 1px solid grey;
                  }

                  QProgressBar {
                     border: 1px solid #707070;
                     text-align: center;
                     font-size: 10px;
                     padding: 1px;

                     background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                                   stop:0 #333333, stop:1 #666666);
                 }

                 QProgressBar::chunk {
                      color: black;
                      border-radius: 0px;
                     background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                                   stop:0 #95c4f0, stop:1 #5d7a96);
                 }

                """)
        mainLayout.addWidget(mainLabel)

        vbox = QtGui.QVBoxLayout()
        mainLabel.setLayout(vbox)

        label = QtGui.QLabel("Exporting...")
        label.setStyleSheet("border: none;")
        vbox.addWidget(label)

        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0, 100)
        vbox.addWidget(self.progressBar)

        self.setLayout(mainLayout)

        self.updateProgress.connect(self.updateValue)

    def reset(self):
        self.progressBar.setValue(0)

    def updateValue(self, newValue):
        self.progressBar.setValue(newValue)
