import keyword
from PyQt4 import QtGui

from PyQt4.Qsci import QsciLexerPython

propertyID = {
    'Default': 0,
    'Comment': 1,
    'Number': 2,
    'DoubleQuotedString': 3,
    'SingleQuotedString': 4,
    'Keyword': 5,
    'TripleSingleQuotedString': 6,
    'TripleDoubleQuotedString': 7,
    'ClassName': 8,
    'FunctionMethodName': 9,
    'Operator': 10,
    'Identifier': 11,
    'CommentBlock': 12,
    'UnclosedString': 13,
    'HighlightedIdentifier': 14,
    'Decorator': 15,
}


def styleDescriptions():
    return propertyID.keys()


def defaultStyle():
    defaultStyle = {
        'UnclosedString': ['Consolas', '#000000', 10, False, False, '#00fd00'],
        'Decorator': ['Consolas', '#00cc00', 10, False, False, '#ffffff'],
        'Default': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'HighlightedIdentifier': ['Consolas', '#900090', 10, False, False, '#ffffff'],
        'CommentBlock': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'FunctionMethodName': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'DoubleQuotedString': ['Consolas', '#00aa00', 10, False, False, '#ffffff'],
        'Operator': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'TripleSingleQuotedString': ['Consolas', '#00aa00', 10, False, False, '#ffffff'],
        'Number': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'Keyword': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'Identifier': ['Consolas', '#000000', 10, False, False, '#ffffff'],
        'ClassName': ['Consolas', '#0000ff', 10, False, False, '#ffffff'],
        'SingleQuotedString': ['Consolas', '#00aa00', 10, False, False, '#ffffff'],
        'TripleDoubleQuotedString': ['Consolas', '#00aa00', 10, False, False, '#ffffff'],
        'Comment': ['Consolas', '#0000ff', 10, False, False, '#ffffff']}

    return defaultStyle


class PythonLexer(QsciLexerPython):

    def __init__(self, style, paper):
        QsciLexerPython.__init__(self)

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

    def keywords(self, set):
        # 1 to 9 sets
        if set == 1:
            k = keyword.kwlist
            s = k[0]
            for i in k[1:]:
                s += ' ' + i
            return s
        elif set == 2:
            s = ''
            for i in dir(__builtins__):
                s += ' ' + i
            return s
