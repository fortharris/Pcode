# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2012 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing an exporter for TeX.
"""

# This code is a port of the C++ code found in SciTE 1.74
# Original code: Copyright 1998-2006 by Neil Hodgson <neilh@scintilla.org>

import os
from PyQt4.Qsci import QsciScintilla
from Extensions import Global

class ExporterTEX():
    """
    Class implementing an exporter for TeX.
    """
    CHARZ = ord('z') - ord('a') + 1

    def __init__(self, editor, progressIndicator, parent=None):
        """
        Constructor

        @param editor reference to the editor object (QScintilla.Editor.Editor)
        @param parent parent object of the exporter (QObject)
        """
        self.editor = editor
        self.progressIndicator = progressIndicator

    def __getTexRGB(self, color):
        """
        Private method to convert a color object to a TeX color string

        @param color color object to convert (QColor)
        @return TeX color string (string)
        """
        # texcolor[rgb]{0,0.5,0}{....}
        rf = color.red() / 256.0
        gf = color.green() / 256.0
        bf = color.blue() / 256.0

        # avoid breakage due to locale setting
        r = int(rf * 10 + 0.5)
        g = int(gf * 10 + 0.5)
        b = int(bf * 10 + 0.5)

        return "{0:d}.{1:d}, {2:d}.{3:d}, {4:d}.{5:d}".format(
               r // 10, r % 10, g // 10, g % 10, b // 10, b % 10)

    def __texStyle(self, style):
        """
        Private method to calculate a style name string for a given style number.

        @param style style number (integer)
        @return style name string (string)
        """
        buf = ""
        if style == 0:
            buf = "a"
        else:
            while style > 0:
                buf += chr(ord('a') + (style % self.CHARZ))
                style //= self.CHARZ
        return buf

    def __defineTexStyle(self, font, color, paper, file, istyle):
        """
        Private method to define a new TeX style.

        @param font the font to be used (QFont)
        @param color the foreground color to be used (QColor)
        @param paper the background color to be used (QColor)
        @param file reference to the open file to write to (file object)
        @param istyle style number (integer)
        """
        closing_brackets = 3
        file.write("\\newcommand{{\\pcode{0}}}[1]{{\\noindent{{\\ttfamily{{".format(
                   self.__texStyle(istyle)))
        if font.italic():
            file.write("\\textit{")
            closing_brackets += 1
        if font.bold():
            file.write("\\textbf{")
            closing_brackets += 1
        if color != self.defaultColor:
            file.write("\\textcolor[rgb]{{{0}}}{{".format(self.__getTexRGB(color)))
            closing_brackets += 1
        if paper != self.defaultPaper:
            file.write("\\colorbox[rgb]{{{0}}}{{".format(self.__getTexRGB(paper)))
            closing_brackets += 1
        file.write("#1{0}\n".format('}' * closing_brackets))

    def exportSource(self, filename):
        """
        Public method performing the export.
        """
        self.editor.recolor(0, -1)

        tabSize = 4

        onlyStylesUsed = True

        lex = self.editor.lexer
        self.defaultPaper = lex and \
                            lex.paper(QsciScintilla.STYLE_DEFAULT) or \
                            self.editor.paper().name()
        self.defaultColor = lex and \
                            lex.color(QsciScintilla.STYLE_DEFAULT) or \
                            self.editor.color().name()
        self.defaultFont = lex and \
                            lex.color(QsciScintilla.STYLE_DEFAULT) or \
                            Global.getDefaultFont()

        lengthDoc = self.editor.length()
        styleIsUsed = {}
        if onlyStylesUsed:
            for index in range(QsciScintilla.STYLE_MAX + 1):
                styleIsUsed[index] = False
            # check the used styles
            pos = 0
            while pos < lengthDoc:
                styleIsUsed[self.editor.styleAt(pos) & 0x7F] = True
                pos += 1
        else:
            for index in range(QsciScintilla.STYLE_MAX + 1):
                styleIsUsed[index] = True
        styleIsUsed[QsciScintilla.STYLE_DEFAULT] = True

        f = open(filename, "w", encoding="utf-8")

        f.write("\\documentclass[a4paper]{article}\n")
        f.write("\\usepackage[a4paper,margin=1.5cm]{geometry}\n")
        f.write("\\usepackage[T1]{fontenc}\n")
        f.write("\\usepackage{color}\n")
        f.write("\\usepackage{alltt}\n")
        f.write("\\usepackage{times}\n")
        if self.editor.isUtf8():
            f.write("\\usepackage[utf8]{inputenc}\n")
        else:
            f.write("\\usepackage[latin1]{inputenc}\n")

        if lex:
            istyle = 0
            while istyle <= QsciScintilla.STYLE_MAX:
                if (istyle <= QsciScintilla.STYLE_DEFAULT or \
                    istyle > QsciScintilla.STYLE_LASTPREDEFINED) and \
                   styleIsUsed[istyle]:
                    if lex.description(istyle) or \
                       istyle == QsciScintilla.STYLE_DEFAULT:
                        font = lex.font(istyle)
                        colour = lex.color(istyle)
                        paper = lex.paper(istyle)

                        self.__defineTexStyle(font, colour, paper, f, istyle)
                istyle += 1
        else:
            colour = self.editor.color()
            paper = self.editor.paper()
            font = Global.getDefaultFont()

            self.__defineTexStyle(font, colour, paper, f, 0)
            self.__defineTexStyle(font, colour, paper, f,
                                  QsciScintilla.STYLE_DEFAULT)

        f.write("\\begin{document}\n\n")
        title = os.path.basename(filename)
        f.write("Source File: {0}\n\n\\noindent\n\\tiny{{\n".format(title))

        styleCurrent = self.editor.styleAt(0)
        f.write("\\pcode{0}{{".format(self.__texStyle(styleCurrent)))

        lineIdx = 0
        pos = 0
        utf8 = self.editor.isUtf8()
        utf8Ch = b""
        utf8Len = 0

        while pos < lengthDoc:
            ch = self.editor.byteAt(pos)
            style = self.editor.styleAt(pos)
            if style != styleCurrent:
                # new style
                f.write("}}\n\\pcode{0}{{".format(self.__texStyle(style)))
                styleCurrent = style

            if ch == b'\t':
                ts = tabSize - (lineIdx % tabSize)
                lineIdx += ts - 1
                f.write("\\hspace*{{{0:d}em}}".format(ts))
            elif ch == b'\\':
                f.write("{\\textbackslash}")
            elif ch in [b'>', b'<', b'@']:
                f.write("${0}$".format(ch[0]))
            elif ch in [b'{', b'}', b'^', b'_', b'&', b'$', b'#', b'%', b'~']:
                f.write("\\{0}".format(ch[0]))
            elif ch in [b'\r', b'\n']:
                lineIdx = -1    # because incremented below
                if ch == b'\r' and self.editor.byteAt(pos + 1) == b'\n':
                    pos += 1    # skip the LF
                styleCurrent = self.editor.styleAt(pos + 1)
                f.write("}} \\\\\n\\pcode{0}{{".format(
                        self.__texStyle(styleCurrent)))
            elif ch == b' ':
                if self.editor.byteAt(pos + 1) == b' ':
                    f.write("{\\hspace*{1em}}")
                else:
                    f.write(' ')
            else:
                if ord(ch) > 127 and utf8:
                    utf8Ch += ch
                    if utf8Len == 0:
                        if (utf8Ch[0] & 0xF0) == 0xF0:
                            utf8Len = 4
                        elif (utf8Ch[0] & 0xE0) == 0xE0:
                            utf8Len = 3
                        elif (utf8Ch[0] & 0xC0) == 0xC0:
                            utf8Len = 2
                    elif len(utf8Ch) == utf8Len:
                        ch = utf8Ch.decode('utf8')
                        f.write(ch)
                        utf8Ch = b""
                        utf8Len = 0
                else:
                    f.write(ch.decode())
            lineIdx += 1
            pos += 1
            self.progressIndicator.updateProgress.emit(int((pos * 100) / lengthDoc))

        # close last empty style macros and document too
        f.write("}\n} %end tiny\n\n\\end{document}\n")
        f.close()
