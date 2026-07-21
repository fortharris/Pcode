import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QButtonGroup, QFontDialog, QHBoxLayout, QLabel, QListWidget, QPushButton,
    QRadioButton, QVBoxLayout, QWidget,
)
from PyQt6.QtXml import QDomDocument

from Extensions.Settings.ColorScheme.Lexers import PythonLexer
from Extensions.Settings.ColorScheme.Lexers import CssLexer
from Extensions.Settings.ColorScheme.Lexers import HtmlLexer
from Extensions.Settings.ColorScheme.Lexers import XmlLexer
from Extensions.Settings.ColorScheme.ColorChooser import ColorChooser
from Extensions import StyleSheet


def _header_style():
    bg = StyleSheet.CURRENT_PALETTE.get("panelHeader", "#D8D8D8")
    return "background: {0}; padding: 2px;".format(bg)


class StyleLexer(QWidget):

    reloadStyles = pyqtSignal()

    def __init__(self, styleProperties, useData, parent=None):
        super(StyleLexer, self).__init__(parent)

        self.styleProperties = styleProperties
        self.useData = useData

        self.setCurrentStyle("Default", "Python")

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # style properties
        self.propertyListWidget = QListWidget()
        self.propertyListWidget.setSortingEnabled(True)
        self.propertyListWidget.currentRowChanged.connect(
            self.newPropertySelected)
        mainLayout.addWidget(self.propertyListWidget)

        self.setLayout(mainLayout)

        # settings
        vbox = QVBoxLayout()
        mainLayout.addLayout(vbox)

        self.fontColorScopeBG = QButtonGroup()

        hbox = QHBoxLayout()
        label = QLabel("Foreground")
        label.setStyleSheet(_header_style())
        hbox.addWidget(label)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        fontColorScopeAll = QRadioButton("All")
        self.fontColorScopeBG.addButton(fontColorScopeAll)
        hbox.addWidget(fontColorScopeAll)

        fontColorScopeCurrent = QRadioButton("Selected")
        self.fontColorScopeBG.addButton(fontColorScopeCurrent)
        fontColorScopeCurrent.setChecked(True)
        hbox.addWidget(fontColorScopeCurrent)

        self.fontColorChooser = ColorChooser()
        self.fontColorChooser.colorChanged.connect(self.updateColor)
        hbox.addWidget(self.fontColorChooser)

        self.backgroundColorScopeBG = QButtonGroup()

        hbox = QHBoxLayout()
        label = QLabel("Background")
        label.setStyleSheet(_header_style())
        hbox.addWidget(label)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        backgroundColorScopeAll = QRadioButton("All")
        self.backgroundColorScopeBG.addButton(backgroundColorScopeAll)
        hbox.addWidget(backgroundColorScopeAll)

        backgroundColorScopeCurrent = QRadioButton("Selected")
        self.backgroundColorScopeBG.addButton(backgroundColorScopeCurrent)
        backgroundColorScopeCurrent.setChecked(True)
        hbox.addWidget(backgroundColorScopeCurrent)

        self.backgroundColorChooser = ColorChooser()
        self.backgroundColorChooser.colorChanged.connect(self.updatePaper)
        hbox.addWidget(self.backgroundColorChooser)

        self.fontScopeBG = QButtonGroup()

        hbox = QHBoxLayout()
        label = QLabel("Font")
        label.setStyleSheet(_header_style())
        hbox.addWidget(label)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        fontScopeAll = QRadioButton("All")
        self.fontScopeBG.addButton(fontScopeAll)
        hbox.addWidget(fontScopeAll)

        fontScopeCurrent = QRadioButton("Selected")
        self.fontScopeBG.addButton(fontScopeCurrent)
        fontScopeCurrent.setChecked(True)
        hbox.addWidget(fontScopeCurrent)

        hbox.addStretch(1)

        self.fontButton = QPushButton("Font")
        self.fontButton.clicked.connect(self.fontChanged)
        hbox.addWidget(self.fontButton)

        vbox.addStretch(1)

    def updatePropertyListWidget(self, groupName):
        if groupName == "Python":
            styles = PythonLexer.styleDescriptions()
        elif groupName == "Css":
            styles = CssLexer.styleDescriptions()
        elif groupName == "Xml":
            styles = XmlLexer.styleDescriptions()
        elif groupName == "Html":
            styles = HtmlLexer.styleDescriptions()

        self.propertyListWidget.clear()
        for i in styles:
            self.propertyListWidget.addItem(i)
        self.propertyListWidget.setCurrentRow(0)

    def createLexer(self, paper, style_name, groupName):
        style = self.loadStyle(style_name, groupName)
        if groupName == "Python":
            lexer = PythonLexer.PythonLexer(style, paper)
        elif groupName == "Xml":
            lexer = XmlLexer.XmlLexer(style, paper)
        elif groupName == "Html":
            lexer = HtmlLexer.HtmlLexer(style, paper)
        elif groupName == "Css":
            lexer = CssLexer.CssLexer(style, paper)
        return lexer

    def setCurrentStyle(self, styleName, groupName):
        self.currentStyle = self.loadStyle(styleName, groupName)

    def loadStyle(self, styleName, groupName):
        if styleName == "Default":
            if groupName == "Python":
                style = PythonLexer.defaultStyle()
            elif groupName == "Css":
                style = CssLexer.defaultStyle()
            elif groupName == "Xml":
                style = XmlLexer.defaultStyle()
            elif groupName == "Html":
                style = HtmlLexer.defaultStyle()
            else:
                style = {}
            # Tie Default lexer colours to the active UI theme tokens.
            from Extensions import StyleSheet
            return StyleSheet.theme_overlay_style(style)
        else:
            pass

        style = {}

        stylePath = os.path.join(self.useData.appPathDict["stylesdir"],
                                 groupName, styleName + ".xml")
        dom_document = QDomDocument()
        with open(stylePath, "r") as file:
            dom_document.setContent(file.read())

        rootElement = dom_document.documentElement()
        lexerElement = rootElement.firstChild().toElement()
        node = lexerElement.firstChild()

        while node.isNull() is False:
            tag = node.toElement()

            name = tag.text()
            font = tag.attribute("font")
            color = tag.attribute("color")
            size = int(tag.attribute("size"))
            bold = (tag.attribute("bold") == "True")
            italic = (tag.attribute("italic") == "True")
            paper = tag.attribute("paper")

            style[name] = [font, color, size, bold, italic, paper]

            node = node.nextSibling()
        return style

    def updateFontSizeBox(self, widget):
        for i in self.fontSizeList:
            widget.addItem(str(i))

    def newPropertySelected(self):
        currentItem = self.propertyListWidget.currentItem()
        if currentItem is None:
            return
        self.currentPropertyName = currentItem.text()
        self.currentPropertyAttrib = \
            self.currentStyle[self.currentPropertyName]

        QColor(self.currentPropertyAttrib[1])
        self.fontColorChooser.setColor(self.currentPropertyAttrib[1])

        QColor(self.currentPropertyAttrib[5])
        self.backgroundColorChooser.setColor(self.currentPropertyAttrib[5])

    def fontChanged(self):
        currentfont = QFont(self.currentPropertyAttrib[
                                  0], self.currentPropertyAttrib[2])
        currentfont.setBold(self.currentPropertyAttrib[3])
        currentfont.setItalic(self.currentPropertyAttrib[4])
        font = QFontDialog().getFont(currentfont, self)
        if font[1]:
            font = font[0]
            name = font.rawName()
            size = font.pointSize()
            bold = font.bold()
            italic = font.italic()
            if self.fontScopeBG.checkedButton().text() == 'All':
                for key, value in self.currentStyle.items():
                    value[0] = name
                    value[2] = size
                    value[3] = bold
                    value[4] = italic
                    self.currentStyle[key] = value
            else:
                self.currentPropertyAttrib[0] = name
                self.currentPropertyAttrib[2] = size
                self.currentPropertyAttrib[3] = bold
                self.currentPropertyAttrib[4] = italic
                self.currentStyle[self.currentPropertyName] = \
                    self.currentPropertyAttrib

    def updateColor(self, color):
        self.currentPropertyAttrib[1] = color
        if self.fontColorScopeBG.checkedButton().text() == 'All':
            for key, value in self.currentStyle.items():
                value[1] = color
                self.currentStyle[key] = value
        else:
            self.currentStyle[
                self.currentPropertyName] = self.currentPropertyAttrib
        self.newPropertySelected()

    def updatePaper(self, color):
        self.currentPropertyAttrib[5] = color
        if self.backgroundColorScopeBG.checkedButton().text() == 'All':
            for key, value in self.currentStyle.items():
                value[5] = color
                self.currentStyle[key] = value
        else:
            self.currentStyle[self.currentPropertyName] = \
                self.currentPropertyAttrib
        self.newPropertySelected()
