import ast
from PyQt4 import QtCore, QtGui
from pyflakes.checker import Checker as flakeChecker
from Xtra import pep8
from Xtra import autopep8
import os.path


class ErrorCheckerThread(QtCore.QThread):

    newAlerts = QtCore.pyqtSignal(list, bool)

    def run(self):
        messages = []
        try:
            warnings = flakeChecker(ast.parse(
                self.editorTabWidget.getSource()))
            warnings.messages.sort(key=lambda a: a.lineno)
            for warning in warnings.messages:
                fname = warning.filename
                lineno = warning.lineno
                message = warning.message
                args = warning.message_args
                messages.append((lineno, message % (args), args))
            self.newAlerts.emit(messages, False)
        except Exception as err:
            error_text = err.args[1][3]
            msg = err.msg.capitalize() + '.'
            line = err.lineno
            offset = err.args[1][2]

            messages.append((1, line, msg, None, offset))
            self.newAlerts.emit(messages, True)

    def runCheck(self, editorTabWidget):
        self.editorTabWidget = editorTabWidget
        self.start()


class Pep8CheckerThread(QtCore.QThread):

    newAlerts = QtCore.pyqtSignal(list)

    def run(self):
        checkList = []
        try:
            styleGuide = pep8.StyleGuide(reporter=Pep8Report)
            report = styleGuide.check_files([os.path.join("temp","temp8.py")])
            for i in report.all_errors:
                fname = i[0]
                lineno = i[1]
                offset = i[2]
                code = i[3]
                error = i[4]

                if code is None:
                    # means the code has been marked to be ignored
                    continue
                checkList.append((fname, lineno, offset, code, error))
        except Exception as err:
            print(err)
        self.newAlerts.emit(checkList)

    def runCheck(self, editorTabWidget):
        self.editorTabWidget = editorTabWidget
        self.start()


class Pep8Report (pep8.BaseReport):

    def __init__(self, options):
        super(Pep8Report, self).__init__(options)

        self.all_errors = []

    def error(self, line_number, offset, text, check):
        code = super(Pep8Report, self).error(line_number, offset, text, check)

        err = (self.filename, line_number, offset, code, text)
        self.all_errors.append(err)
#
#class AutoPep8FixerOtions(object):
#    def __init__(self):
#        self.verbose = 0 #
#        self.diff # print the diff for the fixed source
#        self.in_place # make changes to files in place
#        self.recursive # run recursively; must be used with --in-place or diff
#        self.list_fixes # list codes for fixes; used by --ignore and --select
#        self.exclude # exclude files/directories that match these comma-separated globs
#        self.max_line_length = infinite # maximum number of additional pep8 passes (default: infinite)
#        self.select # fix only these errors/warnings (e.g. E4,W)
#        self.ignore # do not fix these errors/warnings '
#        self.aggressive # enable non-whitespace changes; multiple -a result in more aggressive changes
#        self.jobs # number of parallel jobs; match CPU count if value is less than 1
#

class AutoPep8FixerThread(QtCore.QThread):

    new = QtCore.pyqtSignal(str)

    def run(self):
        try:
            options = {
                'in_place': None, 'pep8_passes': 100, 'list_fixes': None,
                'jobs': 1, 'ignore': ['E226', 'E24'], 'verbose': 0,
                'diff': None, 'select': '', 'exclude': [], 'aggressive': 0,
                'recursive': None, 'max_line_length': 79}

            fixed = autopep8.fix_string(self.editorTabWidget.getSource())
            self.new.emit(fixed)
        except Exception as err:
            print(err)

    def runFix(self, editorTabWidget):
        self.editorTabWidget = editorTabWidget
        self.start()


class Pep8View(QtGui.QTreeWidget):

    def __init__(self, editorTabWidget, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)

        self.editorTabWidget = editorTabWidget

        self.fixerThread = AutoPep8FixerThread()
        self.fixerThread.new.connect(self.autoPep8Done)

        self.setColumnCount(3)
        self.setHeaderLabels(["", "#", "Style Guide"])
        self.setAutoScroll(True)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 50)

        self.createActions()

    def autoPep8Done(self, fixedCode):
        self.editorTabWidget.busyWidget.showBusy(False)
        editor = self.editorTabWidget.getEditor()
        editor.beginUndoAction()
        editor.selectAll()
        editor.removeSelectedText()
        editor.insert(fixedCode)
        editor.endUndoAction()

    def contextMenuEvent(self, event):
        selectedItems = self.selectedItems()
        if len(selectedItems) > 0:
            item = selectedItems[0]
            fixable = item.data(9, 2)
            #self.fixAct.setEnabled(fixable)
            #self.fixAllAct.setEnabled(fixable)
            self.contextMenu.exec_(event.globalPos())

    def fixErrors(self):
        self.fixerThread.runFix(self.editorTabWidget)
        self.editorTabWidget.busyWidget.showBusy(True,
                                                 "Applying Style Guide... please wait!")

    def createActions(self):
        self.fixAct = QtGui.QAction(
            "Fix Selected (Not Ready)", self, statusTip="Fix Selected")
        self.fixAct.setDisabled(True)

        self.fixAllAct = \
            QtGui.QAction(
                "Fix All Occurrences (Not Ready)", self, statusTip="Fix All Occurrences")
        self.fixAllAct.setDisabled(True)

        self.fixModuleAct = \
            QtGui.QAction(
                "Fix All Issues", self, statusTip="Fix All Issues",
                triggered=self.fixErrors)

        self.contextMenu = QtGui.QMenu()
        self.contextMenu.addAction(self.fixAct)
        self.contextMenu.addAction(self.fixAllAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.fixModuleAct)


class NoAssistanceWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        mainLayout = QtGui.QHBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        label = QtGui.QLabel('No Assistance')
        label.setScaledContents(True)
        label.setMinimumWidth(200)
        label.setMinimumHeight(25)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        mainLayout.addWidget(label)

        mainLayout.addStretch(1)


class Assistant(QtGui.QStackedWidget):

    def __init__(self, editorTabWidget, bottomStackSwitcher, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)

        self.useData = editorTabWidget.useData
        self.currentCodeIsPython = False

        supportedFixes = autopep8.supported_fixes()
        self.autopep8SupportDict = {}
        for i in supportedFixes:
            self.autopep8SupportDict[i[0]] = i[1]

        self.addWidget(NoAssistanceWidget())

        self.errorView = QtGui.QTreeWidget()
        self.errorView.setColumnCount(3)
        self.errorView.setHeaderLabels(["", "#", "Alert"])
        self.errorView.setAutoScroll(True)
        self.errorView.setColumnWidth(0, 50)
        self.errorView.setColumnWidth(1, 50)
        self.errorView.itemPressed.connect(self.alertPressed)
        self.addWidget(self.errorView)

        self.pep8View = Pep8View(editorTabWidget)
        self.pep8View.itemPressed.connect(self.pep8Pressed)
        self.addWidget(self.pep8View)

        self.codeCheckerTimer = QtCore.QTimer()
        self.codeCheckerTimer.setSingleShot(True)
        self.codeCheckerTimer.setInterval(500)
        self.codeCheckerTimer.timeout.connect(self.runCheck)

        self.editorTabWidget = editorTabWidget
        self.editorTabWidget.currentEditorTextChanged.connect(
            self.codeCheckerTimer.start)
        self.editorTabWidget.currentChanged.connect(self.changeWorkingMode)

        self.bottomStackSwitcher = bottomStackSwitcher

        self.codeCheckerThread = ErrorCheckerThread()
        self.codeCheckerThread.newAlerts.connect(self.updateAlerts)

        self.pep8CheckerThread = Pep8CheckerThread()
        self.pep8CheckerThread.newAlerts.connect(self.updatePep8)

        if self.useData.SETTINGS["EnableAssistance"] == "False":
            self.setCurrentIndex(0)
        else:
            if self.useData.SETTINGS["EnableAlerts"] == "True":
                self.setCurrentIndex(1)
            if self.useData.SETTINGS["enableStyleGuide"] == "True":
                self.setCurrentIndex(2)

    def setAssistance(self, index=None):
        if index == None:
            if self.useData.SETTINGS["EnableAlerts"] == "True":
                self.setCurrentIndex(1)
            if self.useData.SETTINGS["enableStyleGuide"] == "True":
                self.setCurrentIndex(2)
        else:
            self.setCurrentIndex(index)

        self.bottomStackSwitcher.setCount(self, '')

        self.startTimer()

    def changeWorkingMode(self):
        if self.editorTabWidget.getEditorData("fileType") == "python":
            self.currentCodeIsPython = True
            self.codeCheckerTimer.start()
        else:
            self.currentCodeIsPython = False
            self.errorView.clear()
            self.pep8View.clear()
            self.bottomStackSwitcher.setCount(self, '')

    def startTimer(self):
        if self.currentCodeIsPython:
            self.codeCheckerTimer.start()

    def updateAlerts(self, alertsList, critical):
        if self.currentCodeIsPython:
            self.errorView.clear()
            editor = self.editorTabWidget.getEditor()
            editor.clearErrorMarkerAndIndicator()
            if critical:
                item = alertsList[0]
                item = self.createItem(item[0], item[
                                       1], item[2], item[3], item[4])
                self.errorView.addTopLevelItem(item)

                lineno = int(item.text(1)) - 1
                offset = item.data(10, 2)
                msg = item.text(2)

                lineText = editor.text(lineno)
                l = len(lineText)
                diff = l - len(lineText.lstrip())
                if diff == offset:
                    startPos = 0
                else:
                    startPos = diff

                editor.markerAdd(lineno, 9)
                self.editorTabWidget.updateEditorData("errorLine", lineno)
                editor.fillIndicatorRange(lineno, startPos, lineno,
                                          offset, editor.syntaxErrorIndicator)
                editor.annotate(lineno, msg.capitalize(),
                                editor.annotationErrorStyle)
                self.bottomStackSwitcher.setCurrentWidget(self)
            else:
                for i in alertsList:
                    item = self.createItem(0, i[0], i[1], i[2])
                    self.errorView.addTopLevelItem(item)
                self.editorTabWidget.updateEditorData("errorLine", None)
            self.bottomStackSwitcher.setCount(self,
                                              str(len(alertsList)))
            if len(alertsList) == 0:
                parentItem = QtGui.QTreeWidgetItem()
                item = QtGui.QTreeWidgetItem()
                item.setText(2, "<No Alerts>")
                item.setFlags(QtCore.Qt.NoItemFlags)
                parentItem.addChild(item)
                self.errorView.addTopLevelItem(parentItem)
                parentItem.setExpanded(True)

    def createItem(self, itemType, line, message, args=None, offset=None):
        item = QtGui.QTreeWidgetItem(itemType)
        if itemType == 0:
            item.setIcon(0, QtGui.QIcon(
                os.path.join("Resources","images","alerts","_0035_Flashlight")))
        elif itemType == 1:
            item.setIcon(0, QtGui.QIcon(
                os.path.join("Resources","images","alerts","construction")))
        item.setText(1, str(line))
        item.setText(2, message)
        item.setData(10, 2, offset)
        item.setData(10, 3, args)

        return item

    def updatePep8(self, checkList):
        if self.currentCodeIsPython:
            self.pep8View.clear()
            for i in checkList:
                item = QtGui.QTreeWidgetItem()
                if i[3] in self.autopep8SupportDict:
                    icon = QtGui.QIcon(os.path.join("Resources","images","security","allowed"))
                    item.setData(9, 2, True)
                else:
                    icon = QtGui.QIcon(
                        os.path.join("Resources","images","security","requesting"))
                    item.setData(9, 2, False)
                item.setIcon(0, icon)
                item.setText(1, str(i[1]))
                item.setText(2, i[4])
                item.setData(10, 2, i[2])
                item.setData(11, 2, i[3])
                self.pep8View.addTopLevelItem(item)
            if len(checkList) == 0:
                parentItem = QtGui.QTreeWidgetItem()
                item = QtGui.QTreeWidgetItem()
                item.setText(2, "<No Issues>")
                item.setFlags(QtCore.Qt.NoItemFlags)
                parentItem.addChild(item)
                self.pep8View.addTopLevelItem(parentItem)
                parentItem.setExpanded(True)
            self.bottomStackSwitcher.setCount(self,
                                              str(len(checkList)))

    def alertPressed(self, item):
        # XXX: Fixme this only works if args is not empty
        lineno = int(item.text(1)) - 1
        word = item.data(10, 3)
        editor = self.editorTabWidget.focusedEditor()
        text = editor.text(lineno)
        if word is None:
            editor.showLine(lineno)
        else:
            word = word[0]
            start = text.find(word)
            end = start + len(word)
            editor.setSelection(lineno, start, lineno, end)
        editor.ensureLineVisible(lineno)

    def pep8Pressed(self, item):
        lineno = int(item.text(1)) - 1
        self.editorTabWidget.showLine(lineno)

    def runCheck(self):
        if self.useData.SETTINGS["EnableAssistance"] == "False":
            return
        if self.useData.SETTINGS["EnableAlerts"] == "True":
            self.codeCheckerThread.runCheck(self.editorTabWidget)
        if self.useData.SETTINGS["enableStyleGuide"] == "True":
            saved = self.editorTabWidget.saveToTemp('pep8')
            if saved:
                self.pep8CheckerThread.runCheck(self.editorTabWidget)
