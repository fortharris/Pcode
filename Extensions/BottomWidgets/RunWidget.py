import os
import re
import sys
import locale
from PyQt6.Qsci import QsciScintilla, QsciScintillaBase, QsciLexerCustom
from PyQt6.QtCore import (
    QByteArray, QCoreApplication, QIODevice, QProcess, QProcessEnvironment,
    QSize, Qt, pyqtSignal,
)
from PyQt6.QtGui import QAction, QColor, QIcon, QPalette
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QHBoxLayout, QLabel, QMenu, QMessageBox,
    QSizePolicy, QSpinBox, QToolButton, QVBoxLayout, QWidget,
)

from Extensions.settings_utils import to_bool, from_bool
from Extensions.BaseScintilla import BaseScintilla
from Extensions.PathLineEdit import PathLineEdit
from Extensions import Global
from Extensions import StyleSheet

default_encoding = locale.getpreferredencoding()


class SetRunParameters(QLabel):

    def __init__(self, projectSettings, projectPathDict, useData, parent=None):
        QLabel.__init__(self, parent)

        # QLabel ignores its layout in sizeHint(); height comes from overrides.
        self.setMinimumWidth(480)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.setBackgroundRole(QPalette.ColorRole.Window)
        self.setAutoFillBackground(True)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.projectSettings = projectSettings
        self.useData = useData
        self.projectPathDict = projectPathDict

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(12, 10, 12, 12)
        mainLayout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Run Parameters")
        title.setObjectName("toolWidgetNameLabel")
        header.addWidget(title)
        header.addStretch(1)
        self.hideButton = QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        header.addWidget(self.hideButton)
        mainLayout.addLayout(header)

        # --- Run ---
        mainLayout.addWidget(self._section("Run"))

        self.runTypeBox = QComboBox()
        self.runTypeBox.addItem("Run")
        self.runTypeBox.addItem("Profiler")
        self.runTypeBox.addItem("Trace")
        self.runTypeBox.addItem("Debug")
        if self.projectSettings["RunType"] == 'Profiler':
            self.runTypeBox.setCurrentIndex(1)
        elif self.projectSettings["RunType"] == 'Trace':
            self.runTypeBox.setCurrentIndex(2)
        elif self.projectSettings["RunType"] == 'Debug':
            self.runTypeBox.setCurrentIndex(3)
        self.runTypeBox.currentIndexChanged.connect(self.saveArguments)
        self.runTypeBox.currentIndexChanged.connect(self.runTypeChanged)
        mainLayout.addLayout(self._labeled_row("Mode", self.runTypeBox))

        self.traceTypeBox = QComboBox()
        self.traceTypeBox.addItem("Calling relationships")
        self.traceTypeBox.addItem("Functions called")
        self.traceTypeBox.addItem("Times lines are called")
        self.traceTypeBox.addItem("View currently running line of code")
        self.traceTypeBox.setCurrentIndex(int(
            self.projectSettings["TraceType"]))
        self.traceTypeBox.currentIndexChanged.connect(self.saveArguments)
        mainLayout.addWidget(self.traceTypeBox)
        if self.runTypeBox.currentIndex() != 2:
            self.traceTypeBox.hide()

        self.runWithArgsBox = QCheckBox("Pass arguments")
        if to_bool(self.projectSettings["RunWithArguments"]):
            self.runWithArgsBox.setChecked(True)
        self.runWithArgsBox.toggled.connect(self._argsToggled)
        mainLayout.addWidget(self.runWithArgsBox)

        argsWrap = QWidget()
        argsWrap.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        argsLayout = QHBoxLayout(argsWrap)
        argsLayout.setContentsMargins(18, 0, 0, 0)
        argsLayout.setSpacing(0)
        self.argumentsLine = PathLineEdit()
        self.argumentsLine.setPlaceholderText("Optional arguments…")
        self.argumentsLine.setText(self.projectSettings["RunArguments"])
        self.argumentsLine.textChanged.connect(self.saveArguments)
        argsLayout.addWidget(self.argumentsLine)
        mainLayout.addWidget(argsWrap)
        self.argumentsLine.setEnabled(self.runWithArgsBox.isChecked())

        self.clearOutputBox = QCheckBox("Clear output")
        if to_bool(self.projectSettings["ClearOutputWindowOnRun"]):
            self.clearOutputBox.setChecked(True)
        self.clearOutputBox.toggled.connect(self.saveArguments)
        mainLayout.addWidget(self.clearOutputBox)

        self.bufferSizeBox = QSpinBox()
        self.bufferSizeBox.setMaximum(999)
        self.bufferSizeBox.setMinimumWidth(90)
        self.bufferSizeBox.setValue(int(self.projectSettings['BufferSize']))
        self.bufferSizeBox.valueChanged.connect(self.saveArguments)
        mainLayout.addLayout(
            self._labeled_row("Max lines", self.bufferSizeBox, stretch=False))

        # --- Console ---
        mainLayout.addWidget(self._section("Console"))

        self.runPointBox = QComboBox()
        self.runPointBox.addItem("Internal Console")
        self.runPointBox.addItem("External Console")
        if not to_bool(self.projectSettings["RunInternal"]):
            self.runPointBox.setCurrentIndex(1)
        self.runPointBox.currentIndexChanged.connect(self.saveArguments)
        mainLayout.addLayout(self._labeled_row("Target", self.runPointBox))

        self.useVirtualEnvBox = QCheckBox("Use virtual environment")
        if to_bool(self.projectSettings["UseVirtualEnv"]):
            self.useVirtualEnvBox.setChecked(True)
        self.useVirtualEnvBox.toggled.connect(self.setDefaultInterpreter)
        mainLayout.addWidget(self.useVirtualEnvBox)

        self.debugWaitBox = QCheckBox("Wait for debugger")
        if to_bool(self.projectSettings.get("DebugWait")):
            self.debugWaitBox.setChecked(True)
        self.debugWaitBox.toggled.connect(self.saveArguments)
        mainLayout.addWidget(self.debugWaitBox)

        # --- Interpreter ---
        mainLayout.addWidget(self._section("Interpreter"))
        self.installedPythonVersionBox = QComboBox()
        self.installedPythonVersionBox.setMinimumWidth(280)
        self.updateInstalledInterpreters()
        self.installedPythonVersionBox.currentIndexChanged.connect(
            self.setDefaultInterpreter)
        mainLayout.addLayout(
            self._labeled_row("Python", self.installedPythonVersionBox))

        self.setLayout(mainLayout)
        self.setDefaultInterpreter()

    def sizeHint(self):
        lay = self.layout()
        if lay is not None:
            hint = lay.sizeHint()
            return QSize(max(480, hint.width()), hint.height())
        return QLabel.sizeHint(self)

    def minimumSizeHint(self):
        lay = self.layout()
        if lay is not None:
            hint = lay.minimumSize()
            return QSize(max(480, hint.width()), hint.height())
        return QLabel.minimumSizeHint(self)

    def showEvent(self, event):
        QLabel.showEvent(self, event)
        # Parent overlay may have sized us from QLabel's bogus hint; grow now.
        self.updateGeometry()
        self.adjustSize()

    def _section(self, text):
        label = QLabel(text)
        label.setObjectName("toolWidgetSectionLabel")
        label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        return label

    def _field_label(self, text):
        label = QLabel(text)
        label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return label

    def _labeled_row(self, text, widget, stretch=True):
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self._field_label(text))
        if stretch:
            row.addWidget(widget, 1)
        else:
            row.addWidget(widget)
            row.addStretch(1)
        return row

    def _argsToggled(self, checked):
        self.argumentsLine.setEnabled(checked)
        self.saveArguments()

    def updateInstalledInterpreters(self):
        self.installedPythonVersionBox.clear()
        if len(self.useData.SETTINGS["InstalledInterpreters"]) > 0:
            for i in self.useData.SETTINGS["InstalledInterpreters"]:
                self.installedPythonVersionBox.addItem(i)
                if not to_bool(self.projectSettings["UseVirtualEnv"]):
                    index = self.installedPythonVersionBox.findText(
                        self.projectSettings["DefaultInterpreter"])
                    if index != -1:
                        self.installedPythonVersionBox.setCurrentIndex(index)
        else:
            self.installedPythonVersionBox.addItem("<No Python installed>")

    def runTypeChanged(self, index):
        if index == 2:
            self.traceTypeBox.show()
        else:
            self.traceTypeBox.hide()

    def saveArguments(self):
        self.projectSettings["RunWithArguments"] = from_bool(
            self.runWithArgsBox.isChecked())
        self.projectSettings[
            "RunArguments"] = self.argumentsLine.text().strip()
        self.projectSettings["ClearOutputWindowOnRun"] = from_bool(
            self.clearOutputBox.isChecked())
        self.projectSettings["BufferSize"] = str(self.bufferSizeBox.value())
        self.projectSettings["RunType"] = self.runTypeBox.currentText()
        self.projectSettings["RunInternal"] = from_bool(
            self.runPointBox.currentIndex() == 0)
        self.projectSettings["TraceType"] = str(
            self.traceTypeBox.currentIndex())
        self.projectSettings["DebugWait"] = from_bool(
            self.debugWaitBox.isChecked())

    def setDefaultInterpreter(self):
        use_venv = self.useVirtualEnvBox.isChecked()
        self.installedPythonVersionBox.setEnabled(not use_venv)
        if use_venv:
            from Extensions.python_paths import venv_python
            self.projectSettings["DefaultInterpreter"] = venv_python(
                self.projectPathDict["venvdir"])
        else:
            if len(self.useData.SETTINGS["InstalledInterpreters"]) > 0:
                self.projectSettings["DefaultInterpreter"] = \
                    self.installedPythonVersionBox.currentText()
            else:
                self.projectSettings["DefaultInterpreter"] = 'None'
        self.projectSettings["UseVirtualEnv"] = from_bool(use_venv)
        self.projectSettings["DebugWait"] = from_bool(
            self.debugWaitBox.isChecked())


class OutputLexer(QsciLexerCustom):

    def __init__(self, parent=None):
        QsciLexerCustom.__init__(self, parent)

        self._styles = {
            0: 'Default',
            1: 'ErrorInfo',
            2: 'OutputInfo',
            3: 'ExitInfo',
            4: 'Start'
            }
        for key in self._styles:
            setattr(self, self._styles[key], key)

    def description(self, style):
        return self._styles.get(style, '')

    def defaultColor(self, style):
        if style == self.Default:
            return QColor('#ffffff')
        elif style == self.ErrorInfo:
            return QColor('#E6DB74')
        elif style == self.OutputInfo:
            return QColor('#FFFFFF')
        elif style == self.ExitInfo:
            return QColor('#3DA3EF')
        elif style == self.Start:
            return QColor('#7FE22A')
        return QsciLexerCustom.defaultColor(self, style)

    def defaultFont(self, style):
        if style == self.Default:
            return Global.getDefaultFont()
        elif style == self.ErrorInfo:
            return Global.getDefaultFont()
        elif style == self.OutputInfo:
            return Global.getDefaultFont()
        elif style == self.ExitInfo:
            return Global.getDefaultFont()
        elif style == self.Start:
            return Global.getDefaultFont()
        return QsciLexerCustom.defaultFont(self, style)

    def defaultPaper(self, style):
        return QColor('#000000')

    def defaultEolFill(self, style):
        return True

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        # scintilla works with encoded bytes, not decoded characters.
        # this matters if the source contains non-ascii characters and
        # a multi-byte encoding is used (e.g. utf-8)
        source = ''
        if end > editor.length():
            end = editor.length()
        if end > start:
            if sys.hexversion >= 0x02060000:
                # faster when styling big files, but needs python 2.6
                source = bytearray(end - start)
                editor.SendScintilla(
                    editor.SCI_GETTEXTRANGE, start, end, source)
            else:
                source = editor.text().encode('utf-8')
        if not source:
            return

        self.startStyling(start, 0x1f)


class RunWidget(BaseScintilla):

    loadProfile = pyqtSignal()
    debugStatusChanged = pyqtSignal(str)

    def __init__(
        self, bottomStackSwitcher, projectData, useData, editorTabWidget, vSplitter, runProjectAct, stopRunAct,
            runFileAct, parent=None):
        BaseScintilla.__init__(self, parent)

        self.projectData = projectData
        self.runProjectAct = runProjectAct
        self.stopRunAct = stopRunAct
        self.runFileAct = runFileAct
        self.editorTabWidget = editorTabWidget
        self.parent = parent
        self.vSplitter = vSplitter
        self.bottomStackSwitcher = bottomStackSwitcher
        self.useData = useData

        self.profileMode = False
        self.tracebackRe = re.compile(r'(\s)*File "(.*?)", line \d.+')

        self.setMarginWidth(1, 0)
        self.toggleInsertOrOvertype()

        self.linkIndicator = self.indicatorDefine(
            QsciScintilla.IndicatorStyle.PlainIndicator, 8)
        self.setIndicatorForegroundColor(QColor(
            "#474747"), self.linkIndicator)
        self.setIndicatorDrawUnder(True, self.linkIndicator)

        self.lexer = OutputLexer(self)
        self.setLexer(self.lexer)
        self.setFont(Global.getDefaultFont())
        self.openMode = QIODevice.OpenModeFlag.ReadWrite
        self.currentProcess = None

        self.setCaretForegroundColor(QColor("#ffffff"))
        self.setWrapMode(QsciScintilla.WrapWord)
        self.setSelectionBackgroundColor(QColor("#391EE8"))
        self.setSelectionForegroundColor(QColor("#FFFFFF"))

        self.runProcess = QProcess(self)
        self.runProcess.errorOccurred.connect(self.writeProcessError)
        self.runProcess.stateChanged.connect(self.stateChanged)
        self.runProcess.readyReadStandardOutput.connect(self.writeOutput)
        self.runProcess.readyReadStandardError.connect(self.writeError)
        self.runProcess.started.connect(self.processStarted)
        self.runProcess.finished.connect(self.writeExitStatus)
        self.runProcess.finished.connect(self.processEnded)

        self.copyAct = QAction("Copy", self,
                                     statusTip="Copy", triggered=self.copyText)
        self.contextMenu = QMenu()
        self.contextMenu.addAction(self.copyAct)

        self.setReadOnly(True)
        self.blocking_cursor_pos = (0, 0)

        self.setStyleSheet("QsciScintilla {border: none;}")

    def leaveEvent(self, event):
        self.clearAllIndicators(self.linkIndicator)

        super(RunWidget, self).leaveEvent(event)

    def mouseMoveEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())

        line = self.getHoveredLine(x, y)
        lineText = self.text(line)

        l = len(lineText)
        offset = l - len(lineText.lstrip())

        self.clearAllIndicators(self.linkIndicator)

        if self.tracebackRe.match(lineText):
            self.fillIndicatorRange(
                line, offset, line, (l - 1), self.linkIndicator)

        super(RunWidget, self).mouseMoveEvent(event)

    def copyText(self):
        cb = self.editorTabWidget.app.clipboard()
        if self.hasSelectedText():
            cb.setText(self.selectedText())
        else:
            cb.setText(self.text())

    def stateChanged(self, newState):
        if newState == 2:
            self.vSplitter.showRunning()
            self.setReadOnly(False)
        else:
            self.setReadOnly(True)

    def insertInput(self, text):
        self.append('\n')
        data = QByteArray()
        data.append(bytes(text + '\n', encoding="utf-8"))
        self.runProcess.write(data)

    def writeProcessError(self, processError):
        self.writeOutput()
        self.writeError()
        if processError == 0:
            self.printout(">>> FailedToStart!\n", 3)
        elif processError == 1:
            self.printout(">>> Crashed!\n", 3)
        elif processError == 2:
            self.printout(">>> Timedout!\n", 3)
        elif processError == 3:
            self.printout(">>> WriteError!\n", 3)
        elif processError == 4:
            self.printout(">>> ReadError!\n", 3)
        elif processError == 5:
            self.printout(">>> UnknownError!\n", 3)
        self.bottomStackSwitcher.setCurrentWidget(self)

    def writeOutput(self):
        while self.runProcess.canReadLine():
            if self.currentProcess is None:
                break
            text = self.runProcess.readLine().data().decode(
                default_encoding)
            self.printout(text, 2)

    def writeError(self):
        text = \
            self.runProcess.readAllStandardError().data().decode(
                default_encoding)
        self.printout(text, 1)
        self.bottomStackSwitcher.setCurrentWidget(self)

    def writeExitStatus(self, exitCode, exitStatus):
        self.writeOutput()
        self.writeError()
        if exitStatus == QProcess.ExitStatus.NormalExit:
            self.printout(">>> Exit: {0}\n".format(str(exitCode)), 3)
        else:
            # error will be displayed instead by writeProcessError
            pass
        self.currentProcess = None
        if exitCode == 1:
            self.vSplitter.showError()
        else:
            self.vSplitter.showNormal()

    def processStarted(self):
        self.runProjectAct.setVisible(False)
        self.stopRunAct.setVisible(True)
        self.runFileAct.setEnabled(False)

    def processEnded(self):
        self.runProjectAct.setVisible(True)
        self.stopRunAct.setVisible(False)
        self.runFileAct.setEnabled(True)

        self.currentProcess = None
        self.debugStatusChanged.emit("")
        if self.profileMode:
            self.loadProfile.emit()
            self.profileMode = False

    def printout(self, text, styleNum):
        start = self.length()
        self.SendScintilla(QsciScintillaBase.SCI_STARTSTYLING, start)
        self.append(text)
        self.recolor(start, -1)
        self.SendScintilla(QsciScintillaBase.SCI_SETSTYLING, len(text),
                           styleNum)
        QCoreApplication.processEvents()
        self.setFirstVisibleLine(self.lines())
        self.blocking_cursor_pos = self.position('eof')
        self.setCursorPosition(self.blocking_cursor_pos[
                               0], self.blocking_cursor_pos[1])

    def pythonPath(self):
        if self.projectData["DefaultInterpreter"] == "None":
            QMessageBox.critical(
                self, "Run", "No Python interpreter to run your code. Please install Python.")
            return None
        else:
            if os.path.exists(self.projectData["DefaultInterpreter"]):
                if len(self.useData.SETTINGS["InstalledInterpreters"]) == 0:
                    QMessageBox.critical(
                        self, "Run", "Python must be installed for virtual environment to work.")
                    return None
                else:
                    return self.projectData["DefaultInterpreter"]
            else:
                QMessageBox.critical(
                    self, "Run", "The current Python interpreter is not available.")
                return None

    def runModule(self, runScript, fileName, run_internal, run_with_args, args):
        pythonPath = self.pythonPath()
        if pythonPath is None:
            return
        env = QProcessEnvironment.systemEnvironment()
        self.runProcess.setProcessEnvironment(env)

        if run_internal:
            self.currentProcess = fileName
            if run_with_args:
                self.printout(">>> Running: {0} <arguments={1}>\n".format(
                    self.currentProcess, args), 4)
                self.runProcess.start(pythonPath, [
                                      runScript, args], self.openMode)
            else:
                self.printout(">>> Running: {0} <arguments=None>\n".format(
                    self.currentProcess), 4)
                self.runProcess.start(pythonPath, [runScript], self.openMode)
            self.runProcess.waitForStarted()
        else:
            if run_with_args:
                self.runProcess.startDetached(
                    pythonPath, ["-i", runScript, args])
            else:
                self.runProcess.startDetached(pythonPath, ["-i", runScript])
            # -i ensures that the shell program remains even after the source program
            # has finished or has been terminated in order for debugging to be
            # done

    def runDebug(self, runScript, fileName, run_internal, run_with_args, args):
        pythonPath = self.pythonPath()
        if pythonPath is None:
            return
        try:
            import debugpy  # noqa: F401
        except ImportError:
            QMessageBox.warning(
                self, "Debug",
                "debugpy is not installed.\nInstall with: pip install debugpy")
            return

        env = QProcessEnvironment.systemEnvironment()
        self.runProcess.setProcessEnvironment(env)
        debug_args = ["-m", "debugpy", "--listen", "5678"]
        if to_bool(self.projectData.get("DebugWait")):
            debug_args.append("--wait-for-client")
        debug_args.append(runScript)
        if run_with_args and args:
            debug_args.append(args)

        if run_internal:
            self.currentProcess = fileName
            wait_note = ""
            if to_bool(self.projectData.get("DebugWait")):
                wait_note = " — waiting for debugger on port 5678"
            self.printout(
                ">>> Debug (debugpy listen 5678{0}): {1}\n".format(
                    wait_note, fileName), 4)
            status = "Debug: listening on :5678"
            if to_bool(self.projectData.get("DebugWait")):
                status += " (waiting for attach)"
            self.debugStatusChanged.emit(status)
            self.runProcess.start(pythonPath, debug_args, self.openMode)
            self.runProcess.waitForStarted()
        else:
            self.runProcess.startDetached(pythonPath, ["-i"] + debug_args)

    def runTrace(self, runScript, fileName, run_internal, run_with_args, args, option):
        pythonPath = self.pythonPath()
        if pythonPath is None:
            return

        env = QProcessEnvironment.systemEnvironment()
        self.runProcess.setProcessEnvironment(env)

        if run_internal:
            self.currentProcess = fileName
            if run_with_args:
                self.printout(">>> Trace Execution: {0} <arguments={1}>\n".format(
                    self.currentProcess, args), 4)
            else:
                self.printout(">>> Trace Execution: {0} <arguments=None>\n".format(
                    self.currentProcess), 4)
            if option == 0:
                # calling relationships
                if run_with_args:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--trackcalls', runScript, args], self.openMode)
                else:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--trackcalls', runScript], self.openMode)
            elif option == 1:
                # functions called
                if run_with_args:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--listfuncs', runScript, args], self.openMode)
                else:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--listfuncs', runScript], self.openMode)
            elif option == 2:
                # creates a file with same code but showing how many times
                # each line of code args
                countfile = os.path.abspath(os.path.join("temp", "count.txt"))
                with open(countfile, 'w'):
                    pass
                if run_with_args:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--count', '--file={0}'.format(countfile), runScript, args], self.openMode)
                else:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--count', '--file={0}'.format(countfile), runScript], self.openMode)
            elif option == 3:
                # show in real time what lines of code are currently being
                # executed
                if run_with_args:
                    self.runProcess.start(
                        pythonPath, ['-m', "trace", '--timing',
                                     '--trace', runScript, args], self.openMode)
                else:
                    self.runProcess.start(
                        pythonPath, ['-m', "trace", '--timing',
                                     '--trace', runScript], self.openMode)
        else:
            if option == 0:
                # calling relationships
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--trackcalls', runScript, args], self.openMode)
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--trackcalls', runScript])
            elif option == 1:
                # functions called
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--listfuncs', runScript, args])
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--listfuncs', runScript])
            elif option == 2:
                # creates a file with same code but showing how many times each
                # line of code runs
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--count', runScript, args])
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--count', runScript])
            elif option == 3:
                # show in real time what lines of code are currently being
                # executed
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--timing', '--trace', runScript, args])
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--timing', '--trace', runScript])

    def runProfiler(self, runScript, fileName, run_internal, run_with_args, args):
        pythonPath = self.pythonPath()
        if pythonPath is None:
            return
        env = QProcessEnvironment.systemEnvironment()
        self.runProcess.setProcessEnvironment(env)

        p_args = ['-m', 'cProfile', '-o',
                  os.path.abspath(os.path.join("temp", "profile"))]
        if os.name == 'nt':
            # On Windows, one has to replace backslashes by slashes to avoid
            # confusion with escape characters (otherwise, for example, '\t'
            # will be interpreted as a tabulation):
            p_args.append(os.path.normpath(runScript).replace(os.sep, '/'))
        else:
            p_args.append(runScript)

        self.profileMode = True
        if run_internal:
            self.currentProcess = fileName
            if run_with_args:
                self.printout(">>> Profiling: {0} <arguments={1}>\n".format(
                    self.currentProcess, args), 4)
            else:
                self.printout(">>> Profiling: {0} <arguments=None>\n".format(
                    self.currentProcess), 4)
            self.runProcess.start(pythonPath, p_args)
            self.runProcess.waitForStarted()
        else:
            p_args.insert(0, "-i")
            self.runProcess.startDetached(pythonPath, p_args)
            # -i ensures that the shell program remains even after the source program
            # has finished or has been terminated in order for debugging to be
            # done

    def reRunFile(self):
        self.run(False, True)

    def runFile(self):
        saved = self.editorTabWidget.save()
        if saved:
            self.run(False)

    def runProject(self):
        if self.editorTabWidget.errorsInProject():
            reply = QMessageBox.warning(
                self, "Run Project",
                "There are errors in your project. Run anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                pass
            else:
                return
        saved = self.editorTabWidget.saveProject()
        if saved:
            pass
        else:
            return
        self.run(True)

    def run(self, project, rerun=False):
        if project:
            filePath = self.editorTabWidget.projectPathDict["mainscript"]
            fileName = self.editorTabWidget.projectPathDict["name"]
            if os.path.exists(filePath) is not True:
                QMessageBox.warning(self, "Run Project",
                                                    "Main script is missing: " + fileName)
                return
        else:
            if self.editorTabWidget.getSource().strip() == '':
                QMessageBox.warning(self, "Run",
                                                    "Source code must be present!")
                return
            if rerun is False:
                self.filePath = self.editorTabWidget.getEditorData("filePath")
                filePath = self.filePath
                self.fileName = self.editorTabWidget.getTabName()
                fileName = self.fileName
                self.runFileAct.setEnabled(True)
            else:
                filePath = self.filePath
                fileName = self.fileName
        cwd = os.path.dirname(filePath)
        self.runProcess.setWorkingDirectory(cwd)

        if to_bool(self.projectData["RunInternal"]):
            run_internal = True
        else:
            run_internal = False
        run_with_args = to_bool(self.projectData["RunWithArguments"])
        args = self.projectData["RunArguments"]
        bufferSize = int(self.projectData["BufferSize"])

        clearOutput = self.projectData["ClearOutputWindowOnRun"]

        if to_bool(clearOutput):
            self.clear()
        elif self.lines() >= bufferSize:
            self.clear()
        runType = self.projectData["RunType"]
        if runType == "Run":
            self.runModule(filePath, fileName, run_internal, run_with_args,
                           args)
        elif runType == "Profiler":
            self.runProfiler(filePath, fileName, run_internal, run_with_args,
                             args)
        elif runType == "Trace":
            option = int(self.projectData["TraceType"])
            self.runTrace(filePath, fileName, run_internal, run_with_args,
                          args, option)
        elif runType == "Debug":
            self.runDebug(filePath, fileName, run_internal, run_with_args,
                          args)

    def stopProcess(self):
        self.runProcess.kill()
        self.currentProcess = None
        self.debugStatusChanged.emit("")

    def contextMenuEvent(self, event):
        if self.isReadOnly():
            self.contextMenu.exec(event.globalPos())
        else:
            event.ignore()

    def getHoveredLine(self, x, y):
        position = self.SendScintilla(
            QsciScintilla.SCI_POSITIONFROMPOINT, x, y)
        line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, position)

        return line

    def mouseDoubleClickEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())

        line = self.getHoveredLine(x, y)
        lineText = self.text(line)

        if self.tracebackRe.match(lineText):
            lineText.find('File')
            min_index = lineText.find('"') + 1
            max_index = lineText.find('"', min_index)
            path = lineText[min_index:max_index]

            max_index += 7
            line_end_index = lineText.find(',', max_index)
            lineno = int(lineText[max_index:line_end_index]) - 1

            self.editorTabWidget.loadfile(path)
            self.editorTabWidget.showLine(lineno)

        event.ignore()

    def mousePressEvent(self, event):
        if self.isReadOnly():
            super(RunWidget, self).mousePressEvent(event)
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """
        Reimplemented to create a console-like interface.
        """
        line, index = self.getCursorPosition()
        key = event.key()
        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        alt = event.modifiers() & Qt.KeyboardModifier.AltModifier
        event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        if ctrl:
            pass
        elif alt:
            pass
        elif key == Qt.Key.Key_Backspace:
            if self.getCursorPosition() == self.blocking_cursor_pos:
                pass
            else:
                QsciScintilla.keyPressEvent(self, event)
        elif key == Qt.Key.Key_Left:
            if self.getCursorPosition() == self.blocking_cursor_pos:
                pass
            else:
                QsciScintilla.keyPressEvent(self, event)
        elif key == Qt.Key.Key_Up:
            self.scrollVertical(-1)
        elif key == Qt.Key.Key_Down:
            self.scrollVertical(1)
        elif key == Qt.Key.Key_Return:
            # get input text
            text = self.getText(
                self.blocking_cursor_pos, self.position("eof"))
            self.insertInput(text)
        else:
            QsciScintilla.keyPressEvent(self, event)
