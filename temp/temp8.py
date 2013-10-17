#
# Python implemetation of a scoreboard for the Volta River Authority
# Author: Amoatey Harrison
# Email: fortharris@gmail.com, fortharris@yahoo.co.uk
#

import sys
import re
import os
from PyQt4 import QtCore, QtGui, QtNetwork

from FrameLabel import FrameLabel
import StyleSheet


class SettingsDialog(QtGui.QDialog):

    settingsUpdated = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent,
                               QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("Dispay Settings")
        self.resize(100, 150)

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        formLayout = QtGui.QFormLayout()
        mainLayout.addLayout(formLayout)

        self.scoreFontSizeBox = QtGui.QSpinBox()
        self.scoreFontSizeBox.setMinimum(20)
        self.scoreFontSizeBox.setMaximum(200)
        self.scoreFontSizeBox.setSingleStep(10)
        self.scoreFontSizeBox.setValue(100)
        self.scoreFontSizeBox.valueChanged.connect(self.updateSettings)
        formLayout.addRow("Score font size", self.scoreFontSizeBox)

        self.teamFontSizeBox = QtGui.QSpinBox()
        self.teamFontSizeBox.setMinimum(20)
        self.teamFontSizeBox.setMaximum(150)
        self.teamFontSizeBox.setSingleStep(10)
        self.teamFontSizeBox.setValue(50)
        self.teamFontSizeBox.valueChanged.connect(self.updateSettings)
        formLayout.addRow("Team Name font size", self.teamFontSizeBox)

        self.elapsedTimeFontSizeBox = QtGui.QSpinBox()
        self.elapsedTimeFontSizeBox.setMinimum(20)
        self.elapsedTimeFontSizeBox.setMaximum(200)
        self.elapsedTimeFontSizeBox.setSingleStep(10)
        self.elapsedTimeFontSizeBox.setValue(70)
        self.elapsedTimeFontSizeBox.valueChanged.connect(self.updateSettings)
        formLayout.addRow(
            "Elapsed Time font size", self.elapsedTimeFontSizeBox)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)
        hbox.addStretch(1)

        closelButton = QtGui.QPushButton("Close")
        closelButton.clicked.connect(self.close)
        hbox.addWidget(closelButton)

        hbox.addStretch(1)

        self.updateSettings()

    def updateSettings(self):
        self.settingsList = [self.scoreFontSizeBox.text(),
                             self.teamFontSizeBox.text(),
                             self.elapsedTimeFontSizeBox.text()]
        self.settingsUpdated.emit(self.settingsList)


class NewMatch(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent,
                               QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("New Match")
        self.resize(350, 100)

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(0)
        mainLayout.addLayout(hbox)

        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)

        label = QtGui.QLabel("Team A")
        label.setAlignment(QtCore.Qt.AlignHCenter)
        vbox.addWidget(label)
        
        self.teamALine = QtGui.QLineEdit()
        vbox.addWidget(self.teamALine)

        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)

        label = QtGui.QLabel("Team B")
        label.setAlignment(QtCore.Qt.AlignHCenter)
        vbox.addWidget(label)

        self.teamBLine = QtGui.QLineEdit()
        vbox.addWidget(self.teamBLine)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addStretch(1)

        doneButton = QtGui.QPushButton("Done")
        doneButton.clicked.connect(self.accept)
        hbox.addWidget(doneButton)

        cancelButton = QtGui.QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        hbox.addWidget(cancelButton)

        hbox.addStretch(1)

        self.accepted = False

        self.exec_()

    def accept(self):
        teamA = self.teamALine.text().strip()
        if teamA == '':
            return QtGui.QMessageBox.warning(self, "Add Match", "Team A cannot be empty!")
        teamB = self.teamBLine.text().strip()
        if teamB == '':
            return QtGui.QMessageBox.warning(self, "Add Match", "Team B cannot be empty!")

        self.accepted = True
        self.matchList = [teamA, teamB]

        self.close()


class Rematch(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent, QtCore.Qt.Window |
                              QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.setWindowIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "Icon")))
        self.setWindowTitle("Rematch")

        screen = QtGui.QDesktopWidget().screenGeometry()
        self.setFixedSize(450, 300)
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (
            screen.height() - size.height()) / 2)
        self.lastWindowGeometry = self.geometry()

        self.settingsDialog = SettingsDialog(self)
        self.settingsDialog.settingsUpdated.connect(self.updateSettings)

        mainWidget = QtGui.QWidget(self)
        mainWidget.setGeometry(0, 0, 450, 300)
        mainWidget.setObjectName("main")
        mainWidget.setStyleSheet("""
                            QWidget#main {
                            background: #ffffff; border: 1px solid #00B6F3; border-radius: 0px;
                            }
                            """)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing(0)
        mainLayout.setMargin(0)
        mainWidget.setLayout(mainLayout)

        frame = FrameLabel(self)
        frame.settingsButton.clicked.connect(self.settingsDialog.exec_)
        mainLayout.addWidget(frame)

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.increaseElapsedTime)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(5)
        hbox.setSpacing(5)
        mainLayout.addLayout(hbox)

        hbox.addStretch(1)

        self.pauseButton = QtGui.QToolButton()
        self.pauseButton.setToolTip("Pause Time")
        self.pauseButton.setStyleSheet(StyleSheet.playPauseButtonStyle)
        self.pauseButton.setAutoRaise(True)
        self.pauseButton.setIconSize(QtCore.QSize(30, 30))
        self.pauseButton.setMinimumWidth(45)
        self.pauseButton.setMinimumHeight(45)
        self.pauseButton.setIcon(QtGui.QIcon("Resources\\images\\pause"))
        hbox.addWidget(self.pauseButton)
        self.pauseButton.clicked.connect(self.stop)
        self.pauseButton.hide()

        self.playButton = QtGui.QToolButton()
        self.playButton.setToolTip("Start\Continue Time")
        self.playButton.setStyleSheet(StyleSheet.playPauseButtonStyle)
        self.playButton.setAutoRaise(True)
        self.playButton.setIconSize(QtCore.QSize(30, 30))
        self.playButton.setMinimumWidth(45)
        self.playButton.setMinimumHeight(45)
        self.playButton.setIcon(QtGui.QIcon("Resources\\images\\player_play"))
        self.playButton.clicked.connect(self.play)
        hbox.addWidget(self.playButton)

        hbox.addStretch(1)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(10)
        mainLayout.addLayout(hbox)

        self.teamAScoreLabel = QtGui.QLabel()
        self.teamAScoreLabel.setStyleSheet(StyleSheet.scoreLabelStyle)
        hbox.addWidget(self.teamAScoreLabel)

        hbox.addStretch(1)

        self.scoreABox = QtGui.QLineEdit('0')
        self.scoreABox.setReadOnly(True)
        self.scoreABox.setStyleSheet(StyleSheet.scoreBoxStyle)
        self.scoreABox.setMinimumHeight(45)
        self.scoreABox.setMinimumWidth(95)
        self.scoreABox.textChanged.connect(self.updateInstruction)
        hbox.addWidget(self.scoreABox)

        self.increaseAbutton = QtGui.QToolButton()
        self.increaseAbutton.setToolTip("Score")
        self.increaseAbutton.setIcon(
            QtGui.QIcon("Resources\\images\\go-up-black"))
        self.increaseAbutton.setStyleSheet(StyleSheet.increaseButtonStyle)
        self.increaseAbutton.clicked.connect(self.increaseA)
        hbox.addWidget(self.increaseAbutton)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(10)
        mainLayout.addLayout(hbox)

        self.teamBScoreLabel = QtGui.QLabel()
        self.teamBScoreLabel.setStyleSheet(StyleSheet.scoreLabelStyle)
        hbox.addWidget(self.teamBScoreLabel)

        hbox.addStretch(1)

        self.scoreBBox = QtGui.QLineEdit('0')
        self.scoreBBox.setReadOnly(True)
        self.scoreBBox.setStyleSheet(StyleSheet.scoreBoxStyle)
        self.scoreBBox.setMinimumHeight(45)
        self.scoreBBox.setMinimumWidth(95)
        self.scoreBBox.textChanged.connect(self.updateInstruction)
        hbox.addWidget(self.scoreBBox)

        self.increaseBbutton = QtGui.QToolButton()
        self.increaseBbutton.setToolTip("Score")
        self.increaseBbutton.setStyleSheet(StyleSheet.increaseButtonStyle)
        self.increaseBbutton.setIcon(
            QtGui.QIcon("Resources\\images\\go-up-black"))
        self.increaseBbutton.clicked.connect(self.increaseB)
        hbox.addWidget(self.increaseBbutton)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addStretch(1)

        self.timeElapsedLabel = QtGui.QLabel('00:00')
        self.timeElapsedLabel.setStyleSheet(StyleSheet.timeElapsedStyle)
        hbox.addWidget(self.timeElapsedLabel)

        hbox.addStretch(1)

        mainLayout.addStretch(1)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.resetButton = QtGui.QPushButton("Reset")
        self.resetButton.setStyleSheet(StyleSheet.resetButtonStyle)
        self.resetButton.clicked.connect(self.reset)
        hbox.addWidget(self.resetButton)

        self.movieButton = QtGui.QPushButton("Movie")
        self.movieButton.setStyleSheet(StyleSheet.breakButtonStyle)
        self.movieButton.clicked.connect(self.showMovie)
        hbox.addWidget(self.movieButton)

        self.newButton = QtGui.QPushButton("New")
        self.newButton.setStyleSheet(StyleSheet.newButtonStyle)
        self.newButton.clicked.connect(self.newMatch)
        hbox.addWidget(self.newButton)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(5)
        hbox.setSpacing(5)
        mainLayout.addLayout(hbox)

        label = QtGui.QLabel()
        label.setScaledContents(True)
        label.setMaximumWidth(25)
        label.setMinimumWidth(25)
        label.setMaximumHeight(25)
        label.setMinimumHeight(25)
        label.setPixmap(QtGui.QPixmap("Resources\\images\\network-wireless"))
        hbox.addWidget(label)

        self.addressLabel = QtGui.QLabel("Boadcasting on port:")
        hbox.addWidget(self.addressLabel)

        self.addressLabel = QtGui.QLabel()
        hbox.addWidget(self.addressLabel)

        self.timeElapsed = 0
        self.animation = 0

        self.tcpServer = QtNetwork.QTcpServer(self)
        if not self.tcpServer.listen():
            QtGui.QMessageBox.critical(self, "Rematch",
                                      "Unable to start the server: {0}.".format(self.tcpServer.errorString()))
            self.close()
        self.tcpServer.newConnection.connect(self.sendInstruction)

        self.addressLabel.setText(str(self.tcpServer.serverPort()))
        hbox.addStretch(1)

        self.settingsList = self.settingsDialog.settingsList

        self.updateInstruction()

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.warning(self, "Close",
                                         "Do you really want to quit?",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def increaseA(self):
        if self.timer.isActive():
            self.scoreABox.setText(str(int(self.scoreABox.text()) + 1))
        else:
            message = QtGui.QMessageBox.information(
                self, "Rematch", "No match in progress.")

    def increaseB(self):
        if self.timer.isActive():
            self.scoreBBox.setText(str(int(self.scoreBBox.text()) + 1))
        else:
            message = QtGui.QMessageBox.information(
                self, "Rematch", "No match in progress.")

    def updateInstruction(self):
        teamA = self.teamAScoreLabel.text()
        scoreA = self.scoreABox.text()
        teamB = self.teamBScoreLabel.text()
        scoreB = self.scoreBBox.text()
        elapsedTime = str(self.timeElapsedLabel.text())
        animation = str(self.animation)

        self.instruction = \
            teamA + '#' + \
            scoreA +  '#' + \
            teamB +  '#' + \
            scoreB +  '#' + \
            elapsedTime +  '#' + \
            animation +  '#' + \
            str(self.settingsList[0])  +  '#' + \
            str(self.settingsList[1])  +  '#' + \
            str(self.settingsList[2])

    def sendInstruction(self):
        block = QtCore.QByteArray()
        out = QtCore.QDataStream(block, QtCore.QIODevice.WriteOnly)
        out.setVersion(QtCore.QDataStream.Qt_4_0)
        out.writeUInt16(0)

        try:
            # Python v3.
            instruction = bytes(self.instruction, encoding='ascii')
        except:
            # Python v2.
            print("Error")

        out.writeString(instruction)
        out.device().seek(0)
        out.writeUInt16(block.size() - 2)

        clientConnection = self.tcpServer.nextPendingConnection()
        clientConnection.disconnected.connect(clientConnection.deleteLater)

        clientConnection.write(block)
        clientConnection.disconnectFromHost()

        if self.animation == 1:
            self.animation = 0
            self.updateInstruction()

    def clear(self):
        self.timer.stop()
        self.scoreABox.setText('0')
        self.scoreBBox.setText('0')
        self.pauseButton.hide()
        self.playButton.show()
        self.teamAScoreLabel.clear()
        self.teamBScoreLabel.clear()
        self.timeElapsed = 0
        self.animation = 0
        self.timeElapsedLabel.setText("00:00")

        self.updateInstruction()

    def reset(self):
        reply = QtGui.QMessageBox.warning(self, "Restart",
                                         "This will clear the current match for a new one!\n\n Proceed?",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.clear()
        else:
            return

    def showMovie(self):
        self.animation = 1
        self.updateInstruction()

    def play(self):
        if self.teamBScoreLabel.text().strip() == '':
            message = QtGui.QMessageBox.information(
                self, "Play", "You may have to set up the teams first.")
            return
        self.playButton.hide()
        self.pauseButton.show()
        self.timer.start()
        
    def formatNumber(self, numString):
        if len(numString) == 1:
            return '0' + numString
        else:
            return numString

    def increaseElapsedTime(self):
        self.timeElapsed += 1
    
        if self.timeElapsed >= 60:
            min = int(self.timeElapsed / 60)
            sec = int(self.timeElapsed - (60 * min))
            
            min = self.formatNumber(str(min))
            sec = self.formatNumber(str(sec))
            elapsed = "{0}:{1}".format(min, sec)
        else:
            sec = self.formatNumber(str(self.timeElapsed))
            elapsed = '00:{0}'.format(sec)
        
        self.timeElapsedLabel.setText(elapsed)
        self.updateInstruction()

    def stop(self):
        self.timer.stop()
        self.pauseButton.hide()
        self.playButton.show()

    def newMatch(self):
        if self.teamAScoreLabel.text() != '':
            reply = QtGui.QMessageBox.warning(self, "New Match",
                                             "This will end the current match.\n\nProceed?",
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                pass
            else:
                return
        newMatch = NewMatch(self)
        if newMatch.accepted:
            self.clear()
            self.teamAScoreLabel.setText(newMatch.matchList[0])
            self.teamBScoreLabel.setText(newMatch.matchList[1])
            self.updateInstruction()

    def updateSettings(self, settingsList):
        self.settingsList = settingsList
        self.updateInstruction()

app = QtGui.QApplication(sys.argv)
app.setStyleSheet(StyleSheet.globalStyle)

main = Rematch()
main.show()

sys.exit(app.exec_())
