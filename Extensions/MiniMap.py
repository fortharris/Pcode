import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla

class Handle(QtGui.QFrame):
    def __init__(self, parent):
        QtGui.QLabel.__init__(self, parent)
        
        self.minimap = parent
        self.editor = parent.editor
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.OpenHandCursor)
        self.setStyleSheet("""
                        border-top: 1px solid grey; 
                        border-right: none; 
                        border-bottom: 1px solid grey;
                        padding: 0px, 2px, 0px, 0px;
                        background: rgba(0, 0, 0, 30);
                        """)
        
        self.pressed = False
        self.scroll_margins = None
        
        self.minimapScrollBar = self.minimap.verticalScrollBar()
        
    def updateScrollMargins(self, margins):
        self.scroll_margins = margins
        
    def mousePressEvent(self, event):
        self.pressed = True
        self.setCursor(QtCore.Qt.ClosedHandCursor)
        
    def mouseReleaseEvent(self, event):
        super(Handle, self).mouseReleaseEvent(event)
        self.pressed = False
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def mouseMoveEvent(self, event):
        super(Handle, self).mouseMoveEvent(event)
        if self.pressed:
            relativePos = self.mapToParent(event.pos())
            y = relativePos.y() - (self.height() / 2)
            if y < 0:
                y = 0
            if y < self.scroll_margins[0]:
                self.minimapScrollBar.setSliderPosition(
                    self.minimapScrollBar.sliderPosition() - 2)
            elif y > self.scroll_margins[1]:
                self.minimapScrollBar.setSliderPosition(
                    self.minimapScrollBar.sliderPosition() + 2)
            self.move(0, y)
            self.minimap.updateEditorScrollPos(relativePos, event.pos())
            
    def updatePosition(self):
        font_size = QtGui.QFontMetrics(self.minimap.font()).height()
        height = self.minimap.lines() * font_size
        self.setFixedHeight(height)
        self.scroll_margins = (height, self.minimap.height() - height)
        
    def move_slider(self, y):
        self.move(0, y)

class MiniMap(QsciScintilla):
    def __init__(self, editor=None, parent=None):
        QsciScintilla.__init__(self, parent)
        
        self.editor = editor
        
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.viewport().setCursor(QtCore.Qt.PointingHandCursor)
        self.setMarginWidth(1, 0)
        font = QtGui.QFont()
        font.setPointSize(1)
        self.setFont(font)
        self.setDocument(self.editor.document())
        
        self.setMaximumWidth(120)
        self.setMinimumWidth(120)
        
        self.editorVericalScrollBar = self.editor.verticalScrollBar()
        
        self.handle = Handle(self)
        self.handle.setMinimumWidth(120)
        self.turnOn()
        
    def resizeEvent(self, event):
        super(MiniMap, self).resizeEvent(event)
        self.updateHandleGeometry()
        
    def mousePressEvent(self, event):
        super(MiniMap, self).mousePressEvent(event)
        line, index = self.getCursorPosition()
        self.editor.showLine(line)
        
    def updateHandlePosition(self):
        if not self.handle.pressed:
            line_number = self.editor.firstVisibleLine()
            
            return

            self.setFirstVisibleLine(line_number)
            block = self.document().findBlockByLineNumber(line_number)
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            rect = self.cursorRect(cursor)
            self.setTextCursor(cursor)
            self.handle.move_slider(rect.y())
        
    def updateHandleGeometry(self):
        if not self.handle.pressed:
            lines_on_screen = self.editor.linesOnScreen()
            line_height = self.textHeight(0)
            height = line_height*lines_on_screen
            self.handle.setFixedHeight(height)
            self.handle.updateScrollMargins((height, self.geometry().height() - height))
            
    def updateEditorScrollPos(self, relativePos, handlePos):
        relativePos.setY(relativePos.y() - handlePos.y())
        self.editorVericalScrollBar.setValue(relativePos.y() - handlePos.y())
            
    def wheelEvent(self, event):
        super(MiniMap, self).wheelEvent(event)
        self.editor.wheelEvent(event)
        
    def turnOn(self):
        self.editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.show()
        
    def turnOff(self):
        self.editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.hide()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = MiniMap()
    main.show()

    sys.exit(app.exec_())
