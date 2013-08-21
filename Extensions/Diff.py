import sys

from PyQt4 import QtCore, QtGui
from difflib import SequenceMatcher

# This function is copied from python 2.3 and slightly modified.
# The header lines contain a tab after the filename.


def unified_diff(a, b, fromfile='', tofile='', fromfiledate='',
                 tofiledate='', n=3, lineterm='\n'):
    """
    Compare two sequences of lines; generate the delta as a unified diff.

    Unified diffs are a compact way of showing line changes and a few
    lines of context.  The number of context lines is set by 'n' which
    defaults to three.

    By default, the diff control lines (those with ---, +++, or @@) are
    created with a trailing newline.  This is helpful so that inputs
    created from file.readlines() result in diffs that are suitable for
    file.writelines() since both the inputs and outputs have trailing
    newlines.

    For inputs that do not have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The unidiff format normally has a header for filenames and modification
    times.  Any or all of these may be specified using strings for
    'fromfile', 'tofile', 'fromfiledate', and 'tofiledate'.  The modification
    times are normally expressed in the format returned by time.ctime().

    Example:

    <pre>
    &gt;&gt;&gt; for line in unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), 'Original', 'Current',
    ...             'Sat Jan 26 23:30:50 1991', 'Fri Jun 06 10:20:52 2003',
    ...             lineterm=''):
    ...     print line
    --- Original Sat Jan 26 23:30:50 1991
    +++ Current Fri Jun 06 10:20:52 2003
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    </pre>

    @param a first sequence of lines (list of strings)
    @param b second sequence of lines (list of strings)
    @param fromfile filename of the first file (string)
    @param tofile filename of the second file (string)
    @param fromfiledate modification time of the first file (string)
    @param tofiledate modification time of the second file (string)
    @param n number of lines of context (integer)
    @param lineterm line termination string (string)
    @return a generator yielding lines of differences
    """
    started = False
    for group in SequenceMatcher(None, a, b).get_grouped_opcodes(n):
        if not started:
            yield '--- {0}\t{1}{2}'.format(fromfile, fromfiledate, lineterm)
            yield '+++ {0}\t{1}{2}'.format(tofile, tofiledate, lineterm)
            started = True
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        yield "@@ -{0:d},{1:d} +{2:d},{3:d} @@{4}".format(
            i1 + 1, i2 - i1, j1 + 1, j2 - j1, lineterm)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    yield ' ' + line
                continue
            if tag == 'replace' or tag == 'delete':
                for line in a[i1:i2]:
                    yield '-' + line
            if tag == 'replace' or tag == 'insert':
                for line in b[j1:j2]:
                    yield '+' + line

# This function is copied from python 2.3 and slightly modified.
# The header lines contain a tab after the filename.


def context_diff(a, b, fromfile='', tofile='',
                 fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    """
    Compare two sequences of lines; generate the delta as a context diff.

    Context diffs are a compact way of showing line changes and a few
    lines of context.  The number of context lines is set by 'n' which
    defaults to three.

    By default, the diff control lines (those with *** or ---) are
    created with a trailing newline.  This is helpful so that inputs
    created from file.readlines() result in diffs that are suitable for
    file.writelines() since both the inputs and outputs have trailing
    newlines.

    For inputs that do not have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The context diff format normally has a header for filenames and
    modification times.  Any or all of these may be specified using
    strings for 'fromfile', 'tofile', 'fromfiledate', and 'tofiledate'.
    The modification times are normally expressed in the format returned
    by time.ctime().  If not specified, the strings default to blanks.

    Example:

    <pre>
    &gt;&gt;&gt; print ''.join(context_diff('one\ntwo\nthree\nfour\n'.splitlines(1),
    ...       'zero\none\ntree\nfour\n'.splitlines(1), 'Original', 'Current',
    ...       'Sat Jan 26 23:30:50 1991', 'Fri Jun 06 10:22:46 2003')),
    *** Original Sat Jan 26 23:30:50 1991
    --- Current Fri Jun 06 10:22:46 2003
    ***************
    *** 1,4 ****
      one
    ! two
    ! three
      four
    --- 1,4 ----
    + zero
      one
    ! tree
      four
    </pre>

    @param a first sequence of lines (list of strings)
    @param b second sequence of lines (list of strings)
    @param fromfile filename of the first file (string)
    @param tofile filename of the second file (string)
    @param fromfiledate modification time of the first file (string)
    @param tofiledate modification time of the second file (string)
    @param n number of lines of context (integer)
    @param lineterm line termination string (string)
    @return a generator yielding lines of differences
    """

    started = False
    prefixmap = {'insert': '+ ', 'delete':
                 '- ', 'replace': '! ', 'equal': '  '}
    for group in SequenceMatcher(None, a, b).get_grouped_opcodes(n):
        if not started:
            yield '*** {0}\t{1}{2}'.format(fromfile, fromfiledate, lineterm)
            yield '--- {0}\t{1}{2}'.format(tofile, tofiledate, lineterm)
            started = True

        yield '***************{0}'.format(lineterm)
        if group[-1][2] - group[0][1] >= 2:
            yield '*** {0:d},{1:d} ****{2}'.format(group[0][1] + 1, group[-1][2], lineterm)
        else:
            yield '*** {0:d} ****{1}'.format(group[-1][2], lineterm)
        visiblechanges = [e for e in group if e[0] in ('replace', 'delete')]
        if visiblechanges:
            for tag, i1, i2, _, _ in group:
                if tag != 'insert':
                    for line in a[i1:i2]:
                        yield prefixmap[tag] + line

        if group[-1][4] - group[0][3] >= 2:
            yield '--- {0:d},{1:d} ----{2}'.format(group[0][3] + 1, group[-1][4], lineterm)
        else:
            yield '--- {0:d} ----{1}'.format(group[-1][4], lineterm)
        visiblechanges = [e for e in group if e[0] in ('replace', 'insert')]
        if visiblechanges:
            for tag, _, _, j1, j2 in group:
                if tag != 'delete':
                    for line in b[j1:j2]:
                        yield prefixmap[tag] + line


class DiffWindow(QtGui.QTextEdit):

    def __init__(self, editor=None, snapShot=None, parent=None):
        QtGui.QTextEdit.__init__(self, parent)

        self.setReadOnly(True)

        self.editor = editor
        self.snapShot = snapShot

        self.filename1 = ''
        self.filename2 = ''

        if sys.platform == 'win32':
            self.setFontFamily("Lucida Console")
        else:
            self.setFontFamily("Monospace")

        self.cNormalFormat = self.currentCharFormat()
        self.cAddedFormat = self.currentCharFormat()
        self.cAddedFormat.setBackground(
            QtGui.QBrush(QtGui.QColor(190, 237, 190)))
        self.cRemovedFormat = self.currentCharFormat()
        self.cRemovedFormat.setBackground(
            QtGui.QBrush(QtGui.QColor(237, 190, 190)))
        self.cReplacedFormat = self.currentCharFormat()
        self.cReplacedFormat.setBackground(
            QtGui.QBrush(QtGui.QColor(190, 190, 237)))
        self.cLineNoFormat = self.currentCharFormat()
        self.cLineNoFormat.setBackground(
            QtGui.QBrush(QtGui.QColor(255, 220, 168)))

    def generateUnifiedDiff(self, a=None, b=None):
        """
        Private slot to generate a unified diff output.

        @param a first sequence of lines (list of strings)
        @param b second sequence of lines (list of strings)
        @param fromfile filename of the first file (string)
        @param tofile filename of the second file (string)
        @param fromfiledate modification time of the first file (string)
        @param tofiledate modification time of the second file (string)
        """
        self.clear()

        paras = 0

        if a is None:
            a = self.snapShot.text().splitlines()
        if b is None:
            b = self.editor.text().splitlines()

        fromfile = "Old"
        tofile = "New"

        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        for line in unified_diff(a, b, fromfile, tofile):
            if line.startswith('+') or line.startswith('>'):
                format = self.cAddedFormat
            elif line.startswith('-') or line.startswith('<'):
                format = self.cRemovedFormat
            elif line.startswith('@@'):
                format = self.cLineNoFormat
            else:
                format = self.cNormalFormat
            self.__appendText(line, format)
            paras += 1

        if paras == 0:
            self.__appendText(self.trUtf8(
                'There is no difference.'), self.cNormalFormat)

        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Start)
        self.setTextCursor(tc)
        self.ensureCursorVisible()

        QtGui.QApplication.restoreOverrideCursor()

        return (paras != 0)

    def generateContextDiff(self):
        """
        Private slot to generate a context diff output.

        @param a first sequence of lines (list of strings)
        @param b second sequence of lines (list of strings)
        @param fromfile filename of the first file (string)
        @param tofile filename of the second file (string)
        @param fromfiledate modification time of the first file (string)
        @param tofiledate modification time of the second file (string)
        """
        self.clear()

        paras = 0

        a = self.snapShot.text().splitlines()
        b = self.editor.text().splitlines()

        fromfile = "Old"
        tofile = "New"

        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        for line in context_diff(a, b, fromfile, tofile):
            if line.startswith('+ '):
                format = self.cAddedFormat
            elif line.startswith('- '):
                format = self.cRemovedFormat
            elif line.startswith('! '):
                format = self.cReplacedFormat
            elif (line.startswith('*** ') or line.startswith('--- ')) and paras > 1:
                format = self.cLineNoFormat
            else:
                format = self.cNormalFormat
            self.__appendText(line, format)
            paras += 1

        if paras == 0:
            self.__appendText(self.trUtf8(
                'There is no difference.'), self.cNormalFormat)

        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Start)
        self.setTextCursor(tc)
        self.ensureCursorVisible()

        QtGui.QApplication.restoreOverrideCursor()

    def __appendText(self, txt, format):
        """
        Private method to append text to the end of the contents pane.

        @param txt text to insert (string)
        @param format text format to be used (QTextCharFormat)
        """
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(tc)
        self.setCurrentCharFormat(format)
        self.insertPlainText(txt + '\n')
