# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText

from PyQt4 import QtCore, QtGui

class Feedback(QtGui.QLabel):
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        
        self.setWindowTitle("Feedback")
        self.setMinimumSize(500, 150)
        
        self.setBackgroundRole(QtGui.QPalette.Background)
        self.setAutoFillBackground(True)
        
        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        
        label = QtGui.QLabel("Feedback")
        label.setStyleSheet("font: 14px; color: grey;")
        mainLayout.addWidget(label)
        
        self.feedbackForm = QtGui.QPlainTextEdit()
        mainLayout.addWidget(self.feedbackForm)
        
        hbox = QtGui.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 5, 0)
        mainLayout.addLayout(hbox)
        hbox.addStretch(1)
        
        self.sendButton = QtGui.QPushButton("Send")
        self.sendButton.clicked.connect(self.send)
        hbox.addWidget(self.sendButton)
        
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.hide)
        hbox.addWidget(self.cancelButton)

    def send(self):    
        try:
            # Create a text/plain message
            msg = MIMEText(self.feedbackForm.toPlainText())

            text = self.feedbackForm.toPlainText()
            if text.strip() == '':
                message = QtGui.QMessageBox.information(self, "Send", "Message cannot be empty!")
                return
            else:
                pass
            msg['Subject'] = 'Feedback'
            msg['From'] = "Pcode User"
            msg['To'] = "Pcode Mailing List"

            # Send the message via our own SMTP server, but don't include the
            # envelope header.
            s = smtplib.SMTP('localhost')
            s.sendmail(text, ["pcode-ide@googlegroups.com"], msg.as_string())
            s.quit()
            
            self.close()
        except Exception as err:
            message = QtGui.QMessageBox.warning(self, "Feedback", "Sending failed!\n\n{0}".format(str(err)))