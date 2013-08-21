import sys

from PyQt4 import QtGui
from PyQt4.Qsci import QsciLexerCSS

# Platform specific fonts
if sys.platform == 'win32':
    defaultFont = 'Consolas'
elif sys.platform == 'darwin':
    defaultFont = 'Monaco'
else:
    defaultFont = 'Bitstream Vera Sans Mono'

propertyID = {
                'UnknownPseudoClass': 4, 
                'DoubleQuotedString': 13, 
                'Tag': 1, 
                'Comment': 9, 
                'AtRule': 12, 
                'CSS1Property': 6, 
                'UnknownProperty': 7, 
                'Attribute': 16, 
                'CSS2Property': 15, 
                'PseudoElement': 18, 
                'Operator': 5, 
                'PseudoClass': 3, 
                'ExtendedCSSProperty': 19, 
                'Value': 8, 
                'MediaRule': 22, 
                'Variable': 23, 
                'ExtendedPseudoClass': 20, 
                'CSS3Property': 17, 
                'IDSelector': 10, 
                'Important': 11, 
                'ExtendedPseudoElement': 21, 
                'Default': 0, 
                'SingleQuotedString': 14
                }


def styleDescriptions():
    return propertyID.keys()


def defaultStyle():
    defaultStyle = {
        'UnknownPseudoClass': [defaultFont, '#D9007E', 10, False, False, '#ffffff'],
        'DoubleQuotedString': [defaultFont, '#00cc00', 10, False, False, '#ffffff'],
        'Tag': [defaultFont, '#E72500', 10, False, False, '#ffffff'],
        'Comment': [defaultFont, '#00CC00', 10, False, False, '#ffffff'],
        'AtRule': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'CSS1Property': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'UnknownProperty': [defaultFont, '#00aa00', 10, False, False, '#ffffff'],
        'Attribute': [defaultFont, '#000000', 10, False, False, '#ffffff'],
        'CSS2Property': [defaultFont, '#00aa00', 10, False, False, '#ffffff'],
        'PseudoElement': [defaultFont, '#000000', 10, False, False, '#ffffff'],
        'Operator': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'PseudoClass': [defaultFont, '#000000', 10, False, False, '#ffffff'],
        'ExtendedCSSProperty': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'Value': [defaultFont, '#000000', 10, False, False, '#ffffff'],
        'MediaRule': [defaultFont, '#00aa00', 10, False, False, '#ffffff'],
        'Variable': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'ExtendedPseudoClass': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'CSS3Property': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'IDSelector': [defaultFont, '#71AB71', 10, False, False, '#ffffff'],
        'Important': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'ExtendedPseudoElement': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'Default': [defaultFont, '#0000ff', 10, False, False, '#ffffff'],
        'SingleQuotedString': [defaultFont, '#00cc00', 10, False, False, '#ffffff'],
        }

    return defaultStyle


class CssLexer(QsciLexerCSS):

    def __init__(self, style, paper):
        QsciLexerCSS.__init__(self)

        self.lexerPaper = paper

        for key, attrib in style.items():
            value = propertyID[key]
            self.setColor(QtGui.QColor(attrib[1]), value)
            self.setEolFill(True, value)
            self.setPaper(QtGui.QColor(attrib[5]), value)
            if self.lexerPaper[0] == "Plain":
                self.setPaper(QtGui.QColor(attrib[5]), value)
            else:
                self.setPaper(QtGui.QColor(self.lexerPaper[1]), value)

            font = QtGui.QFont(attrib[0], attrib[2])
            font.setBold(attrib[3])
            font.setItalic(attrib[4])
            self.setFont(font, value)

        if self.lexerPaper[0] == "Plain":
            self.setDefaultPaper(QtGui.QColor("#ffffff"))
        else:
            self.setDefaultPaper(QtGui.QColor(self.lexerPaper[1]))
