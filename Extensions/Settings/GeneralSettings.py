import os
import shutil
from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla


class GeneralSettings(QtGui.QDialog):

    def __init__(self, useData, projectWindowStack, parent=None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Window |
                               QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("Settings")
        self.useData = useData
        self.projectWindowStack = projectWindowStack

        mainLayout = QtGui.QHBoxLayout()
        self.setLayout(mainLayout)

        # AUTO COMPLETION
        mainVbox = QtGui.QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        self.autoCompGbox = QtGui.QGroupBox("Auto-Completion")
        self.autoCompGbox.setFlat(True)
        self.autoCompGbox.setCheckable(True)
        mainVbox.addWidget(self.autoCompGbox)

        vbox = QtGui.QVBoxLayout()
        self.autoCompGbox.setLayout(vbox)

        self.autoCompButtonGroup = QtGui.QButtonGroup()
        self.autoCompButtonGroup.setExclusive(True)

        self.autoCompApiBox = QtGui.QCheckBox("Project")
        if (self.useData.SETTINGS["AutoCompletion"] == "Api"):
            self.autoCompApiBox.setChecked(True)
        self.autoCompButtonGroup.addButton(self.autoCompApiBox)
        self.autoCompApiBox.toggled.connect(self.setAutoCompletion)
        vbox.addWidget(self.autoCompApiBox)

        self.autoCompDocBox = QtGui.QCheckBox("Current Module")
        if (self.useData.SETTINGS["AutoCompletion"] == "Document"):
            self.autoCompDocBox.setChecked(True)
        self.autoCompButtonGroup.addButton(self.autoCompDocBox)
        self.autoCompDocBox.toggled.connect(self.setAutoCompletion)
        vbox.addWidget(self.autoCompDocBox)

        if self.useData.SETTINGS["EnableAutoCompletion"] == "True":
            self.autoCompGbox.setChecked(True)
        else:
            self.autoCompGbox.setChecked(False)
        self.autoCompGbox.toggled.connect(self.enableAutoCompletion)

        # SEARCH

        gbox = QtGui.QGroupBox("Search")
        gbox.setFlat(True)

        vbox = QtGui.QVBoxLayout()
        gbox.setLayout(vbox)
        mainVbox.addWidget(gbox)

        self.dynamicSearchBox = QtGui.QCheckBox("Dynamic Search")
        if self.useData.SETTINGS["DynamicSearch"] == "True":
            self.dynamicSearchBox.setChecked(True)
        self.dynamicSearchBox.toggled.connect(self.setDynamicSearch)
        vbox.addWidget(self.dynamicSearchBox)

        self.markWordOccurrenceBox = QtGui.QCheckBox("Mark Word Occurrence")
        if self.useData.SETTINGS["MarkSearchOccurrence"] == "True":
            self.markWordOccurrenceBox.setChecked(True)
        self.markWordOccurrenceBox.toggled.connect(
            self.setMarkSearchOccurrence)
        vbox.addWidget(self.markWordOccurrenceBox)

        vbox.addStretch(1)

        # EDITOR VIEW

        mainVbox = QtGui.QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        vbox = QtGui.QVBoxLayout()

        gbox = QtGui.QGroupBox("Editor")
        gbox.setFlat(True)
        gbox.setLayout(vbox)
        mainVbox.addWidget(gbox)

        self.showCalltipsBox = QtGui.QCheckBox("Calltips")
        if self.useData.SETTINGS["CallTips"] == "True":
            self.showCalltipsBox.setChecked(True)
        self.showCalltipsBox.toggled.connect(self.setShowCalltip)
        vbox.addWidget(self.showCalltipsBox)

        self.showWhiteSpacesBox = QtGui.QCheckBox("White Spaces")
        if self.useData.SETTINGS["ShowWhiteSpaces"] == "True":
            self.showWhiteSpacesBox.setChecked(True)
        self.showWhiteSpacesBox.toggled.connect(self.setShowWhiteSpaces)
        vbox.addWidget(self.showWhiteSpacesBox)

        # ACTIVE LINE

        activeLineBox = QtGui.QCheckBox("Active Line")
        if self.useData.SETTINGS["ShowCaretLine"] == 'True':
            activeLineBox.setChecked(True)
        else:
            activeLineBox.setChecked(False)
        activeLineBox.toggled.connect(self.setShowCaretLine)
        vbox.addWidget(activeLineBox)

        # LINE NUMBERS

        self.showLineNumbersBox = QtGui.QCheckBox("Line Numbers")
        if self.useData.SETTINGS["ShowLineNumbers"] == "True":
            self.showLineNumbersBox.setChecked(True)
        self.showLineNumbersBox.toggled.connect(self.setShowLineNumbers)
        vbox.addWidget(self.showLineNumbersBox)

        # BRACE MATCHING

        self.matchBracesBox = QtGui.QCheckBox("Match Braces")
        if self.useData.SETTINGS["MatchBraces"] == "True":
            self.matchBracesBox.setChecked(True)
        self.matchBracesBox.toggled.connect(self.setMatchBraces)
        vbox.addWidget(self.matchBracesBox)

        # FOLDING

        self.foldingBox = QtGui.QCheckBox("Folding")
        if self.useData.SETTINGS["EnableFolding"] == "True":
            self.foldingBox.setChecked(True)
        self.foldingBox.toggled.connect(self.setFolding)
        vbox.addWidget(self.foldingBox)

        # DOC ON HOVER

        self.docOnHoverBox = QtGui.QCheckBox("Doc on hover")
        if self.useData.SETTINGS["DocOnHover"] == "True":
            self.docOnHoverBox.setChecked(True)
        self.docOnHoverBox.toggled.connect(self.setDocOnHover)
        vbox.addWidget(self.docOnHoverBox)

        vbox.addStretch(1)

        # EDGE LINE ATTRIBUTES

        mainVbox = QtGui.QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        gbox = QtGui.QGroupBox("Edge Line")
        gbox.setFlat(True)
        gbox.setCheckable(True)
        mainVbox.addWidget(gbox)

        if self.useData.SETTINGS["ShowEdgeLine"] == "True":
            gbox.setChecked(True)
        else:
            gbox.setChecked(False)
        gbox.toggled.connect(self.setShowEdgeLine)

        vbox = QtGui.QVBoxLayout()
        gbox.setLayout(vbox)

        self.positionBox = QtGui.QSpinBox()
        self.positionBox.setRange(1, 200)
        self.positionBox.setValue(int(self.useData.SETTINGS["EdgeColumn"]))
        self.positionBox.valueChanged.connect(self.setEdgeColumn)
        vbox.addWidget(self.positionBox)

        vbox.addWidget(QtGui.QLabel("Edge Mode"))

        self.edgeModeBox = QtGui.QComboBox()
        self.edgeModeBox.addItem("Line")
        self.edgeModeBox.addItem("Background")
        self.edgeModeBox.setCurrentIndex(
            self.edgeModeBox.findText(self.useData.SETTINGS['EdgeMode']))
        self.edgeModeBox.activated.connect(self.setEdgeMode)
        self.edgeModeBox.currentIndexChanged.connect(self.setEdgeMode)
        vbox.addWidget(self.edgeModeBox)

        mainVbox.addStretch(1)

        # ASSISTANT

        mainVbox = QtGui.QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        gbox = QtGui.QGroupBox("Assistant")
        gbox.setFlat(True)
        gbox.setCheckable(True)
        mainVbox.addWidget(gbox)

        vbox = QtGui.QVBoxLayout()
        gbox.setLayout(vbox)

        self.assistantButtonGroup = QtGui.QButtonGroup()
        self.assistantButtonGroup.setExclusive(True)

        self.enableAlertsBox = QtGui.QCheckBox("Alerts")
        if self.useData.SETTINGS["EnableAlerts"] == "True":
            self.enableAlertsBox.setChecked(True)
        self.assistantButtonGroup.addButton(self.enableAlertsBox)
        self.enableAlertsBox.toggled.connect(self.setAssistant)
        vbox.addWidget(self.enableAlertsBox)

        self.enableStyleGuideBox = QtGui.QCheckBox("Style Guide")
        if self.useData.SETTINGS["enableStyleGuide"] == "True":
            self.enableStyleGuideBox.setChecked(True)
        self.assistantButtonGroup.addButton(self.enableStyleGuideBox)
        self.enableStyleGuideBox.toggled.connect(self.enableStyleGuide)
        vbox.addWidget(self.enableStyleGuideBox)

        if self.useData.SETTINGS["EnableAssistance"] == "True":
            gbox.setChecked(True)
        else:
            gbox.setChecked(False)
        gbox.toggled.connect(self.enableAssistance)

        vbox.addStretch(1)

        # MANAGEMENT
        mainLayout.addStretch(1)

        mainVbox = QtGui.QVBoxLayout()
        mainVbox.addStretch(1)
        mainLayout.addLayout(mainVbox)

        self.enableSoundsBox = QtGui.QCheckBox("Enable Sounds")
        if self.useData.SETTINGS["SoundsEnabled"] == 'True':
            self.enableSoundsBox.setChecked(True)
        self.enableSoundsBox.toggled.connect(self.setSoundsEnabled)
        mainVbox.addWidget(self.enableSoundsBox)

        self.exportButton = QtGui.QPushButton("Export Settings")
        self.exportButton.clicked.connect(self.exportSettings)
        mainVbox.addWidget(self.exportButton)

    def exportSettings(self):
        options = QtGui.QFileDialog.Options()
        savepath = os.path.join(self.useData.getLastOpenedDir(),
                                "Pcode_Settings" + '_' + QtCore.QDateTime().currentDateTime().toString().replace(' ', '_').replace(':', '-'))
        savepath = os.path.normpath(savepath)
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Choose Folder", savepath,
                                                     "Pcode Settings (*)", options)
        if fileName:
            try:
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                self.useData.saveLastOpenedDir(os.path.split(fileName)[0])
                shutil.make_archive(fileName, "zip",
                                    self.useData.appPathDict["settingsdir"])
            except Exception as err:
                QtGui.QApplication.restoreOverrideCursor()
                message = QtGui.QMessageBox.warning(self, "Export", str(err))
            QtGui.QApplication.restoreOverrideCursor()

    def enableAssistance(self, state):
        self.useData.SETTINGS["EnableAssistance"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            alertsWidget = self.projectWindowStack.widget(i).assistantWidget
            if state == True:
                alertsWidget.setAssistance()
            else:
                alertsWidget.setAssistance(0)

    def setAssistant(self, state):
        self.useData.SETTINGS["EnableAlerts"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            alertsWidget = self.projectWindowStack.widget(i).assistantWidget
            alertsWidget.setAssistance(1)
            if state == False:
                editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
                for i in range(editorTabWidget.count()):
                    editor = editorTabWidget.getEditor(i)
                    if editor.DATA["fileType"] == "python":
                        editor2 = editorTabWidget.getCloneEditor(i)

                        editor.clearErrorMarkerAndIndicator()
                        editor2.clearErrorMarkerAndIndicator()

    def enableStyleGuide(self, state):
        self.useData.SETTINGS["enableStyleGuide"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            alertsWidget = self.projectWindowStack.widget(i).assistantWidget
            alertsWidget.setAssistance(2)

    def setEdgeMode(self):
        self.useData.SETTINGS['EdgeMode'] = self.edgeModeBox.currentText()
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    if self.edgeModeBox.currentText() == "Line":
                        editor.setEdgeMode(QsciScintilla.EdgeLine)
                        editor2.setEdgeMode(QsciScintilla.EdgeLine)
                    elif self.edgeModeBox.currentText() == "Background":
                        editor.setEdgeMode(QsciScintilla.EdgeBackground)
                        editor2.setEdgeMode(QsciScintilla.EdgeBackground)

    def setEdgeColumn(self, value):
        self.useData.SETTINGS['EdgeColumn'] = str(value)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.setEdgeColumn(value)
                    editor2.setEdgeColumn(value)

    def setSoundsEnabled(self, state):
        self.useData.SETTINGS["SoundsEnabled"] = str(state)

    def setShowCaretLine(self, state):
        self.useData.SETTINGS["ShowCaretLine"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] in self.useData.supportedFileTypes:
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.setCaretLineVisible(state)
                    editor2.setCaretLineVisible(state)

    def setShowCalltip(self, state):
        self.useData.SETTINGS["CallTips"] = str(state)

    def setShowLineNumbers(self, state):
        self.useData.SETTINGS["ShowLineNumbers"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                editor2 = editorTabWidget.getCloneEditor(i)
                editor.showLineNumbers()
                editor2.showLineNumbers()

    def setMatchBraces(self, state):
        self.useData.SETTINGS["MatchBraces"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                editor2 = editorTabWidget.getCloneEditor(i)
                if state == True:
                    editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)
                    editor2.setBraceMatching(
                        QsciScintilla.SloppyBraceMatch)
                else:
                    editor.setBraceMatching(QsciScintilla.NoBraceMatch)
                    editor2.setBraceMatching(QsciScintilla.NoBraceMatch)

    def setFolding(self, state):
        self.useData.SETTINGS["EnableFolding"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    if state == True:
                        editor.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)
                        editor2.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)
                    else:
                        editor.setFolding(QsciScintilla.NoFoldStyle, 2)
                        editor2.setFolding(QsciScintilla.NoFoldStyle, 2)

    def setShowWhiteSpaces(self, state):
        self.useData.SETTINGS["ShowWhiteSpaces"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.showWhiteSpaces()
                    editor2.showWhiteSpaces()

    def enableAutoCompletion(self, state):
        self.useData.SETTINGS["EnableAutoCompletion"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                fileType = editorTabWidget.getEditorData(
                    "fileType", i)
                if fileType == "python":
                    editorTabWidget.getEditor(i).setAutoCompletion()
                    editorTabWidget.getCloneEditor(i).setAutoCompletion()

    def setAutoCompletion(self):
        if self.autoCompDocBox.isChecked() is True:
            self.useData.SETTINGS["AutoCompletion"] = "Document"
        elif self.autoCompApiBox.isChecked() is True:
            self.useData.SETTINGS["AutoCompletion"] = "Api"
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor.setAutoCompletion()
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor2.setAutoCompletion()

    def setDynamicSearch(self, state):
        self.useData.SETTINGS["DynamicSearch"] = str(state)

    def setMarkSearchOccurrence(self, state):
        self.useData.SETTINGS["MarkSearchOccurrence"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor.clearSearchIndicators()

    def setShowEdgeLine(self, state):
        self.useData.SETTINGS["ShowEdgeLine"] = str(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.showWhiteSpaces()
                    editor2.showWhiteSpaces()
                    if state == True:
                        editor.setEdgeMode(QsciScintilla.EdgeLine)
                        editor2.setEdgeMode(QsciScintilla.EdgeLine)
                    else:
                        editor.setEdgeMode(QsciScintilla.EdgeNone)
                        editor2.setEdgeMode(QsciScintilla.EdgeNone)

    def setDocOnHover(self, state):
        self.useData.SETTINGS["DocOnHover"] = str(state)

    def updateStyleBox(self):
        self.themeBox.clear()
        self.themeBox.addItem('Default')
        self.themeBox.insertSeparator(1)
        for i in os.listdir(self.useData.appPathDict["stylesdir"]):
            self.themeBox.addItem(os.path.splitext(i)[0])
