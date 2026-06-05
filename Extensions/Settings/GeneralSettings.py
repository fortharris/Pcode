import os
import shutil

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QDialog, QFileDialog,
    QGroupBox, QHBoxLayout, QLabel, QPushButton, QSpinBox,
    QVBoxLayout,
)

from Extensions import StyleSheet


class GeneralSettings(QDialog):

    def __init__(self, useData, mainApp, projectWindowStack, parent=None):
        QDialog.__init__(self, parent, Qt.WindowType.Window |
                               Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("Settings")
        self.useData = useData
        self.mainApp = mainApp
        self.projectWindowStack = projectWindowStack

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        # AUTO COMPLETION
        mainVbox = QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        self.autoCompGbox = QGroupBox("Auto-Completion")
        self.autoCompGbox.setFlat(True)
        self.autoCompGbox.setCheckable(True)
        mainVbox.addWidget(self.autoCompGbox)

        vbox = QVBoxLayout()
        self.autoCompGbox.setLayout(vbox)

        self.autoCompButtonGroup = QButtonGroup()
        self.autoCompButtonGroup.setExclusive(True)

        self.autoCompApiBox = QCheckBox("Project")
        if (self.useData.SETTINGS["AutoCompletion"] == "Api"):
            self.autoCompApiBox.setChecked(True)
        self.autoCompButtonGroup.addButton(self.autoCompApiBox)
        self.autoCompApiBox.toggled.connect(self.setAutoCompletion)
        vbox.addWidget(self.autoCompApiBox)

        self.autoCompDocBox = QCheckBox("Current Module")
        if (self.useData.SETTINGS["AutoCompletion"] == "Document"):
            self.autoCompDocBox.setChecked(True)
        self.autoCompButtonGroup.addButton(self.autoCompDocBox)
        self.autoCompDocBox.toggled.connect(self.setAutoCompletion)
        vbox.addWidget(self.autoCompDocBox)

        if self.useData.setting_bool("EnableAutoCompletion"):
            self.autoCompGbox.setChecked(True)
        else:
            self.autoCompGbox.setChecked(False)
        self.autoCompGbox.toggled.connect(self.enableAutoCompletion)

        # SEARCH

        gbox = QGroupBox("Search")
        gbox.setFlat(True)

        vbox = QVBoxLayout()
        gbox.setLayout(vbox)
        mainVbox.addWidget(gbox)

        self.dynamicSearchBox = QCheckBox("Dynamic Search")
        if self.useData.setting_bool("DynamicSearch"):
            self.dynamicSearchBox.setChecked(True)
        self.dynamicSearchBox.toggled.connect(self.setDynamicSearch)
        vbox.addWidget(self.dynamicSearchBox)

        self.markWordOccurrenceBox = QCheckBox("Mark Word Occurrence")
        if self.useData.setting_bool("MarkSearchOccurrence"):
            self.markWordOccurrenceBox.setChecked(True)
        self.markWordOccurrenceBox.toggled.connect(
            self.setMarkSearchOccurrence)
        vbox.addWidget(self.markWordOccurrenceBox)

        vbox.addStretch(1)

        # EDITOR VIEW

        mainVbox = QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        vbox = QVBoxLayout()

        gbox = QGroupBox("Editor")
        gbox.setFlat(True)
        gbox.setLayout(vbox)
        mainVbox.addWidget(gbox)

        self.showCalltipsBox = QCheckBox("Calltips")
        if self.useData.setting_bool("CallTips"):
            self.showCalltipsBox.setChecked(True)
        self.showCalltipsBox.toggled.connect(self.setShowCalltip)
        vbox.addWidget(self.showCalltipsBox)

        self.showWhiteSpacesBox = QCheckBox("White Spaces")
        if self.useData.setting_bool("ShowWhiteSpaces"):
            self.showWhiteSpacesBox.setChecked(True)
        self.showWhiteSpacesBox.toggled.connect(self.setShowWhiteSpaces)
        vbox.addWidget(self.showWhiteSpacesBox)

        # ACTIVE LINE

        activeLineBox = QCheckBox("Active Line")
        if self.useData.setting_bool("ShowCaretLine"):
            activeLineBox.setChecked(True)
        else:
            activeLineBox.setChecked(False)
        activeLineBox.toggled.connect(self.setShowCaretLine)
        vbox.addWidget(activeLineBox)

        # LINE NUMBERS

        self.showLineNumbersBox = QCheckBox("Line Numbers")
        if self.useData.setting_bool("ShowLineNumbers"):
            self.showLineNumbersBox.setChecked(True)
        self.showLineNumbersBox.toggled.connect(self.setShowLineNumbers)
        vbox.addWidget(self.showLineNumbersBox)

        # BRACE MATCHING

        self.matchBracesBox = QCheckBox("Match Braces")
        if self.useData.setting_bool("MatchBraces"):
            self.matchBracesBox.setChecked(True)
        self.matchBracesBox.toggled.connect(self.setMatchBraces)
        vbox.addWidget(self.matchBracesBox)

        # FOLDING

        self.foldingBox = QCheckBox("Folding")
        if self.useData.setting_bool("EnableFolding"):
            self.foldingBox.setChecked(True)
        self.foldingBox.toggled.connect(self.setFolding)
        vbox.addWidget(self.foldingBox)

        # DOC ON HOVER

        self.docOnHoverBox = QCheckBox("Doc on hover")
        if self.useData.setting_bool("DocOnHover"):
            self.docOnHoverBox.setChecked(True)
        self.docOnHoverBox.toggled.connect(self.setDocOnHover)
        vbox.addWidget(self.docOnHoverBox)

        # MARK OPERATIONAL LINES

        self.markOperationalLinesBox = QCheckBox("Mark Operation Lines")
        if self.useData.setting_bool("MarkOperationalLines"):
            self.markOperationalLinesBox.setChecked(True)
        self.markOperationalLinesBox.toggled.connect(
            self.setMarkOperationalLines)
        vbox.addWidget(self.markOperationalLinesBox)

        vbox.addStretch(1)

        # EDGE LINE ATTRIBUTES

        mainVbox = QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        gbox = QGroupBox("Edge Line")
        gbox.setFlat(True)
        gbox.setCheckable(True)
        mainVbox.addWidget(gbox)

        if self.useData.setting_bool("ShowEdgeLine"):
            gbox.setChecked(True)
        else:
            gbox.setChecked(False)
        gbox.toggled.connect(self.setShowEdgeLine)

        vbox = QVBoxLayout()
        gbox.setLayout(vbox)

        self.positionBox = QSpinBox()
        self.positionBox.setRange(1, 200)
        self.positionBox.setValue(int(self.useData.SETTINGS["EdgeColumn"]))
        self.positionBox.valueChanged.connect(self.setEdgeColumn)
        vbox.addWidget(self.positionBox)

        vbox.addWidget(QLabel("Edge Mode"))

        self.edgeModeBox = QComboBox()
        self.edgeModeBox.addItem("Line")
        self.edgeModeBox.addItem("Background")
        self.edgeModeBox.setCurrentIndex(
            self.edgeModeBox.findText(self.useData.SETTINGS['EdgeMode']))
        self.edgeModeBox.activated.connect(self.setEdgeMode)
        self.edgeModeBox.currentIndexChanged.connect(self.setEdgeMode)
        vbox.addWidget(self.edgeModeBox)
        
        # LINE WRAP ATTRIBUTES

        gbox = QGroupBox("Line Wrap")
        gbox.setFlat(True)
        gbox.setCheckable(True)
        mainVbox.addWidget(gbox)

        if self.useData.setting_bool("LineWrap"):
            gbox.setChecked(True)
        else:
            gbox.setChecked(False)
        gbox.toggled.connect(self.setWrapEnabled)

        vbox = QVBoxLayout()
        gbox.setLayout(vbox)

        vbox.addWidget(QLabel("Line Wrap Mode"))

        self.wrapModeBox = QComboBox()
        self.wrapModeBox.addItem("Word")
        self.wrapModeBox.addItem("Character")
        self.wrapModeBox.addItem("Whitespace")
        self.wrapModeBox.setCurrentIndex(
            self.wrapModeBox.findText(self.useData.SETTINGS['WrapMode']))
        self.wrapModeBox.activated.connect(self.setWrapMode)
        self.wrapModeBox.currentIndexChanged.connect(self.setWrapMode)
        vbox.addWidget(self.wrapModeBox)

        mainVbox.addStretch(1)

        # ASSISTANT

        mainVbox = QVBoxLayout()
        mainLayout.addLayout(mainVbox)

        gbox = QGroupBox("Assistant")
        gbox.setFlat(True)
        gbox.setCheckable(True)
        mainVbox.addWidget(gbox)

        vbox = QVBoxLayout()
        gbox.setLayout(vbox)

        self.assistantButtonGroup = QButtonGroup()
        self.assistantButtonGroup.setExclusive(True)

        self.enableAlertsBox = QCheckBox("Alerts")
        if self.useData.setting_bool("EnableAlerts"):
            self.enableAlertsBox.setChecked(True)
        self.assistantButtonGroup.addButton(self.enableAlertsBox)
        self.enableAlertsBox.toggled.connect(self.setAssistant)
        vbox.addWidget(self.enableAlertsBox)

        self.enableStyleGuideBox = QCheckBox("Style Guide")
        if self.useData.setting_bool("enableStyleGuide"):
            self.enableStyleGuideBox.setChecked(True)
        self.assistantButtonGroup.addButton(self.enableStyleGuideBox)
        self.enableStyleGuideBox.toggled.connect(self.enableStyleGuide)
        vbox.addWidget(self.enableStyleGuideBox)

        if self.useData.setting_bool("EnableAssistance"):
            gbox.setChecked(True)
        else:
            gbox.setChecked(False)
        gbox.toggled.connect(self.enableAssistance)

        vbox.addStretch(1)

        # MANAGEMENT

        mainVbox.addWidget(QLabel("UI"))

        self.uiBox = QComboBox()
        self.uiBox.addItem("Custom")
        self.uiBox.addItem("Native")
        if self.useData.SETTINGS["UI"] == 'Native':
            self.uiBox.setCurrentIndex(1)
        self.uiBox.currentIndexChanged.connect(self.setUI)
        mainVbox.addWidget(self.uiBox)

        mainVbox.addWidget(QLabel("Theme"))

        self.themeBox = QComboBox()
        self.themeBox.addItems(["Light", "Dark", "System"])
        currentTheme = self.useData.SETTINGS.get("Theme", "Light")
        themeIndex = self.themeBox.findText(currentTheme)
        if themeIndex != -1:
            self.themeBox.setCurrentIndex(themeIndex)
        self.themeBox.currentIndexChanged.connect(self.setTheme)
        mainVbox.addWidget(self.themeBox)

        self.enableSoundsBox = QCheckBox("Enable Sounds")
        if self.useData.setting_bool("SoundsEnabled"):
            self.enableSoundsBox.setChecked(True)
        self.enableSoundsBox.toggled.connect(self.setSoundsEnabled)
        mainVbox.addWidget(self.enableSoundsBox)

        self.exportButton = QPushButton("Export Settings")
        self.exportButton.clicked.connect(self.exportSettings)
        mainVbox.addWidget(self.exportButton)

    def setUI(self, index):
        self.useData.SETTINGS["UI"] = self.uiBox.currentText()
        if index == 0:
            StyleSheet.apply_theme(
                self.mainApp, self.useData.SETTINGS.get("Theme", "Light"))
        else:
            self.mainApp.setStyleSheet(None)
        isCustom = (index == 0)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            if isCustom:
                editorTabWidget.adjustToStyleSheet(True)
            else:
                editorTabWidget.adjustToStyleSheet(False)

    def setTheme(self, index):
        self.useData.SETTINGS["Theme"] = self.themeBox.currentText()
        # Theme only affects the custom UI; native uses the OS style.
        if self.useData.SETTINGS["UI"] == "Custom":
            StyleSheet.apply_theme(
                self.mainApp, self.useData.SETTINGS["Theme"])

    def exportSettings(self):
        options = QFileDialog.Options()
        savepath = os.path.join(self.useData.getLastOpenedDir(),
                                "Pcode_Settings" + '_' + QDateTime().currentDateTime().toString().replace(' ', '_').replace(':', '-'))
        savepath = os.path.normpath(savepath)
        fileName = QFileDialog.getSaveFileName(self,
                                                     "Choose Folder", savepath,
                                                     "Pcode Settings (*)", options)
        if fileName:
            try:
                QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
                self.useData.saveLastOpenedDir(os.path.split(fileName)[0])
                shutil.make_archive(fileName, "zip",
                                    self.useData.appPathDict["settingsdir"])
            except Exception as err:
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(self, "Export", str(err))
            QApplication.restoreOverrideCursor()

    def enableAssistance(self, state):
        self.useData.set_setting_bool("EnableAssistance", state)
        for i in range(self.projectWindowStack.count() - 1):
            alertsWidget = self.projectWindowStack.widget(i).assistantWidget
            if state:
                alertsWidget.setAssistance()
            else:
                alertsWidget.setAssistance(0)

    def setAssistant(self, state):
        self.useData.set_setting_bool("EnableAlerts", state)
        for i in range(self.projectWindowStack.count() - 1):
            alertsWidget = self.projectWindowStack.widget(i).assistantWidget
            alertsWidget.setAssistance(1)
            if state is False:
                editorTabWidget = self.projectWindowStack.widget(
                    i).editorTabWidget
                for i in range(editorTabWidget.count()):
                    editor = editorTabWidget.getEditor(i)
                    if editor.DATA["fileType"] == "python":
                        editor2 = editorTabWidget.getCloneEditor(i)

                        editor.clearErrorMarkerAndIndicator()
                        editor2.clearErrorMarkerAndIndicator()

    def enableStyleGuide(self, state):
        self.useData.set_setting_bool("enableStyleGuide", state)
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
                    
    def setWrapEnabled(self, state):
        self.useData.set_setting_bool("LineWrap", state)
        if state:
            self.setWrapMode()
        else:
            for i in range(self.projectWindowStack.count() - 1):
                editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
                for i in range(editorTabWidget.count()):
                    editor = editorTabWidget.getEditor(i)
                    if editor.DATA["fileType"] == "python":
                        editor2 = editorTabWidget.getCloneEditor(i)
                        
                        editor.setWrapMode(QsciScintilla.WrapNone)
                        editor2.setWrapMode(QsciScintilla.WrapNone)
                            
    def setWrapMode(self):
        self.useData.SETTINGS['WrapMode'] = self.wrapModeBox.currentText()
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    if self.wrapModeBox.currentText() == "Word":
                        editor.setWrapMode(QsciScintilla.WrapWord)
                        editor2.setWrapMode(QsciScintilla.WrapWord)
                    elif self.wrapModeBox.currentText() == "Character":
                        editor.setWrapMode(QsciScintilla.WrapCharacter)
                        editor2.setWrapMode(QsciScintilla.WrapCharacter)
                    elif self.wrapModeBox.currentText() == "Whitespace":
                        editor.setWrapMode(QsciScintilla.WrapWhitespace)
                        editor2.setWrapMode(QsciScintilla.WrapWhitespace)

    def setSoundsEnabled(self, state):
        self.useData.set_setting_bool("SoundsEnabled", state)

    def setShowCaretLine(self, state):
        self.useData.set_setting_bool("ShowCaretLine", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] in self.useData.supportedFileTypes:
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.setCaretLineVisible(state)
                    editor2.setCaretLineVisible(state)

    def setShowCalltip(self, state):
        self.useData.set_setting_bool("CallTips", state)

    def setShowLineNumbers(self, state):
        self.useData.set_setting_bool("ShowLineNumbers", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                editor2 = editorTabWidget.getCloneEditor(i)
                editor.showLineNumbers()
                editor2.showLineNumbers()

    def setMatchBraces(self, state):
        self.useData.set_setting_bool("MatchBraces", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                editor2 = editorTabWidget.getCloneEditor(i)
                if state:
                    editor.setBraceMatching(QsciScintilla.StrictBraceMatch)
                    editor2.setBraceMatching(
                        QsciScintilla.StrictBraceMatch)
                else:
                    editor.setBraceMatching(QsciScintilla.NoBraceMatch)
                    editor2.setBraceMatching(QsciScintilla.NoBraceMatch)

    def setFolding(self, state):
        self.useData.set_setting_bool("EnableFolding", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    if state:
                        editor.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)
                        editor2.setFolding(QsciScintilla.BoxedTreeFoldStyle, 2)
                    else:
                        editor.setFolding(QsciScintilla.NoFoldStyle, 2)
                        editor2.setFolding(QsciScintilla.NoFoldStyle, 2)

    def setShowWhiteSpaces(self, state):
        self.useData.set_setting_bool("ShowWhiteSpaces", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.showWhiteSpaces()
                    editor2.showWhiteSpaces()

    def enableAutoCompletion(self, state):
        self.useData.set_setting_bool("EnableAutoCompletion", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editorTabWidget.getEditor(i).setAutoCompletion()
                editorTabWidget.getCloneEditor(i).setAutoCompletion()

    def setAutoCompletion(self):
        if self.autoCompDocBox.isChecked():
            self.useData.SETTINGS["AutoCompletion"] = "Document"
        elif self.autoCompApiBox.isChecked():
            self.useData.SETTINGS["AutoCompletion"] = "Api"
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                editor.setAutoCompletion()
                editor2 = editorTabWidget.getCloneEditor(i)
                editor2.setAutoCompletion()

    def setDynamicSearch(self, state):
        self.useData.set_setting_bool("DynamicSearch", state)

    def setMarkSearchOccurrence(self, state):
        self.useData.set_setting_bool("MarkSearchOccurrence", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                snapshot = editorTabWidget.getSnapshot(i)

                editor.clearMatchIndicators()
                snapshot.clearMatchIndicators()

    def setShowEdgeLine(self, state):
        self.useData.set_setting_bool("ShowEdgeLine", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.showWhiteSpaces()
                    editor2.showWhiteSpaces()
                    if state:
                        editor.setEdgeMode(QsciScintilla.EdgeLine)
                        editor2.setEdgeMode(QsciScintilla.EdgeLine)
                    else:
                        editor.setEdgeMode(QsciScintilla.EdgeNone)
                        editor2.setEdgeMode(QsciScintilla.EdgeNone)

    def setDocOnHover(self, state):
        self.useData.set_setting_bool("DocOnHover", state)

    def setMarkOperationalLines(self, state):
        self.useData.set_setting_bool("MarkOperationalLines", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(i)
                    editor.setMarkOperationalLines()
                    editor2.setMarkOperationalLines()

    def updateStyleBox(self):
        self.themeBox.clear()
        self.themeBox.addItem('Default')
        self.themeBox.insertSeparator(1)
        for i in os.listdir(self.useData.appPathDict["stylesdir"]):
            self.themeBox.addItem(os.path.splitext(i)[0])
