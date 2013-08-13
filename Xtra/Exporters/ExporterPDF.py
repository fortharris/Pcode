# -*- coding: utf-8 -*-

# Copyright (c) 2007 - 2012 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing an exporter for PDF.
"""

# This code is a port of the C++ code found in SciTE 1.74
# Original code: Copyright 1998-2006 by Neil Hodgson <neilh@scintilla.org>


from PyQt4 import QtGui
from PyQt4.Qsci import QsciScintilla
from Extensions import Global

PDF_FONT_DEFAULT = 1    # Helvetica
PDF_FONTSIZE_DEFAULT = 10
PDF_SPACING_DEFAULT = 1.2
PDF_MARGIN_DEFAULT = 72  # 1.0"
PDF_ENCODING = "WinAnsiEncoding"

PDFfontNames = [
    "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic"
]
PDFfontAscenders = [629, 718, 699]
PDFfontDescenders = [157, 207, 217]
PDFfontWidths = [600,   0,   0]

PDFpageSizes = {
    # name   : (height, width)
    "Letter": (792, 612),
    "A4": (842, 595),
}


class PDFStyle(object):
    """
    Simple class to store the values of a PDF style.
    """
    def __init__(self):
        """
        Constructor
        """
        self.fore = ""
        self.font = 0


class PDFObjectTracker(object):
    """
    Class to conveniently handle the tracking of PDF objects
    so that the cross-reference table can be built (PDF1.4Ref(p39))
    All writes to the file are passed through a PDFObjectTracker object.
    """
    def __init__(self, file):
        """
        Constructor

        @param file file object open for writing (file)
        """
        self.file = file
        self.offsetList = []
        self.index = 1

    def write(self, objectData):
        """
        Public method to write the data to the file.

        @param objectData data to be written (integer or string)
        """
        if isinstance(objectData, int):
            self.file.write("{0:d}".format(objectData))
        else:
            self.file.write(objectData)

    def add(self, objectData):
        """
        Public method to add a new object.

        @param objectData data to be added (integer or string)
        @return object number assigned to the supplied data (integer)
        """
        self.offsetList.append(self.file.tell())
        self.write(self.index)
        self.write(" 0 obj\n")
        self.write(objectData)
        self.write("endobj\n")
        ind = self.index
        self.index += 1
        return ind

    def xref(self):
        """
        Public method to build the xref table.

        @return file offset of the xref table (integer)
        """
        xrefStart = self.file.tell()
        self.write("xref\n0 ")
        self.write(self.index)
        # a xref entry *must* be 20 bytes long (PDF1.4Ref(p64))
        # so extra space added; also the first entry is special
        self.write("\n0000000000 65535 f \n")
        ind = 0
        while ind < len(self.offsetList):
            self.write("{0:010d} 00000 n \n".format(self.offsetList[ind]))
            ind += 1
        return xrefStart

class PDFRender(object):
    """
    Class to manage line and page rendering.

    Apart from startPDF, endPDF everything goes in via add() and nextLine()
    so that line formatting and pagination can be done properly.
    """
    def __init__(self):
        """
        Constructor
        """
        self.pageStarted = False
        self.firstLine = False
        self.pageCount = 0
        self.pageData = ""
        self.style = {}
        self.segStyle = ""
        self.segment = ""
        self.pageMargins = {
            "left": 72,
            "right": 72,
            "top": 72,
            "bottom": 72,
        }
        self.fontSize = 0
        self.fontSet = 0
        self.leading = 0.0
        self.pageWidth = 0
        self.pageHeight = 0
        self.pageContentStart = 0
        self.xPos = 0.0
        self.yPos = 0.0
        self.justWhiteSpace = False
        self.oT = None

    def fontToPoints(self, thousandths):
        """
        Public method to convert the font size to points.

        @return point size of the font (integer)
        """
        return self.fontSize * thousandths / 1000.0

    def setStyle(self, style_):
        """
        Public method to set a style.

        @param style_ style to be set (integer)
        @return the PDF string to set the given style (string)
        """
        styleNext = style_
        if style_ == -1:
            styleNext = self.styleCurrent

        buf = ""
        if styleNext != self.styleCurrent or style_ == -1:
            if self.style[self.styleCurrent].font != self.style[styleNext].font or \
               style_ == -1:
                buf += "/F{0:d} {1:d} Tf ".format(self.style[styleNext].font + 1,
                                                  self.fontSize)
            if self.style[self.styleCurrent].fore != self.style[styleNext].fore or \
               style_ == -1:
                buf += "{0}rg ".format(self.style[styleNext].fore)
        return buf

    def startPDF(self):
        """
        Public method to start the PDF document.
        """
        if self.fontSize <= 0:
            self.fontSize = PDF_FONTSIZE_DEFAULT

        # leading is the term for distance between lines
        self.leading = self.fontSize * PDF_SPACING_DEFAULT

        # sanity check for page size and margins
        pageWidthMin = int(self.leading) + \
                       self.pageMargins["left"] + self.pageMargins["right"]
        if self.pageWidth < pageWidthMin:
            self.pageWidth = pageWidthMin
        pageHeightMin = int(self.leading) + \
                       self.pageMargins["top"] + self.pageMargins["bottom"]
        if self.pageHeight < pageHeightMin:
            self.pageHeight = pageHeightMin

        # start to write PDF file here (PDF1.4Ref(p63))
        # ASCII>127 characters to indicate binary-possible stream
        self.oT.write("%PDF-1.3\n%??\n")
        self.styleCurrent = QsciScintilla.STYLE_DEFAULT

        # build objects for font resources; note that font objects are
        # *expected* to start from index 1 since they are the first objects
        # to be inserted (PDF1.4Ref(p317))
        for i in range(4):
            buffer = \
                "<</Type/Font/Subtype/Type1/Name/F{0:d}/BaseFont/{1}/Encoding/{2}>>\n"\
                .format(i + 1, PDFfontNames[self.fontSet * 4 + i], PDF_ENCODING)
            self.oT.add(buffer)

        self.pageContentStart = self.oT.index

    def endPDF(self):
        """
        Public method to end the PDF document.
        """
        if self.pageStarted:
            # flush buffers
            self.endPage()

        # refer to all used or unused fonts for simplicity
        resourceRef = self.oT.add(
            "<</ProcSet[/PDF/Text]\n/Font<</F1 1 0 R/F2 2 0 R/F3 3 0 R/F4 4 0 R>> >>\n")

        # create all the page objects (PDF1.4Ref(p88))
        # forward reference pages object; calculate its object number
        pageObjectStart = self.oT.index
        pagesRef = pageObjectStart + self.pageCount
        for i in range(self.pageCount):
            buffer = "<</Type/Page/Parent {0:d} 0 R\n" \
                     "/MediaBox[ 0 0 {1:d} {2:d}]\n" \
                     "/Contents {3:d} 0 R\n" \
                     "/Resources {4:d} 0 R\n>>\n".format(
                     pagesRef, self.pageWidth, self.pageHeight,
                     self.pageContentStart + i, resourceRef)
            self.oT.add(buffer)

        # create page tree object (PDF1.4Ref(p86))
        self.pageData = "<</Type/Pages/Kids[\n"
        for i in range(self.pageCount):
            self.pageData += "{0:d} 0 R\n".format(pageObjectStart + i)
        self.pageData += "]/Count {0:d}\n>>\n".format(self.pageCount)
        self.oT.add(self.pageData)

        # create catalog object (PDF1.4Ref(p83))
        buffer = "<</Type/Catalog/Pages {0:d} 0 R >>\n".format(pagesRef)
        catalogRef = self.oT.add(buffer)

        # append the cross reference table (PDF1.4Ref(p64))
        xref = self.oT.xref()

        # end the file with the trailer (PDF1.4Ref(p67))
        buffer = "trailer\n<< /Size {0:d} /Root {1:d} 0 R\n>>\nstartxref\n{2:d}\n%%EOF\n"\
                 .format(self.oT.index, catalogRef, xref)
        self.oT.write(buffer)

    def add(self, ch, style_):
        """
        Public method to add a character to the page.

        @param ch character to add (string)
        @param style_ number of the style of the character (integer)
        """
        if not self.pageStarted:
            self.startPage()

        # get glyph width (TODO future non-monospace handling)
        glyphWidth = self.fontToPoints(PDFfontWidths[self.fontSet])
        self.xPos += glyphWidth

        # if cannot fit into a line, flush, wrap to next line
        if self.xPos > self.pageWidth - self.pageMargins["right"]:
            self.nextLine()
            self.xPos += glyphWidth

        # if different style, then change to style
        if style_ != self.styleCurrent:
            self.flushSegment()
            # output code (if needed) for new style
            self.segStyle = self.setStyle(style_)
            self.stylePrev = self.styleCurrent
            self.styleCurrent = style_

        # escape these characters
        if ch == ')' or ch == '(' or ch == '\\':
            self.segment += '\\'
        if ch != ' ':
            self.justWhiteSpace = False
        self.segment += ch  # add to segment data

    def flushSegment(self):
        """
        Public method to flush a segment of data.
        """
        if len(self.segment) > 0:
            if self.justWhiteSpace:     # optimise
                self.styleCurrent = self.stylePrev
            else:
                self.pageData += self.segStyle
            self.pageData += "({0})Tj\n".format(self.segment)
            self.segment = ""
            self.segStyle = ""
            self.justWhiteSpace = True

    def startPage(self):
        """
        Public method to start a new page.
        """
        self.pageStarted = True
        self.firstLine = True
        self.pageCount += 1
        fontAscender = self.fontToPoints(PDFfontAscenders[self.fontSet])
        self.yPos = self.pageHeight - self.pageMargins["top"] - fontAscender

        # start a new page
        buffer = "BT 1 0 0 1 {0:d} {1:d} Tm\n".format(
            self.pageMargins["left"], int(self.yPos))

        # force setting of initial font, colour
        self.segStyle = self.setStyle(-1)
        buffer += self.segStyle
        self.pageData = buffer
        self.xPos = self.pageMargins["left"]
        self.segment = ""
        self.flushSegment()

    def endPage(self):
        """
        Public method to end a page.
        """
        self.pageStarted = False
        self.flushSegment()

        # build actual text object; +3 is for "ET\n"
        # PDF1.4Ref(p38) EOL marker preceding endstream not counted
        textObj = "<</Length {0:d}>>\nstream\n{1}ET\nendstream\n".format(
                  len(self.pageData) - 1 + 3, self.pageData)
        self.oT.add(textObj)

    def nextLine(self):
        """
        Public method to start a new line.
        """
        if not self.pageStarted:
            self.startPage()

        self.xPos = self.pageMargins["left"]
        self.flushSegment()

        # PDF follows cartesian coords, subtract -> down
        self.yPos -= self.leading
        fontDescender = self.fontToPoints(PDFfontDescenders[self.fontSet])
        if self.yPos < self.pageMargins["bottom"] + fontDescender:
            self.endPage()
            self.startPage()
            return

        if self.firstLine:
            # avoid breakage due to locale setting
            f = int(self.leading * 10 + 0.5)
            buffer = "0 -{0:d}.{1:d} TD\n".format(f // 10, f % 10)
            self.firstLine = False
        else:
            buffer = "T*\n"
        self.pageData += buffer


class ExporterPDF():
    """
    Class implementing an exporter for PDF.
    """
    def __init__(self, editor, progressIndicator, parent=None):
        """
        Constructor

        @param editor reference to the editor object (QScintilla.Editor.Editor)
        @param parent parent object of the exporter (QObject)
        """
        self.editor = editor
        self.progressIndicator = progressIndicator

    def __getPDFRGB(self, color):
        """
        Private method to convert a color object to the correct PDF color.

        @param color color object to convert (QColor)
        @return PDF color description (string)
        """
        pdfColor = ""
        for component in [color.red(), color.green(), color.blue()]:
            c = (component * 1000 + 127) // 255
            if c == 0 or c == 1000:
                pdfColor += "{0:d} ".format(c // 1000)
            else:
                pdfColor += "0.{0:03d} ".format(c)
        return pdfColor

    def exportSource(self, filename):
        """
        Public method performing the export.
        """
        self.pr = PDFRender()
        self.editor.recolor(0, -1)
        lex = self.editor.lexer

        tabSize = 4

        # get magnification value to add to default screen font size
        self.pr.fontSize = 0

        # set font family according to face name
        fontName = "Helvetica"
        self.pr.fontSet = PDF_FONT_DEFAULT
        if fontName == "Courier":
            self.pr.fontSet = 0
        elif fontName == "Helvetica":
            self.pr.fontSet = 1
        elif fontName == "Times":
            self.pr.fontSet = 2

        # page size: height, width,
        pageSize = "A4"
        try:
            pageDimensions = PDFpageSizes[pageSize]
        except KeyError:
            pageDimensions = PDFpageSizes["A4"]
        self.pr.pageHeight = pageDimensions[0]
        self.pr.pageWidth = pageDimensions[1]

        # page margins: left, right, top, bottom
        # < 0 to use PDF default values
        val = 36
        if val < 0:
            self.pr.pageMargins["left"] = PDF_MARGIN_DEFAULT
        else:
            self.pr.pageMargins["left"] = val
        val = 36
        if val < 0:
            self.pr.pageMargins["right"] = PDF_MARGIN_DEFAULT
        else:
            self.pr.pageMargins["right"] = val
        val = 36
        if val < 0:
            self.pr.pageMargins["top"] = PDF_MARGIN_DEFAULT
        else:
            self.pr.pageMargins["top"] = val
        val = 36
        if val < 0:
            self.pr.pageMargins["bottom"] = PDF_MARGIN_DEFAULT
        else:
            self.pr.pageMargins["bottom"] = val

        # collect all styles available for that 'language'
        # or the default style if no language is available...
        if lex:
            istyle = 0
            while istyle <= QsciScintilla.STYLE_MAX:
                if (istyle <= QsciScintilla.STYLE_DEFAULT or \
                    istyle > QsciScintilla.STYLE_LASTPREDEFINED):
                    if lex.description(istyle) or \
                       istyle == QsciScintilla.STYLE_DEFAULT:
                        style = PDFStyle()

                        font = lex.font(istyle)
                        if font.italic():
                            style.font |= 2
                        if font.bold():
                            style.font |= 1

                        colour = lex.color(istyle)
                        style.fore = self.__getPDFRGB(colour)
                        self.pr.style[istyle] = style

                    # grab font size from default style
                    if istyle == QsciScintilla.STYLE_DEFAULT:
                        fontSize = QtGui.QFontInfo(font).pointSize()
                        if fontSize > 0:
                            self.pr.fontSize += fontSize
                        else:
                            self.pr.fontSize = PDF_FONTSIZE_DEFAULT

                istyle += 1
        else:
            style = PDFStyle()

            font = Global.getDefaultFont()
            if font.italic():
                style.font |= 2
            if font.bold():
                style.font |= 1

            colour = self.editor.color()
            style.fore = self.__getPDFRGB(colour)
            self.pr.style[0] = style
            self.pr.style[QsciScintilla.STYLE_DEFAULT] = style

            fontSize = QtGui.QFontInfo(font).pointSize()
            if fontSize > 0:
                self.pr.fontSize += fontSize
            else:
                self.pr.fontSize = PDF_FONTSIZE_DEFAULT

        # save file in win ansi using cp1250
        f = open(filename, "w", encoding="cp1250", errors="backslashreplace")

        # initialise PDF rendering
        ot = PDFObjectTracker(f)
        self.pr.oT = ot
        self.pr.startPDF()

        # do here all the writing
        lengthDoc = self.editor.length()

        if lengthDoc == 0:
            self.pr.nextLine()  # enable zero length docs
        else:
            pos = 0
            column = 0
            utf8 = self.editor.isUtf8()
            utf8Ch = b""
            utf8Len = 0

            while pos < lengthDoc:
                ch = self.editor.byteAt(pos)
                style = self.editor.styleAt(pos)

                if ch == b'\t':
                    # expand tabs
                    ts = tabSize - (column % tabSize)
                    column += ts
                    self.pr.add(' ' * ts, style)
                elif ch == b'\r' or ch == b'\n':
                    if ch == b'\r' and self.editor.byteAt(pos + 1) == b'\n':
                        pos += 1
                    # close and begin a newline...
                    self.pr.nextLine()
                    column = 0
                else:
                    # write the character normally...
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
                            self.pr.add(ch, style)
                            utf8Ch = b""
                            utf8Len = 0
                        else:
                            column -= 1  # will be incremented again later
                    else:
                        self.pr.add(ch.decode(), style)
                    column += 1

                pos += 1
                self.progressIndicator.updateProgress.emit(int((pos * 100) / lengthDoc))

            # write required stuff and close the PDF file
            self.pr.endPDF()
            f.close()