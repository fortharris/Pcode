# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2012 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing an exporter for HTML.
"""

# This code is a port of the C++ code found in SciTE 1.74
# Original code: Copyright 1998-2006 by Neil Hodgson <neilh@scintilla.org>


import os, re
from PyQt4 import QtGui
from PyQt4.Qsci import QsciScintilla

class HTMLGenerator(object):
    """
    Class implementing an HTML generator for exporting source code.
    """
    
    _escape = re.compile("[&<>\"\u0080-\uffff]")

    _escape_map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
    }
    
    def __init__(self, editor, progressIndicator):
        self.editor = editor
        self.progressIndicator = progressIndicator
        
    def escape_entities(self, m, map=_escape_map):
        """
        Function to encode html entities.
        
        @param m the match object
        @param map the map of entities to encode
        @return the converted text (string)
        """
        char = m.group()
        text = map.get(char)
        if text is None:
            text = "&#{0:d};".format(ord(char))
        return text
        

    def html_encode(self, text, pattern=_escape):
        """
        Function to correctly encode a text for html.
        
        @param text text to be encoded (string)
        @param pattern search pattern for text to be encoded (string)
        @return the encoded text (string)
        """
        if not text:
            return ""
        text = pattern.sub(self.escape_entities, text)
        return text

    def generate(self, tabSize=4, useTabs=False, wysiwyg=True, folding=False,
                 onlyStylesUsed=False, titleFullPath=False):
        """
        Public method to generate HTML for the source editor.

        @keyparam tabSize size of tabs (integer)
        @keyparam useTabs flag indicating the use of tab characters (boolean)
        @keyparam wysiwyg flag indicating colorization (boolean)
        @keyparam folding flag indicating usage of fold markers
        @keyparam onlyStylesUsed flag indicating to include only style definitions
            for styles used in the source (boolean)
        @keyparam titleFullPath flag indicating to include the full file path
            in the title tag (boolean)
        @return generated HTML text (string)
        """
        self.editor.recolor(0, -1)
        fileName = os.path.basename(titleFullPath)

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

        html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD''' \
            ''' XHTML 1.0 Transitional//EN"\n''' \
            ''' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n''' \
            '''<html xmlns="http://www.w3.org/1999/xhtml">\n''' \
            '''<head>\n'''
        if titleFullPath:
            html += '''<title>{0}</title>\n'''.format(fileName)
        else:
            html += '''<title>{0}</title>\n'''.format(
                os.path.basename(fileName))
        html += '''<meta name="Generator" content="Pcode" />\n''' \
            '''<meta http-equiv="Content-Type" ''' \
            '''content="text/html; charset=utf-8" />\n'''
        if folding:
            html += '''<script language="JavaScript" type="text/javascript">\n''' \
                    '''<!--\n''' \
                    '''function symbol(id, sym) {\n''' \
                    '''  if (id.textContent == undefined) {\n''' \
                    '''    id.innerText = sym;\n''' \
                    '''  } else {\n''' \
                    '''    id.textContent = sym;\n''' \
                    '''  }\n''' \
                    '''}\n''' \
                    '''function toggle(id) {\n''' \
                    '''  var thislayer = document.getElementById('ln' + id);\n''' \
                    '''  id -= 1;\n''' \
                    '''  var togline = document.getElementById('hd' + id);\n''' \
                    '''  var togsym = document.getElementById('bt' + id);\n''' \
                    '''  if (thislayer.style.display == 'none') {\n''' \
                    '''    thislayer.style.display = 'block';\n''' \
                    '''    togline.style.textDecoration = 'none';\n''' \
                    '''    symbol(togsym, '- ');\n''' \
                    '''  } else {\n''' \
                    '''    thislayer.style.display = 'none';\n''' \
                    '''    togline.style.textDecoration = 'underline';\n''' \
                    '''    symbol(togsym, '+ ');\n''' \
                    '''  }\n''' \
                    '''}\n''' \
                    '''//-->\n''' \
                    '''</script>\n'''

        lex = self.editor.lexer
        if lex:
            bgColour = lex.paper(QsciScintilla.STYLE_DEFAULT).name()
        else:
            bgColour = self.editor.paper().name()

        html += '''<style type="text/css">\n'''
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
                        if istyle == QsciScintilla.STYLE_DEFAULT:
                            html += '''span {\n'''
                        else:
                            html += '''.S{0:d} {{\n'''.format(istyle)
                        if font.italic():
                            html += '''    font-style: italic;\n'''
                        if font.bold():
                            html += '''    font-weight: bold;\n'''
                        if wysiwyg:
                            html += '''    font-family: '{0}';\n'''.format(
                                    font.family())
                        html += '''    color: {0};\n'''.format(colour.name())
                        if istyle != QsciScintilla.STYLE_DEFAULT and \
                           bgColour != paper.name():
                            html += '''    background: {0};\n'''.format(
                                    paper.name())
                            html += '''    text-decoration: inherit;\n'''
                        if wysiwyg:
                            html += '''    font-size: {0:d}pt;\n'''.format(
                                    QtGui.QFontInfo(font).pointSize())
                        html += '''}\n'''
                    else:
                        styleIsUsed[istyle] = False
                istyle += 1
        else:
            colour = self.editor.color()
            paper = self.editor.paper()
            font = QtGui.QFont("Courier New", 12)
            html += '''.S0 {\n'''
            if font.italic():
                html += '''    font-style: italic;\n'''
            if font.bold():
                html += '''    font-weight: bold;\n'''
            if wysiwyg:
                html += '''    font-family: '{0}';\n'''.format(font.family())
            html += '''    color: {0};\n'''.format(colour.name())
            if bgColour != paper.name():
                html += '''    background: {0};\n'''.format(paper.name())
                html += '''    text-decoration: inherit;\n'''
            if wysiwyg:
                html += '''    font-size: {0:d}pt;\n'''.format(
                        QtGui.QFontInfo(font).pointSize())
            html += '''}\n'''
        html += '''</style>\n'''
        html += '''</head>\n'''

        html += '''<body bgcolor="{0}">\n'''.format(bgColour)
        line = self.editor.lineAt(0)
        level = self.editor.foldLevelAt(line) - QsciScintilla.SC_FOLDLEVELBASE
        levelStack = [level]
        styleCurrent = self.editor.styleAt(0)
        inStyleSpan = False
        inFoldSpan = False
        # Global span for default attributes
        if wysiwyg:
            html += '''<span>'''
        else:
            html += '''<pre>'''

        if folding:
            if self.editor.foldFlagsAt(line) & \
               QsciScintilla.SC_FOLDLEVELHEADERFLAG:
                html += '''<span id="hd{0:d}" onclick="toggle('{1:d}')">'''\
                        .format(line, line + 1)
                html += '''<span id="bt{0:d}">- </span>'''.format(line)
                inFoldSpan = True
            else:
                html += '''&nbsp; '''

        if styleIsUsed[styleCurrent]:
            html += '''<span class="S{0:0d}">'''.format(styleCurrent)
            inStyleSpan = True

        column = 0
        pos = 0
        utf8 = self.editor.isUtf8()
        utf8Ch = b""
        utf8Len = 0

        while pos < lengthDoc:
            ch = self.editor.byteAt(pos)
            style = self.editor.styleAt(pos)
            if style != styleCurrent:
                if inStyleSpan:
                    html += '''</span>'''
                    inStyleSpan = False
                if ch not in [b'\r', b'\n']:  # no need of a span for the EOL
                    if styleIsUsed[style]:
                        html += '''<span class="S{0:d}">'''.format(style)
                        inStyleSpan = True
                    styleCurrent = style

            if ch == b' ':
                if wysiwyg:
                    prevCh = b''
                    if column == 0:
                        # at start of line, must put a &nbsp;
                        # because regular space will be collapsed
                        prevCh = b' '
                    while pos < lengthDoc and self.editor.byteAt(pos) == b' ':
                        if prevCh != b' ':
                            html += ' '
                        else:
                            html += '''&nbsp;'''
                        prevCh = self.editor.byteAt(pos)
                        pos += 1
                        column += 1
                    pos -= 1
                    # the last incrementation will be done by the outer loop
                else:
                    html += ' '
                    column += 1
            elif ch == b'\t':
                ts = tabSize - (column % tabSize)
                if wysiwyg:
                    html += '''&nbsp;''' * ts
                    column += ts
                else:
                    if useTabs:
                        html += '\t'
                        column += 1
                    else:
                        html += ' ' * ts
                        column += ts
            elif ch in [b'\r', b'\n']:
                if inStyleSpan:
                    html += '''</span>'''
                    inStyleSpan = False
                if inFoldSpan:
                    html += '''</span>'''
                    inFoldSpan = False
                if ch == b'\r' and self.editor.byteAt(pos + 1) == b'\n':
                    pos += 1  # CR+LF line ending, skip the "extra" EOL char
                column = 0
                if wysiwyg:
                    html += '''<br />'''

                styleCurrent = self.editor.styleAt(pos + 1)
                if folding:
                    line = self.editor.lineAt(pos + 1)
                    newLevel = self.editor.foldLevelAt(line)

                    if newLevel < level:
                        while levelStack[-1] > newLevel:
                            html += '''</span>'''
                            levelStack.pop()
                    html += '\n'  # here to get clean code
                    if newLevel > level:
                        html += '''<span id="ln{0:d}">'''.format(line)
                        levelStack.append(newLevel)
                    if self.editor.foldFlagsAt(line) & \
                       QsciScintilla.SC_FOLDLEVELHEADERFLAG:
                        html += \
                            '''<span id="hd{0:d}" onclick="toggle('{1:d}')">'''\
                            .format(line, line + 1)
                        html += '''<span id="bt{0:d}">- </span>'''.format(line)
                        inFoldSpan = True
                    else:
                        html += '''&nbsp; '''
                    level = newLevel
                else:
                    html += '\n'

                if styleIsUsed[styleCurrent] and \
                   self.editor.byteAt(pos + 1) not in [b'\r', b'\n']:
                    # We know it's the correct next style,
                    # but no (empty) span for an empty line
                    html += '''<span class="S{0:0d}">'''.format(styleCurrent)
                    inStyleSpan = True
            else:
                if ch == b'<':
                    html += '''&lt;'''
                elif ch == b'>':
                    html += '''&gt'''
                elif ch == b'&':
                    html += '''&amp;'''
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
                            column -= 1  # will be incremented again later
                        elif len(utf8Ch) == utf8Len:
                            ch = utf8Ch.decode('utf8')
                            html += self.html_encode(ch)
                            utf8Ch = b""
                            utf8Len = 0
                        else:
                            column -= 1  # will be incremented again later
                    else:
                        html += ch.decode()
                column += 1

            pos += 1
            self.progressIndicator.updateProgress.emit(int((pos * 100) / lengthDoc))

        if inStyleSpan:
            html += '''</span>'''

        if folding:
            while levelStack:
                html += '''</span>'''
                levelStack.pop()

        if wysiwyg:
            html += '''</span>'''
        else:
            html += '''</pre>'''

        html += '''</body>\n</html>\n'''

        return html
