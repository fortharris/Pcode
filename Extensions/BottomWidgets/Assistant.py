import os
import ast
import logging
import traceback
from Extensions.qt_bindings import QtCore, QtGui
from pyflakes.checker import Checker as flakeChecker
import pycodestyle as pep8
import autopep8


class ErrorCheckerThread(QtCore.QThread):

    newAlerts = QtCore.Signal(list, bool)

    def run(self):
        messages = []
        try:
            warnings = flakeChecker(ast.parse(self.source))
            warnings.messages.sort(key=lambda a: a.lineno)
            for warning in warnings.messages:
                lineno = warning.lineno
                message = warning.message
                args = warning.message_args
                messages.append((lineno, message % (args), args))
            self.newAlerts.emit(messages, False)
        except SyntaxError as err:
            msg = err.msg.capitalize() + '.'
            line = err.lineno or 1
            offset = err.offset or 0

            messages.append((1, line, msg, None, offset))
            self.newAlerts.emit(messages, True)

    def runCheck(self, source):
        self.source = source

        self.start()


class Pep8CheckerThread(QtCore.QThread):

    newAlerts = QtCore.Signal(list)

    def run(self):
        checkList = []
        try:
            styleGuide = pep8.StyleGuide(reporter=Pep8Report)
            report = styleGuide.check_files([self.tempPath])
            for i in report.all_errors:
                lineno = i[1]
                offset = i[2]
                code = i[3]
                error = i[4]

                if code is None:
                    # means the code has been marked to be ignored
                    continue
                checkList.append((i[0], lineno, offset, code, error))
        except Exception:
            logging.error(traceback.format_exc())
        self.newAlerts.emit(checkList)

    def runCheck(self, tempPath):
        self.tempPath = tempPath
        self.start()


class Pep8Report (pep8.BaseReport):

    def __init__(self, options):
        super(Pep8Report, self).__init__(options)

        self.all_errors = []

    def error(self, line_number, offset, text, check):
        code = super(Pep8Report, self).error(line_number, offset, text, check)

        err = (self.filename, line_number, offset, code, text)
        self.all_errors.append(err)

class AutoPep8FixerThread(QtCore.QThread):

    new = QtCore.Signal()

    def run(self):
        try:
            file = self.tempPath
            # Build a complete options namespace via autopep8 itself so every
            # attribute modern autopep8 expects is present (a hand-rolled
            # object would miss newer fields like hang_closing/global_config).
            options = autopep8.parse_args(
                [file, "--in-place", "--aggressive", "--aggressive"],
                apply_config=False)
            autopep8.fix_file(file, options)
            self.new.emit()
        except Exception:
            logging.error(traceback.format_exc())

    def runFix(self, tempPath):
        self.tempPath = tempPath
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

    def autoPep8Done(self):
        self.editorTabWidget.busyWidget.showBusy(False)
        
        editor = self.editorTabWidget.getEditor()
        with open(self.editorTabWidget.pep8TempPath, "r") as file:
            editor.setText(file.read())
        self.editorTabWidget.getEditor().removeBookmarks()
        self.editorTabWidget.enableBookmarkButtons(False)

    def contextMenuEvent(self, event):
        selectedItems = self.selectedItems()
        if len(selectedItems) > 0:
            self.contextMenu.exec(event.globalPos())

    def fixErrors(self):
        # just in case autopep8 check has not been done already
        self.editorTabWidget.saveToTemp('pep8')
        self.fixerThread.runFix(self.editorTabWidget.pep8TempPath)
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
        self.refactor = editorTabWidget.refactor

        self.currentCodeIsPython = False

        supportedFixes = autopep8.supported_fixes()
        self.autopep8SupportDict = {}
        for i in supportedFixes:
            self.autopep8SupportDict[i[0]] = i[1]

        self.addWidget(NoAssistanceWidget())

        self.errorView = QtGui.QTreeWidget()
        self.errorView.setColumnCount(3)
        self.errorView.setHeaderLabels(["", "#", "Alerts"])
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
        self.codeCheckerTimer.timeout.connect(self.runCheck)

        self.editorTabWidget = editorTabWidget
        self.editorTabWidget.currentEditorTextChanged.connect(
            self.startCodeCheckerTimer)
        self.editorTabWidget.currentChanged.connect(self.changeWorkingMode)

        self.bottomStackSwitcher = bottomStackSwitcher

        self.codeCheckerThread = ErrorCheckerThread()
        self.codeCheckerThread.newAlerts.connect(self.updateAlertsView)

        self.pep8CheckerThread = Pep8CheckerThread()
        self.pep8CheckerThread.newAlerts.connect(self.updatePep8View)

        if not self.useData.setting_bool("EnableAssistance"):
            self.setCurrentIndex(0)
        else:
            if self.useData.setting_bool("EnableAlerts"):
                self.setCurrentIndex(1)
            if self.useData.setting_bool("enableStyleGuide"):
                self.setCurrentIndex(2)

        self.extendedErrorsCount = 0
        self.alertsCount = 0

    def startCodeCheckerTimer(self):
        self.codeCheckerTimer.start(800)

    def setAssistance(self, index=None):
        if index is None:
            if self.useData.setting_bool("EnableAlerts"):
                self.setCurrentIndex(1)
            if self.useData.setting_bool("enableStyleGuide"):
                self.setCurrentIndex(2)
        else:
            self.setCurrentIndex(index)

        self.bottomStackSwitcher.setCount(self, '')

        self.startTimer()

    def _cancel_running_checks(self):
        self.codeCheckerTimer.stop()
        if self.codeCheckerThread.isRunning():
            self.codeCheckerThread.terminate()
            self.codeCheckerThread.wait(200)
        if self.pep8CheckerThread.isRunning():
            self.pep8CheckerThread.terminate()
            self.pep8CheckerThread.wait(200)

    def changeWorkingMode(self):
        self._cancel_running_checks()
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

    def updateAlertsView(self, alertsList, critical):
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
                startPos = l - len(lineText.lstrip())

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
            self.bottomStackSwitcher.setCount(self, str(len(alertsList)))
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
                os.path.join("Resources", "images", "alerts", "_0035_Flashlight")))
        elif itemType == 1:
            item.setIcon(0, QtGui.QIcon(
                os.path.join("Resources", "images", "alerts", "construction")))
        item.setText(1, str(line))
        item.setText(2, message)
        item.setData(10, 2, offset)
        item.setData(10, 3, args)

        return item

    def updatePep8View(self, checkList):
        if self.currentCodeIsPython:
            self.pep8View.clear()
            for i in checkList:
                item = QtGui.QTreeWidgetItem()
                if i[3] in self.autopep8SupportDict:
                    icon = QtGui.QIcon(
                        os.path.join("Resources", "images", "security", "allowed"))
                    item.setData(9, 2, True)
                else:
                    icon = QtGui.QIcon(
                        os.path.join("Resources", "images", "security", "requesting"))
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
        lineno = int(item.text(1)) - 1
        args = item.data(10, 3)
        offset = item.data(10, 2)
        editor = self.editorTabWidget.focusedEditor()
        text = editor.text(lineno)
        if args is None or args == () or args == "":
            editor.showLine(lineno)
            if offset is not None:
                try:
                    col = int(offset)
                    editor.setSelection(lineno, max(0, col - 1), lineno, col)
                except (TypeError, ValueError):
                    pass
        else:
            word = args[0] if isinstance(args, (tuple, list)) else str(args)
            start = text.find(word)
            if start < 0:
                # Fall back: highlight from message token or whole line
                parts = item.text(2).split()
                for token in parts:
                    start = text.find(token.strip("'\",()"))
                    if start >= 0:
                        word = token.strip("'\",()")
                        break
            if start >= 0:
                editor.setSelection(lineno, start, lineno, start + len(word))
            else:
                editor.showLine(lineno)
        editor.ensureLineVisible(lineno)

    def pep8Pressed(self, item):
        lineno = int(item.text(1)) - 1
        self.editorTabWidget.showLine(lineno)

    def runCheck(self):
        if not self.useData.setting_bool("EnableAssistance"):
            return
        if (self.codeCheckerThread.isRunning()
                or self.pep8CheckerThread.isRunning()):
            self.codeCheckerTimer.start(800)
            return
        if self.useData.setting_bool("EnableAlerts"):
            self.codeCheckerThread.runCheck(self.editorTabWidget.getSource())
        if self.useData.setting_bool("enableStyleGuide"):
            saved = self.editorTabWidget.saveToTemp('pep8')
            if saved:
                self.pep8CheckerThread.runCheck(self.editorTabWidget.pep8TempPath)
