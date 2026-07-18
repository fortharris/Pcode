import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QTabWidget, QToolButton, QVBoxLayout,
)
from PyQt6.QtXml import QDomDocument

from Extensions.Settings.ColorScheme.StyleEditor import StyleEditor
from Extensions.Settings.ColorScheme.StyleLexer import StyleLexer


class GetName(QDialog):

    def __init__(self, caption, path, defaultText=None, parent=None):
        QDialog.__init__(self, parent, Qt.WindowType.Window |
                               Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        self.path = path

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Name:"))

        self.nameLine = QLineEdit()
        if defaultText is not None:
            self.nameLine.setText(defaultText)
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QHBoxLayout()

        self.statusLabel = QLabel()
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.acceptButton = QPushButton("Ok")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.closeButton = QPushButton("Cancel")
        self.closeButton.clicked.connect(self.close)
        hbox.addWidget(self.closeButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.resize(300, 20)
        self.enableAcceptButton()

        self.accepted = False

        self.exec()

    def enableAcceptButton(self):
        text = self.nameLine.text().strip()
        if text == '':
            self.acceptButton.setDisabled(True)
        else:
            preExistNames = os.listdir(self.path)
            if text in preExistNames:
                self.statusLabel.setText("Unavailable")
                self.acceptButton.setDisabled(True)
            else:
                self.acceptButton.setDisabled(False)
                preExistNames = os.listdir(self.path)
                if (text in preExistNames) or (text == 'Default'):
                    self.statusLabel.setText("Unavailable")
                    self.acceptButton.setDisabled(True)
                else:
                    self.statusLabel.setText("Available")
                    self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.name = self.nameLine.text().strip()
        self.close()


class ColorScheme(QDialog):

    def __init__(self, useData, projectWindowStack, libraryViewer, parent=None):
        super(ColorScheme, self).__init__(parent)

        self.useData = useData
        self.projectWindowStack = projectWindowStack
        self.libraryViewer = libraryViewer

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(mainLayout)

        optionsTab = QTabWidget()

        self.editorStyler = StyleEditor(self.useData)
        self.lexerStyler = StyleLexer(self.editorStyler, self.useData)
        self.editorStyler.paperChanged.connect(
            self.lexerStyler.reloadStyles.emit)

        optionsTab.addTab(self.lexerStyler,
                          QIcon(os.path.join("Resources", "images", "edit-color")), "Lexer")
        optionsTab.addTab(self.editorStyler,
                          QIcon(os.path.join("Resources", "images", "ui-scroll-pane-blog")), "Editor")

        mainLayout.addWidget(optionsTab)

        self.schemeTypeBox = QComboBox()
        self.schemeTypeBox.addItem("Python")
        self.schemeTypeBox.addItem("Xml")
        self.schemeTypeBox.addItem("Html")
        self.schemeTypeBox.addItem("Css")
        self.schemeTypeBox.currentIndexChanged.connect(self.groupChanged)
        mainLayout.addWidget(self.schemeTypeBox)

        hbox = QHBoxLayout()

        self.schemeNameBox = QComboBox()
        self.schemeNameBox.setMinimumWidth(180)
        self.loadSchemeNames()
        self.schemeNameBox.currentIndexChanged.connect(self.updateScheme)
        hbox.addWidget(self.schemeNameBox)

        self.newButton = QToolButton()
        self.newButton.setAutoRaise(True)
        self.newButton.setDefaultAction(
            QAction(
                QIcon(os.path.join("Resources", "images", "add")),
                "New", self, triggered=self.newScheme))
        hbox.addWidget(self.newButton)

        self.renameButton = QToolButton()
        self.renameButton.setAutoRaise(True)
        self.renameButton.setDefaultAction(
            QAction(
                QIcon(
                    os.path.join("Resources", "images", "ui-text-field")),
                "Rename", self, triggered=self.rename))
        self.renameButton.setDisabled(True)
        hbox.addWidget(self.renameButton)

        self.removeButton = QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setDefaultAction(
            QAction(
                QIcon(os.path.join("Resources", "images", "minus")),
                "Remove", self, triggered=self.remove))
        self.removeButton.setDisabled(True)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.saveStyleChanges)
        self.saveButton.setDisabled(True)
        hbox.addWidget(self.saveButton)

        self.applyButton = QPushButton("Apply")
        self.applyButton.clicked.connect(self.applyScheme)
        hbox.addWidget(self.applyButton)

        mainLayout.addLayout(hbox)

        index = self.schemeNameBox.findText(
            self.useData.SETTINGS["EditorStylePython"])
        self.schemeNameBox.setCurrentIndex(index)

    def groupChanged(self):
        self.loadSchemeNames()
        self.updateScheme()

    def loadSchemeNames(self):
        self.schemeNameBox.clear()
        self.schemeNameBox.addItem(
            QIcon(os.path.join("Resources", "images", "mail_pinned")),
            "Default")
        groupName = self.schemeTypeBox.currentText()
        path = os.path.join(self.useData.appPathDict["stylesdir"], groupName)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
        for i in os.listdir(path):
            self.schemeNameBox.addItem(QIcon(
                os.path.join("Resources", "images", "foaf")), os.path.splitext(i)[0])
        self.lexerStyler.updatePropertyListWidget(groupName)

    def updateScheme(self):
        name = self.schemeNameBox.currentText()
        groupName = self.schemeTypeBox.currentText()
        if name == '':
            return
        self.editorStyler.setCurrentProperty(name, groupName)
        self.lexerStyler.setCurrentStyle(name, groupName)
        if name == "Default":
            self.saveButton.setDisabled(True)
            self.removeButton.setDisabled(True)
            self.renameButton.setDisabled(True)
        else:
            self.saveButton.setDisabled(False)
            self.removeButton.setDisabled(False)
            self.renameButton.setDisabled(False)

        self.editorStyler.propertyListWidget.setCurrentRow(0)

    def save(self, name=None):
        # save style
        dom_document = QDomDocument("Scheme")

        main = dom_document.createElement("Attributes")
        dom_document.appendChild(main)

        root = dom_document.createElement("lexer")
        main.appendChild(root)

        for key, value in self.lexerStyler.currentStyle.items():
            tag = dom_document.createElement("property")
            tag.setAttribute("font", value[0])
            tag.setAttribute("color", value[1])
            tag.setAttribute("size", value[2])
            tag.setAttribute("bold", str(value[3]))
            tag.setAttribute("italic", str(value[4]))
            tag.setAttribute("paper", value[5])

            t = dom_document.createTextNode(key)
            tag.appendChild(t)
            root.appendChild(tag)

        root = dom_document.createElement("editor")
        main.appendChild(root)

        for key, value in self.editorStyler.currentProperties.items():
            tag = dom_document.createElement("property")
            root.appendChild(tag)

            tag.setAttribute("background", value[0])
            tag.setAttribute("foreground", value[1])
            if key == "Calltips":
                tag.setAttribute("highLight", value[2])
            if key == "Number Margin":
                tag.setAttribute("font", value[2])
                tag.setAttribute("size", str(value[3]))
                tag.setAttribute("bold", str(value[4]))
                tag.setAttribute("italic", str(value[5]))

            t = dom_document.createTextNode(key)
            tag.appendChild(t)

        if name is None:
            name = self.schemeNameBox.currentText()
        groupName = self.schemeTypeBox.currentText()
        path = os.path.join(
            self.useData.appPathDict["stylesdir"], groupName, name + '.xml')
        try:
            with open(path, "w") as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write(dom_document.toString())
        except Exception as err:
            QMessageBox.warning(self, "Save",
                                                "Saving failed: {0}".format(str(err)))
            return

    def saveStyleChanges(self):
        currentScheme = self.schemeNameBox.currentText()
        self.save()
        f = self.schemeNameBox.findText(currentScheme)
        self.schemeNameBox.setCurrentIndex(f)

    def newScheme(self):
        themeName = GetName(
            "New Scheme", self.useData.appPathDict["stylesdir"],
            None, self)
        if themeName.accepted:
            self.save(themeName.name)
            self.loadSchemeNames()
            f = self.schemeNameBox.findText(themeName.name)
            self.schemeNameBox.setCurrentIndex(f)

    def rename(self):
        old_name = self.schemeNameBox.currentText()
        newName = GetName("Rename", self.useData.appPathDict["stylesdir"],
                          old_name, self)
        old_name = old_name + '.xml'
        if newName.accepted:
            groupName = self.schemeTypeBox.currentText()
            new_path = os.path.join(
                self.useData.appPathDict["stylesdir"], groupName,
                newName.name + '.xml')
            old_path = os.path.join(
                self.useData.appPathDict["stylesdir"], groupName,
                old_name)
            try:
                os.rename(old_path, new_path)
                self.loadSchemeNames()
                f = self.schemeNameBox.findText(newName.name)
                self.schemeNameBox.setCurrentIndex(f)
                if self.useData.SETTINGS["EditorStyle" + self.schemeTypeBox.currentText()] == old_name:
                    self.useData.SETTINGS[
                        "EditorStyle" + self.schemeTypeBox.currentText()] = newName.name
                    self.useData.saveUseData()
            except Exception as err:
                QMessageBox.warning(self, "Rename",
                                                    "Rename failed!\n\n{0}".format(str(err)))

    def remove(self):
        index = self.schemeNameBox.currentIndex()
        currentScheme = self.schemeNameBox.currentText()

        mess = "Do you really want to remove '{0}'?".format(currentScheme)
        reply = QMessageBox.warning(self, "Remove",
                                          mess, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            schemeFullName = currentScheme + '.xml'
            groupName = self.schemeTypeBox.currentText()
            path = os.path.join(
                self.useData.appPathDict["stylesdir"], groupName,
                schemeFullName)
            try:
                os.remove(path)
                self.schemeNameBox.removeItem(index)
                self.updateScheme()
                if self.useData.SETTINGS["EditorStyle" + self.schemeTypeBox.currentText()] == currentScheme:
                    self.useData.SETTINGS[
                        "EditorStyle" + self.schemeTypeBox.currentText()] = self.schemeNameBox.currentText()
                    self.useData.saveUseData()
            except Exception as err:
                QMessageBox.warning(self, "Remove",
                                                    "Removing failed!\n\n{0}".format(str(err)))
        elif reply == QMessageBox.StandardButton.No:
            pass

    def restyleAllEditors(self):
        """Restyle every open editor (e.g. after UI theme change)."""
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            if not hasattr(window, "editorTabWidget"):
                continue
            editorTabWidget = window.editorTabWidget
            for tab in range(editorTabWidget.count()):
                self.styleEditor(editorTabWidget.getEditor(tab))
                self.styleEditor(editorTabWidget.getCloneEditor(tab))
                self.styleEditor(editorTabWidget.getSnapshot(tab))
        self.styleEditor(self.libraryViewer)

    def applyScheme(self):
        schemeType = self.schemeTypeBox.currentText()
        schemeName = self.schemeNameBox.currentText()
        if self.schemeNameBox.currentIndex() != 0:
            self.save()
        self.useData.SETTINGS[
            "EditorStyle" + schemeType] = schemeName
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            editorTabWidget = window.editorTabWidget
            for i in range(window.editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == 'python':
                    if schemeType != "Python":
                        continue
                elif editor.DATA["fileType"] == '.xml':
                    if schemeType != "Xml":
                        continue
                elif editor.DATA["fileType"] == '.html':
                    if schemeType != "Html":
                        continue
                elif editor.DATA["fileType"] == '.css':
                    if schemeType != "Css":
                        continue
                self.styleEditor(editor)
                editor2 = editorTabWidget.getCloneEditor(i)
                self.styleEditor(editor2)
                snapshot = editorTabWidget.getSnapshot(i)
                self.styleEditor(snapshot)
        self.styleEditor(self.libraryViewer)

    def styleEditor(self, editor):
        fileType = editor.DATA["fileType"]
        if fileType not in self.useData.supportedFileTypes:
            return None
        if fileType == "python":
            style_name = self.useData.SETTINGS["EditorStylePython"]
            groupName = "Python"
        elif fileType == ".xml":
            style_name = self.useData.SETTINGS["EditorStyleXml"]
            groupName = "Xml"
        elif fileType == ".html":
            style_name = self.useData.SETTINGS["EditorStyleHtml"]
            groupName = "Html"
        elif fileType == ".css":
            style_name = self.useData.SETTINGS["EditorStyleCss"]
            groupName = "Css"

        properties = self.editorStyler.loadProperties(style_name, groupName)
        paper = self.editorStyler.applyChanges(editor, properties)
        lexer = self.lexerStyler.createLexer(paper, style_name, groupName)
        editor.updateLexer(lexer)

        return lexer
