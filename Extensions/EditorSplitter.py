from PyQt4 import QtGui


class EditorSplitter(QtGui.QSplitter):

    def __init__(self, editor, editor2, DATA, editorTabWidget, parent):
        QtGui.QSplitter.__init__(self, parent)

        self.editorTabWidget = editorTabWidget
        self.DATA = DATA
        self.parent = parent

        self.editor = editor
        self.editor2 = editor2

        self.addWidget(self.editor)
        self.addWidget(self.editor2)
        editor2.hide()

        self.setCollapsible(0, False)
        self.setCollapsible(1, False)

        self.editor.modificationChanged.connect(self.textModified)
        self.editor2.modificationChanged.connect(self.textModified)

    def getEditor(self, index=None):
        if index is None:
            index = 0
        return self.widget(index)

    def getFocusedEditor(self):
        f = self.focusWidget()
        if f is None:
            return self.getEditor()
        return f

    def textModified(self, modified):
        index = self.editorTabWidget.indexOf(self.parent)
        self.editorTabWidget.updateTabName(index)
