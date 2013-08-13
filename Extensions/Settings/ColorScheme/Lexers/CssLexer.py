from PyQt4 import QtGui

from PyQt4.Qsci import QsciLexerCSS

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
        'UnknownPseudoClass': ['Consolas', '#D9007E', 10, False, False, '#ffffff'],
        'DoubleQuotedString': ['Consolas', '#00cc00', 10, False, False, '#ffffff'],
        'Tag': ['Consolas', '#E72500', 10, False, False, '#ffffff'],
        'Comment': ['Consolas', '#00CC00', 10, False, False, '#ffffff'],
        'AtRule': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'CSS1Property': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'UnknownProperty': ['Consolas', '#00aa00', 10, False, False, '#ffffff'],
        'Attribute': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'CSS2Property': ['Consolas', '#00aa00', 10, False, False, '#ffffff'],
        'PseudoElement': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'Operator': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'PseudoClass': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'ExtendedCSSProperty': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'Value': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'MediaRule': ['Consolas', '#00aa00', 10, False, False, '#ffffff'],
        'Variable': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'ExtendedPseudoClass': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'CSS3Property': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'IDSelector': ['Consolas', '#71AB71', 10, False, False, '#ffffff'],
        'Important': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'ExtendedPseudoElement': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'Default': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'SingleQuotedString': ['Consolas', '#00cc00', 10, False, False, '#ffffff'],
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
