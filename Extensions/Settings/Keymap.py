from PyQt4 import QtCore, QtGui, QtXml


class GetShortcut(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("New Shortcut")

        self.keys = 0
        self.accepted = False

        # Keyword modifiers!
        self.keyword_modifiers = (
            QtCore.Qt.Key_Control, QtCore.Qt.Key_Meta, QtCore.Qt.Key_Shift,
            QtCore.Qt.Key_Alt, QtCore.Qt.Key_Menu)

        mainLayout = QtGui.QVBoxLayout(self)

        self.keyLine = QtGui.QLineEdit()
        self.keyLine.setReadOnly(True)
        self.keyLine.installEventFilter(self)
        mainLayout.addWidget(self.keyLine)

        hbox = QtGui.QHBoxLayout()
        mainLayout.addLayout(hbox)

        okButton = QtGui.QPushButton("Accept")
        okButton.clicked.connect(self.saveShortcut)
        hbox.addWidget(okButton)

        cancelButton = QtGui.QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        hbox.addWidget(cancelButton)

    def saveShortcut(self):
        self.close()
        self.keysequence = QtGui.QKeySequence(self.keyLine.text())
        self.accepted = True

    def setShortcut(self, txt):
        self.keyLine.setText(txt)

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.KeyPress:
            self.keyPressEvent(event)
            return True
        return False

    def keyPressEvent(self, evt):
        # modifier can not be used as shortcut
        if evt.key() in self.keyword_modifiers:
            return
        # save the key
        if evt.key() == QtCore.Qt.Key_Backtab and evt.modifiers() & QtCore.Qt.ShiftModifier:
            self.keys = QtCore.Qt.Key_Tab
        else:
            self.keys = evt.key()
        if evt.modifiers() & QtCore.Qt.ShiftModifier:
            self.keys += QtCore.Qt.SHIFT
        if evt.modifiers() & QtCore.Qt.ControlModifier:
            self.keys += QtCore.Qt.CTRL
        if evt.modifiers() & QtCore.Qt.AltModifier:
            self.keys += QtCore.Qt.ALT
        if evt.modifiers() & QtCore.Qt.MetaModifier:
            self.keys += QtCore.Qt.META
        # set the keys
        self.setShortcut(QtGui.QKeySequence(self.keys).toString())


class Keymap(QtGui.QDialog):

    def __init__(self, useData, projectWindowStack, parent):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle('Keymap')
        self.resize(500, 400)

        self.parent = parent
        self.useData = useData
        self.projectWindowStack = projectWindowStack

        mainLayout = QtGui.QVBoxLayout()
        self.setLayout(mainLayout)

        self.shortcutsView = QtGui.QTreeWidget()
        self.shortcutsView.setHeaderLabels(["Function", "Shortcut"])
        self.shortcutsView.setColumnWidth(0, 450)
        self.shortcutsView.setSortingEnabled(True)
        self.shortcutsView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.shortcutsView.itemDoubleClicked.connect(self.getShortcut)
        mainLayout.addWidget(self.shortcutsView)

        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(0)
        mainLayout.addLayout(hbox)

        hbox.addStretch(1)
        load_defaults_button = QtGui.QPushButton(self.tr("Default"))
        load_defaults_button.clicked.connect(self.setDefaultShortcuts)
        hbox.addWidget(load_defaults_button)

        self.applyButton = QtGui.QPushButton("Apply")
        self.applyButton.clicked.connect(self.save)
        hbox.addWidget(self.applyButton)

        self.updateShortcutsView()

    def validateShortcut(self, keysequence):
        """
        Validate a shortcut
        """
        if keysequence.isEmpty():
            return True
            
        currentItem = self.shortcutsView.currentItem()
        keystr = keysequence.toString()
        
        for index in range(self.shortcutsView.topLevelItemCount()):
            topLevelItem = self.shortcutsView.topLevelItem(index)
            
            for i in range(topLevelItem.childCount()):
                item = topLevelItem.child(i)
                if item.text(1) == keystr:
                    if currentItem != item:
                        reply = QtGui.QMessageBox.warning(self,
                                                        'Shortcut',
                                                        "Shortcut already in use by '{0}'\n\nReplace it?".format(item.text(0)),
                                                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                        if reply == QtGui.QMessageBox.Yes:
                            item.setText(1, "")
                            return True
                        else:
                            return False
            
        return True

    def getShortcut(self, item, column):
        """
        Open the dialog to set a shortcut
        """
        if item.childCount():
            return
        getShortcut = GetShortcut(self)
        getShortcut.setShortcut(QtGui.QKeySequence(item.text(1)).toString())
        getShortcut.exec_()
        if getShortcut.accepted:
            if self.validateShortcut(getShortcut.keysequence):
                item = self.shortcutsView.currentItem()
                topLevelItem = item.parent()
                item.setText(
                    1, getShortcut.keysequence.toString())
                print(self.useData.CUSTOM_DEFAULT_SHORTCUTS[topLevelItem.text(0)][item.text(0)])
                self.useData.CUSTOM_DEFAULT_SHORTCUTS[topLevelItem.text(0)][item.text(0)][0] = getShortcut.keysequence.toString()

    def save(self):
        self.applyKeyBindings()
        self.saveKeymap()

    def saveKeymap(self, path=None):
        dom_document = QtXml.QDomDocument("keymap")

        keymap = dom_document.createElement("keymap")
        dom_document.appendChild(keymap)

        for key, value in self.useData.CUSTOM_DEFAULT_SHORTCUTS.items():
            root = dom_document.createElement(key)
            keymap.appendChild(root)
            for short, func in value.items():
                tag = dom_document.createElement(short)
                tag.setAttribute("shortcut", func[0])
                tag.setAttribute("function", func[1])
                root.appendChild(tag)

        if path is None:
            path = self.useData.appPathDict["keymap"]
        file = open(path, "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()
                
    def applyKeyBindings(self):
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            window.install_shortcuts()
            editorTabWidget = window.editorTabWidget
            editorTabWidget.install_shortcuts()
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                editor2 = editorTabWidget.getCloneEditor(i)
                editor.install_shortcuts()
                editor2.install_shortcuts()

    def updateShortcutsView(self):
        self.shortcutsView.clear()
        keyList = ['Editor', 'Ide']
        for i in keyList:
            mainItem = QtGui.QTreeWidgetItem(self.shortcutsView)
            mainItem.setText(0, i)
            for function, action in self.useData.CUSTOM_DEFAULT_SHORTCUTS[i].items():
                key = action[0]
                desc = action = action[1]
                treeData = [function, key]
                item = QtGui.QTreeWidgetItem(mainItem, treeData)
                item.setToolTip(0, desc)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            mainItem.setExpanded(True)

    def setDefaultShortcuts(self):
        self.shortcutsView.clear()
        self.useData.CUSTOM_DEFAULT_SHORTCUTS = self.useData.DEFAULT_SHORTCUTS
        self.updateShortcutsView()
        
        self.save()
