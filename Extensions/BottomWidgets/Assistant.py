from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMenu, QPushButton, QStackedWidget, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget,
)

import os
import ast
import logging
import traceback
from pyflakes.checker import Checker as flakeChecker
import pycodestyle as pep8
import autopep8


class ErrorCheckerThread(QThread):

    newAlerts = pyqtSignal(list, bool)
    progress = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        self._cancelled = False
        messages = []
        try:
            self.progress.emit("Checking syntax…")
            warnings = flakeChecker(ast.parse(self.source))
            if self._cancelled:
                self.newAlerts.emit([], False)
                return
            warnings.messages.sort(key=lambda a: a.lineno)
            total = len(warnings.messages)
            for idx, warning in enumerate(warnings.messages):
                if self._cancelled:
                    break
                lineno = warning.lineno
                message = warning.message
                args = warning.message_args
                messages.append((lineno, message % (args), args))
                if idx and idx % 25 == 0:
                    self.progress.emit(
                        "Alerts: {0}/{1}…".format(idx, total))
                    self.newAlerts.emit(list(messages), False)
            if self._cancelled:
                self.progress.emit("Cancelled")
            self.newAlerts.emit(messages, False)
        except SyntaxError as err:
            if self._cancelled:
                self.newAlerts.emit([], False)
                return
            msg = err.msg.capitalize() + '.'
            line = err.lineno or 1
            offset = err.offset or 0

            messages.append((1, line, msg, None, offset))
            self.newAlerts.emit(messages, True)

    def runCheck(self, source):
        self.source = source
        self._cancelled = False
        self.start()


class Pep8CheckerThread(QThread):

    newAlerts = pyqtSignal(list)
    progress = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        self._cancelled = False
        checkList = []
        try:
            self.progress.emit("Checking style guide…")
            styleGuide = pep8.StyleGuide(reporter=Pep8Report)
            report = styleGuide.check_files([self.tempPath])
            for idx, i in enumerate(report.all_errors):
                if self._cancelled:
                    break
                lineno = i[1]
                offset = i[2]
                code = i[3]
                error = i[4]

                if code is None:
                    # means the code has been marked to be ignored
                    continue
                checkList.append((i[0], lineno, offset, code, error))
                if idx and idx % 25 == 0:
                    self.progress.emit(
                        "Style issues: {0}…".format(len(checkList)))
                    self.newAlerts.emit(list(checkList))
        except Exception:
            logging.error(traceback.format_exc())
        if self._cancelled:
            self.progress.emit("Cancelled")
        self.newAlerts.emit(checkList)

    def runCheck(self, tempPath):
        self.tempPath = tempPath
        self._cancelled = False
        self.start()


class Pep8Report (pep8.BaseReport):

    def __init__(self, options):
        super(Pep8Report, self).__init__(options)

        self.all_errors = []

    def error(self, line_number, offset, text, check):
        code = super(Pep8Report, self).error(line_number, offset, text, check)

        err = (self.filename, line_number, offset, code, text)
        self.all_errors.append(err)

class AutoPep8FixerThread(QThread):

    new = pyqtSignal()

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


class Pep8View(QTreeWidget):

    def __init__(self, editorTabWidget, parent=None):
        QTreeWidget.__init__(self, parent)

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
        self.fixAct = QAction(
            "Fix Selected (Not Ready)", self, statusTip="Fix Selected")
        self.fixAct.setDisabled(True)

        self.fixAllAct = \
            QAction(
                "Fix All Occurrences (Not Ready)", self, statusTip="Fix All Occurrences")
        self.fixAllAct.setDisabled(True)

        self.fixModuleAct = \
            QAction(
                "Fix All Issues", self, statusTip="Fix All Issues",
                triggered=self.fixErrors)

        self.contextMenu = QMenu()
        self.contextMenu.addAction(self.fixAct)
        self.contextMenu.addAction(self.fixAllAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.fixModuleAct)


class NoAssistanceWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        label = QLabel('No Assistance')
        label.setScaledContents(True)
        label.setMinimumWidth(200)
        label.setMinimumHeight(25)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        mainLayout.addWidget(label)

        mainLayout.addStretch(1)


class Assistant(QStackedWidget):

    def __init__(self, editorTabWidget, bottomStackSwitcher, parent=None):
        QStackedWidget.__init__(self, parent)

        self.useData = editorTabWidget.useData
        self.refactor = editorTabWidget.refactor

        self.currentCodeIsPython = False

        supportedFixes = autopep8.supported_fixes()
        self.autopep8SupportDict = {}
        for i in supportedFixes:
            self.autopep8SupportDict[i[0]] = i[1]

        # Outer layout: status/cancel bar above the stacked views.
        shell = QWidget(self)
        shellLayout = QVBoxLayout(shell)
        shellLayout.setContentsMargins(0, 0, 0, 0)
        shellLayout.setSpacing(2)

        statusRow = QHBoxLayout()
        self.statusLabel = QLabel("")
        self.statusLabel.setStyleSheet("color: gray; padding: 2px;")
        statusRow.addWidget(self.statusLabel, 1)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setEnabled(False)
        self.cancelButton.setMaximumWidth(80)
        self.cancelButton.clicked.connect(self.cancelChecks)
        statusRow.addWidget(self.cancelButton)
        shellLayout.addLayout(statusRow)

        self.views = QStackedWidget()
        shellLayout.addWidget(self.views, 1)

        # Keep QStackedWidget API: Assistant itself remains a stacked widget
        # with a single shell page so existing setCurrentIndex callers work
        # against the inner views via helpers below.
        self.addWidget(shell)
        QStackedWidget.setCurrentIndex(self, 0)

        self.views.addWidget(NoAssistanceWidget())

        self.errorView = QTreeWidget()
        self.errorView.setColumnCount(3)
        self.errorView.setHeaderLabels(["", "#", "Alerts"])
        self.errorView.setAutoScroll(True)
        self.errorView.setColumnWidth(0, 50)
        self.errorView.setColumnWidth(1, 50)
        self.errorView.itemPressed.connect(self.alertPressed)

        self.views.addWidget(self.errorView)

        self.pep8View = Pep8View(editorTabWidget)
        self.pep8View.itemPressed.connect(self.pep8Pressed)
        self.views.addWidget(self.pep8View)

        self.codeCheckerTimer = QTimer()
        self.codeCheckerTimer.setSingleShot(True)
        self.codeCheckerTimer.timeout.connect(self.runCheck)

        self.editorTabWidget = editorTabWidget
        self.editorTabWidget.currentEditorTextChanged.connect(
            self.startCodeCheckerTimer)
        self.editorTabWidget.currentChanged.connect(self.changeWorkingMode)

        self.bottomStackSwitcher = bottomStackSwitcher

        self.codeCheckerThread = ErrorCheckerThread()
        self.codeCheckerThread.newAlerts.connect(self.updateAlertsView)
        self.codeCheckerThread.progress.connect(self._set_status)
        self.codeCheckerThread.finished.connect(self._checks_finished)

        self.pep8CheckerThread = Pep8CheckerThread()
        self.pep8CheckerThread.newAlerts.connect(self.updatePep8View)
        self.pep8CheckerThread.progress.connect(self._set_status)
        self.pep8CheckerThread.finished.connect(self._checks_finished)

        if not self.useData.setting_bool("EnableAssistance"):
            self.views.setCurrentIndex(0)
        else:
            if self.useData.setting_bool("EnableAlerts"):
                self.views.setCurrentIndex(1)
            if self.useData.setting_bool("enableStyleGuide"):
                self.views.setCurrentIndex(2)

        self.extendedErrorsCount = 0
        self.alertsCount = 0

    def setCurrentIndex(self, index):
        # Route view switches to the inner stack; shell stays on page 0.
        if hasattr(self, "views"):
            self.views.setCurrentIndex(index)
        else:
            QStackedWidget.setCurrentIndex(self, index)

    def currentIndex(self):
        if hasattr(self, "views"):
            return self.views.currentIndex()
        return QStackedWidget.currentIndex(self)

    def _set_status(self, text):
        self.statusLabel.setText(text or "")
        busy = (self.codeCheckerThread.isRunning()
                or self.pep8CheckerThread.isRunning())
        self.cancelButton.setEnabled(busy)

    def _checks_finished(self):
        if (self.codeCheckerThread.isRunning()
                or self.pep8CheckerThread.isRunning()):
            return
        if self.statusLabel.text() != "Cancelled":
            self.statusLabel.setText("")
        self.cancelButton.setEnabled(False)

    def cancelChecks(self):
        self.codeCheckerTimer.stop()
        self.codeCheckerThread.cancel()
        self.pep8CheckerThread.cancel()
        self.statusLabel.setText("Cancelling…")
        self.cancelButton.setEnabled(False)

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
        self.codeCheckerThread.cancel()
        self.pep8CheckerThread.cancel()
        if self.codeCheckerThread.isRunning():
            self.codeCheckerThread.wait(500)
        if self.pep8CheckerThread.isRunning():
            self.pep8CheckerThread.wait(500)
        # Last resort if a stuck C extension won't yield.
        if self.codeCheckerThread.isRunning():
            self.codeCheckerThread.terminate()
            self.codeCheckerThread.wait(200)
        if self.pep8CheckerThread.isRunning():
            self.pep8CheckerThread.terminate()
            self.pep8CheckerThread.wait(200)
        self.cancelButton.setEnabled(False)
        self.statusLabel.setText("")

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
                parentItem = QTreeWidgetItem()
                item = QTreeWidgetItem()
                item.setText(2, "<No Alerts>")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                parentItem.addChild(item)
                self.errorView.addTopLevelItem(parentItem)
                parentItem.setExpanded(True)

    def createItem(self, itemType, line, message, args=None, offset=None):
        item = QTreeWidgetItem(itemType)
        if itemType == 0:
            item.setIcon(0, QIcon(
                os.path.join("Resources", "images", "alerts", "_0035_Flashlight")))
        elif itemType == 1:
            item.setIcon(0, QIcon(
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
                item = QTreeWidgetItem()
                if i[3] in self.autopep8SupportDict:
                    icon = QIcon(
                        os.path.join("Resources", "images", "security", "allowed"))
                    item.setData(9, 2, True)
                else:
                    icon = QIcon(
                        os.path.join("Resources", "images", "security", "requesting"))
                    item.setData(9, 2, False)
                item.setIcon(0, icon)
                item.setText(1, str(i[1]))
                item.setText(2, i[4])
                item.setData(10, 2, i[2])
                item.setData(11, 2, i[3])
                self.pep8View.addTopLevelItem(item)
            if len(checkList) == 0:
                parentItem = QTreeWidgetItem()
                item = QTreeWidgetItem()
                item.setText(2, "<No Issues>")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
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
        self.cancelButton.setEnabled(True)
        self.statusLabel.setText("Checking…")
        if self.useData.setting_bool("EnableAlerts"):
            self.codeCheckerThread.runCheck(self.editorTabWidget.getSource())
        if self.useData.setting_bool("enableStyleGuide"):
            saved = self.editorTabWidget.saveToTemp('pep8')
            if saved:
                self.pep8CheckerThread.runCheck(self.editorTabWidget.pep8TempPath)
        if (not self.codeCheckerThread.isRunning()
                and not self.pep8CheckerThread.isRunning()):
            self.cancelButton.setEnabled(False)
            self.statusLabel.setText("")
