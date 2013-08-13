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
