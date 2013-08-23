#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

from PyQt4 import QtCore, QtGui


class ClipLet(QtGui.QLabel):
    def __init__(self, text, parent):
        super(ClipLet, self).__init__(text, parent)

        self.setAutoFillBackground(True)
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameShadow(QtGui.QFrame.Raised)

        self.setFocusPolicy(QtCore.Qt.ClickFocus)

    def mousePressEvent(self, event):
        hotSpot = event.pos()

        mimeData = QtCore.QMimeData()
        mimeData.setText(self.text())
        mimeData.setData('application/x-hotspot',
                         '%d %d' % (hotSpot.x(), hotSpot.y()))

        pixmap = QtGui.QPixmap(self.size())
        self.render(pixmap)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hotSpot)

        dropAction = drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

        if dropAction == QtCore.Qt.MoveAction:
            self.close()
            self.update()

    def mouseDoubleClickEvent(self, event):
        self.close()


class ClipBoard(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ClipBoard, self).__init__(parent)

        self.setBackgroundRole(QtGui.QPalette.Light)
        self.setAutoFillBackground(True)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.setDropAction(QtCore.Qt.CopyAction)
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            mime = event.mimeData()
            text = mime.text()
            position = event.pos()
            hotSpot = QtCore.QPoint()

            hotSpotPos = mime.data('application/x-hotspot').split(' ')
            if len(hotSpotPos) == 2:
                hotSpot.setX(hotSpotPos[0].toInt()[0])
                hotSpot.setY(hotSpotPos[1].toInt()[0])

            clipLet = ClipLet(text, self)
            clipLet.setStyleSheet("background: #FFFECB; color: black;")
            clipLet.move(position - hotSpot)
            clipLet.show()

            position += QtCore.QPoint(clipLet.width(), 0)

            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                event.setDropAction(QtCore.Qt.CopyAction)
                event.accept()
        else:
            event.ignore()

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = ClipBoard()
    window.show()
    sys.exit(app.exec_())
