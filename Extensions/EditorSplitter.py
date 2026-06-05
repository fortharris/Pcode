from PyQt6.QtWidgets import QHBoxLayout, QSplitter, QWidget


class EditorSplitter(QWidget):

    def __init__(self, editor, editor2, DATA, editorTabWidget, parent):
        QWidget.__init__(self, parent)

        self.editorTabWidget = editorTabWidget
        self.DATA = DATA
        self.parent = parent

        self.editor = editor
        self.editor2 = editor2

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.splitter = QSplitter()
        mainLayout.addWidget(self.splitter)

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.editor2)
        editor2.hide()

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        self.editor.modificationChanged.connect(self.textModified)
        self.editor2.modificationChanged.connect(self.textModified)

    def getEditor(self, index=None):
        if index is None:
            index = 0
        return self.splitter.widget(index)

    def getFocusedEditor(self):
        f = self.splitter.focusWidget()
        if f is None:
            return self.getEditor()
        return f

    def textModified(self, modified):
        index = self.editorTabWidget.indexOf(self.parent)
        self.editorTabWidget.updateTabName(index)
