import os
import shutil

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QRadioButton,
    QSpinBox, QVBoxLayout, QWidget,
)

from Extensions import StyleSheet
from Extensions.file_dialog_utils import file_dialog_path


def _section(title):
    """Plain (non-checkable) group box with consistent flat styling."""
    box = QGroupBox(title)
    box.setFlat(True)
    layout = QVBoxLayout()
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(6)
    box.setLayout(layout)
    return box, layout


class GeneralSettings(QWidget):
    """General preferences page (embedded in the Settings tab widget)."""

    def __init__(self, useData, mainApp, projectWindowStack, host=None, parent=None):
        QWidget.__init__(self, parent)

        self.useData = useData
        self.mainApp = mainApp
        self.projectWindowStack = projectWindowStack
        self.host = host
        self._filter_sections = []  # (group_widget, searchable_text)

        root = QVBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)
        self.setLayout(root)

        # --- Filter ---------------------------------------------------------
        filter_row = QHBoxLayout()
        filter_label = QLabel("Filter:")
        filter_label.setAccessibleName("Settings filter label")
        filter_row.addWidget(filter_label)
        self.filterLine = QLineEdit()
        self.filterLine.setPlaceholderText("Filter settings\u2026")
        self.filterLine.setClearButtonEnabled(True)
        self.filterLine.setAccessibleName("Filter settings")
        self.filterLine.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self.filterLine, 1)
        root.addLayout(filter_row)

        columns = QHBoxLayout()
        columns.setSpacing(16)
        root.addLayout(columns, 1)

        left = QVBoxLayout()
        left.setSpacing(10)
        right = QVBoxLayout()
        right.setSpacing(10)
        columns.addLayout(left, 1)
        columns.addLayout(right, 1)

        # ===================== LEFT: Editor / Search / Completion ==========
        self._build_editor_section(left)
        self._build_search_section(left)
        self._build_completion_section(left)
        left.addStretch(1)

        # ===================== RIGHT: Appearance first =====================
        self._build_appearance_section(right)
        self._build_assistant_section(right)
        self._build_edge_section(right)
        self._build_wrap_section(right)
        right.addStretch(1)

        # Demoted secondary action
        export_row = QHBoxLayout()
        export_row.addStretch(1)
        self.exportButton = QPushButton("Export settings\u2026")
        self.exportButton.setFlat(True)
        self.exportButton.setAccessibleName("Export settings")
        self.exportButton.setToolTip("Export workspace settings as a zip archive")
        self.exportButton.clicked.connect(self.exportSettings)
        export_row.addWidget(self.exportButton)
        root.addLayout(export_row)

        # Apply initial enable/disable for parent toggles
        self._sync_completion_enabled(self.enableAutoCompletionBox.isChecked())
        self._sync_assistant_enabled(self.enableAssistanceBox.isChecked())
        self._sync_edge_enabled(self.showEdgeLineBox.isChecked())
        self._sync_wrap_enabled(self.enableWrapBox.isChecked())

    def _register_section(self, widget, *texts):
        blob = " ".join(t.lower() for t in texts if t)
        self._filter_sections.append((widget, blob))

    def _apply_filter(self, text):
        query = (text or "").strip().lower()
        for widget, blob in self._filter_sections:
            widget.setVisible(not query or query in blob)

    # --- sections -----------------------------------------------------------

    def _build_editor_section(self, parent_layout):
        gbox, layout = _section("Editor")
        parent_layout.addWidget(gbox)

        display = QLabel("Display")
        display.setStyleSheet("font-weight: 600; color: gray;")
        layout.addWidget(display)

        self.showLineNumbersBox = QCheckBox("Line numbers")
        self.showLineNumbersBox.setChecked(
            self.useData.setting_bool("ShowLineNumbers"))
        self.showLineNumbersBox.toggled.connect(self.setShowLineNumbers)
        layout.addWidget(self.showLineNumbersBox)

        self.showWhiteSpacesBox = QCheckBox("White spaces")
        self.showWhiteSpacesBox.setChecked(
            self.useData.setting_bool("ShowWhiteSpaces"))
        self.showWhiteSpacesBox.toggled.connect(self.setShowWhiteSpaces)
        layout.addWidget(self.showWhiteSpacesBox)

        self.activeLineBox = QCheckBox("Highlight active line")
        self.activeLineBox.setChecked(
            self.useData.setting_bool("ShowCaretLine"))
        self.activeLineBox.toggled.connect(self.setShowCaretLine)
        layout.addWidget(self.activeLineBox)

        self.markOperationalLinesBox = QCheckBox("Mark operator lines")
        self.markOperationalLinesBox.setToolTip(
            "Highlight lines that contain operators")
        self.markOperationalLinesBox.setChecked(
            self.useData.setting_bool("MarkOperationalLines"))
        self.markOperationalLinesBox.toggled.connect(
            self.setMarkOperationalLines)
        layout.addWidget(self.markOperationalLinesBox)

        behavior = QLabel("Behavior")
        behavior.setStyleSheet("font-weight: 600; color: gray; padding-top: 4px;")
        layout.addWidget(behavior)

        self.matchBracesBox = QCheckBox("Match braces")
        self.matchBracesBox.setChecked(
            self.useData.setting_bool("MatchBraces"))
        self.matchBracesBox.toggled.connect(self.setMatchBraces)
        layout.addWidget(self.matchBracesBox)

        self.foldingBox = QCheckBox("Code folding")
        self.foldingBox.setChecked(
            self.useData.setting_bool("EnableFolding"))
        self.foldingBox.toggled.connect(self.setFolding)
        layout.addWidget(self.foldingBox)

        self.showCalltipsBox = QCheckBox("Calltips")
        self.showCalltipsBox.setChecked(
            self.useData.setting_bool("CallTips"))
        self.showCalltipsBox.toggled.connect(self.setShowCalltip)
        layout.addWidget(self.showCalltipsBox)

        self.docOnHoverBox = QCheckBox("Documentation on hover")
        self.docOnHoverBox.setChecked(
            self.useData.setting_bool("DocOnHover"))
        self.docOnHoverBox.toggled.connect(self.setDocOnHover)
        layout.addWidget(self.docOnHoverBox)

        self._register_section(
            gbox, "editor", "line numbers", "white spaces", "active line",
            "operator", "braces", "folding", "calltips", "documentation",
            "hover", "display", "behavior")

    def _build_search_section(self, parent_layout):
        gbox, layout = _section("Search")
        parent_layout.addWidget(gbox)

        self.dynamicSearchBox = QCheckBox("Dynamic search")
        self.dynamicSearchBox.setChecked(
            self.useData.setting_bool("DynamicSearch"))
        self.dynamicSearchBox.toggled.connect(self.setDynamicSearch)
        layout.addWidget(self.dynamicSearchBox)

        self.markWordOccurrenceBox = QCheckBox("Mark word occurrences")
        self.markWordOccurrenceBox.setChecked(
            self.useData.setting_bool("MarkSearchOccurrence"))
        self.markWordOccurrenceBox.toggled.connect(
            self.setMarkSearchOccurrence)
        layout.addWidget(self.markWordOccurrenceBox)

        self._register_section(
            gbox, "search", "dynamic", "word", "occurrence", "mark")

    def _build_completion_section(self, parent_layout):
        gbox, layout = _section("Auto-Completion")
        parent_layout.addWidget(gbox)

        self.enableAutoCompletionBox = QCheckBox("Enable auto-completion")
        self.enableAutoCompletionBox.setChecked(
            self.useData.setting_bool("EnableAutoCompletion"))
        self.enableAutoCompletionBox.toggled.connect(self.enableAutoCompletion)
        layout.addWidget(self.enableAutoCompletionBox)

        self.autoCompApiBox = QRadioButton("Project (rope)")
        self.autoCompDocBox = QRadioButton("Current module")
        if self.useData.SETTINGS["AutoCompletion"] == "Document":
            self.autoCompDocBox.setChecked(True)
        else:
            self.autoCompApiBox.setChecked(True)
        self.autoCompApiBox.toggled.connect(self.setAutoCompletion)
        self.autoCompDocBox.toggled.connect(self.setAutoCompletion)
        layout.addWidget(self.autoCompApiBox)
        layout.addWidget(self.autoCompDocBox)

        self._register_section(
            gbox, "auto", "completion", "project", "module", "rope")

    def _build_appearance_section(self, parent_layout):
        gbox, layout = _section("Appearance")
        parent_layout.addWidget(gbox)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(6)
        layout.addLayout(form)

        self.themeBox = QComboBox()
        self.themeBox.setAccessibleName("Theme")
        self.themeBox.addItems(["Light", "Dark", "System"])
        currentTheme = self.useData.SETTINGS.get("Theme", "Light")
        themeIndex = self.themeBox.findText(currentTheme)
        if themeIndex != -1:
            self.themeBox.setCurrentIndex(themeIndex)
        self.themeBox.currentIndexChanged.connect(self.setTheme)
        form.addRow("Theme", self.themeBox)

        self.uiBox = QComboBox()
        self.uiBox.setAccessibleName("UI style")
        self.uiBox.addItem("Custom")
        self.uiBox.addItem("Native")
        if self.useData.SETTINGS["UI"] == "Native":
            self.uiBox.setCurrentIndex(1)
        self.uiBox.currentIndexChanged.connect(self.setUI)
        form.addRow("UI style", self.uiBox)

        self.uiScaleBox = QSpinBox()
        self.uiScaleBox.setAccessibleName("UI font scale percent")
        self.uiScaleBox.setRange(75, 150)
        self.uiScaleBox.setSingleStep(5)
        self.uiScaleBox.setSuffix("%")
        try:
            scale = int(self.useData.SETTINGS.get("UIFontScale", "100"))
        except (TypeError, ValueError):
            scale = 100
        self.uiScaleBox.setValue(max(75, min(150, scale)))
        self.uiScaleBox.valueChanged.connect(self.setUIFontScale)
        form.addRow("Font scale", self.uiScaleBox)

        self.enableSoundsBox = QCheckBox("Enable sounds")
        self.enableSoundsBox.setChecked(
            self.useData.setting_bool("SoundsEnabled"))
        self.enableSoundsBox.toggled.connect(self.setSoundsEnabled)
        layout.addWidget(self.enableSoundsBox)

        self._register_section(
            gbox, "appearance", "theme", "ui", "font", "scale", "sounds",
            "light", "dark", "native", "custom")

    def _build_assistant_section(self, parent_layout):
        gbox, layout = _section("Assistant")
        parent_layout.addWidget(gbox)

        self.enableAssistanceBox = QCheckBox("Enable assistant")
        self.enableAssistanceBox.setChecked(
            self.useData.setting_bool("EnableAssistance"))
        self.enableAssistanceBox.toggled.connect(self.enableAssistance)
        layout.addWidget(self.enableAssistanceBox)

        # Independent toggles (both can run; not exclusive).
        self.enableAlertsBox = QCheckBox("Syntax alerts (pyflakes)")
        self.enableAlertsBox.setChecked(
            self.useData.setting_bool("EnableAlerts"))
        self.enableAlertsBox.toggled.connect(self.setAssistant)
        layout.addWidget(self.enableAlertsBox)

        self.enableStyleGuideBox = QCheckBox("Style guide (PEP 8)")
        self.enableStyleGuideBox.setChecked(
            self.useData.setting_bool("enableStyleGuide"))
        self.enableStyleGuideBox.toggled.connect(self.enableStyleGuide)
        layout.addWidget(self.enableStyleGuideBox)

        self._register_section(
            gbox, "assistant", "alerts", "style", "pep8", "pyflakes", "syntax")

    def _build_edge_section(self, parent_layout):
        gbox, layout = _section("Edge Line")
        parent_layout.addWidget(gbox)

        self.showEdgeLineBox = QCheckBox("Show edge line")
        self.showEdgeLineBox.setChecked(
            self.useData.setting_bool("ShowEdgeLine"))
        self.showEdgeLineBox.toggled.connect(self.setShowEdgeLine)
        layout.addWidget(self.showEdgeLineBox)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(6)
        layout.addLayout(form)

        self.positionBox = QSpinBox()
        self.positionBox.setAccessibleName("Edge column")
        self.positionBox.setRange(1, 200)
        self.positionBox.setValue(int(self.useData.SETTINGS["EdgeColumn"]))
        self.positionBox.valueChanged.connect(self.setEdgeColumn)
        form.addRow("Column", self.positionBox)

        self.edgeModeBox = QComboBox()
        self.edgeModeBox.setAccessibleName("Edge mode")
        self.edgeModeBox.addItem("Line")
        self.edgeModeBox.addItem("Background")
        self.edgeModeBox.setCurrentIndex(
            self.edgeModeBox.findText(self.useData.SETTINGS["EdgeMode"]))
        self.edgeModeBox.activated.connect(self.setEdgeMode)
        self.edgeModeBox.currentIndexChanged.connect(self.setEdgeMode)
        form.addRow("Mode", self.edgeModeBox)

        self._register_section(
            gbox, "edge", "line", "column", "mode", "background")

    def _build_wrap_section(self, parent_layout):
        gbox, layout = _section("Line Wrap")
        parent_layout.addWidget(gbox)

        self.enableWrapBox = QCheckBox("Enable line wrap")
        self.enableWrapBox.setChecked(
            self.useData.setting_bool("LineWrap"))
        self.enableWrapBox.toggled.connect(self.setWrapEnabled)
        layout.addWidget(self.enableWrapBox)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(6)
        layout.addLayout(form)

        self.wrapModeBox = QComboBox()
        self.wrapModeBox.setAccessibleName("Line wrap mode")
        self.wrapModeBox.addItem("Word")
        self.wrapModeBox.addItem("Character")
        self.wrapModeBox.addItem("Whitespace")
        self.wrapModeBox.setCurrentIndex(
            self.wrapModeBox.findText(self.useData.SETTINGS["WrapMode"]))
        self.wrapModeBox.activated.connect(self.setWrapMode)
        self.wrapModeBox.currentIndexChanged.connect(self.setWrapMode)
        form.addRow("Wrap mode", self.wrapModeBox)

        self._register_section(
            gbox, "line", "wrap", "word", "character", "whitespace")

    # --- enable/disable children --------------------------------------------

    def _sync_completion_enabled(self, enabled):
        self.autoCompApiBox.setEnabled(enabled)
        self.autoCompDocBox.setEnabled(enabled)

    def _sync_assistant_enabled(self, enabled):
        self.enableAlertsBox.setEnabled(enabled)
        self.enableStyleGuideBox.setEnabled(enabled)

    def _sync_edge_enabled(self, enabled):
        self.positionBox.setEnabled(enabled)
        self.edgeModeBox.setEnabled(enabled)

    def _sync_wrap_enabled(self, enabled):
        self.wrapModeBox.setEnabled(enabled)

    # --- setters (behavior unchanged) ---------------------------------------

    def setUI(self, index):
        mode = self.uiBox.currentText()
        if self.host is not None and hasattr(self.host, "applyUiMode"):
            self.host.applyUiMode(mode)
            return
        self.useData.SETTINGS["UI"] = mode
        if index == 0:
            StyleSheet.apply_theme(
                self.mainApp, self.useData.SETTINGS.get("Theme", "Light"))
        else:
            StyleSheet.apply_native(self.mainApp)
        isCustom = (index == 0)
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            if hasattr(window, "refreshChromeStyles"):
                window.refreshChromeStyles(isCustom)
            if hasattr(window, "editorTabWidget"):
                window.editorTabWidget.adjustToStyleSheet(isCustom)

    def setTheme(self, index):
        theme = self.themeBox.currentText()
        if self.host is not None and hasattr(self.host, "applyTheme"):
            self.host.applyTheme(theme)
            return
        self.useData.SETTINGS["Theme"] = theme
        if self.useData.SETTINGS["UI"] == "Custom":
            StyleSheet.apply_theme(self.mainApp, theme)

    def setUIFontScale(self, value):
        self.useData.SETTINGS["UIFontScale"] = str(int(value))
        StyleSheet.apply_ui_font_scale(self.mainApp, value)

    def exportSettings(self):
        savepath = os.path.join(
            self.useData.getLastOpenedDir(),
            "Pcode_Settings" + '_' + QDateTime().currentDateTime().toString(
            ).replace(' ', '_').replace(':', '-'))
        savepath = os.path.normpath(savepath)
        fileName = file_dialog_path(QFileDialog.getSaveFileName(
            self,
            "Export Settings", savepath,
            "Pcode Settings (*)",
        ))
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
        self._sync_assistant_enabled(state)
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
                for j in range(editorTabWidget.count()):
                    editor = editorTabWidget.getEditor(j)
                    if editor.DATA["fileType"] == "python":
                        editor2 = editorTabWidget.getCloneEditor(j)
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
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(j)
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
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(j)
                    editor.setEdgeColumn(value)
                    editor2.setEdgeColumn(value)

    def setWrapEnabled(self, state):
        self.useData.set_setting_bool("LineWrap", state)
        self._sync_wrap_enabled(state)
        if state:
            self.setWrapMode()
        else:
            for i in range(self.projectWindowStack.count() - 1):
                editorTabWidget = self.projectWindowStack.widget(
                    i).editorTabWidget
                for j in range(editorTabWidget.count()):
                    editor = editorTabWidget.getEditor(j)
                    if editor.DATA["fileType"] == "python":
                        editor2 = editorTabWidget.getCloneEditor(j)
                        editor.setWrapMode(QsciScintilla.WrapNone)
                        editor2.setWrapMode(QsciScintilla.WrapNone)

    def setWrapMode(self):
        self.useData.SETTINGS['WrapMode'] = self.wrapModeBox.currentText()
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(j)
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
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] in self.useData.supportedFileTypes:
                    editor2 = editorTabWidget.getCloneEditor(j)
                    editor.setCaretLineVisible(state)
                    editor2.setCaretLineVisible(state)

    def setShowCalltip(self, state):
        self.useData.set_setting_bool("CallTips", state)

    def setShowLineNumbers(self, state):
        self.useData.set_setting_bool("ShowLineNumbers", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                editor2 = editorTabWidget.getCloneEditor(j)
                editor.showLineNumbers()
                editor2.showLineNumbers()

    def setMatchBraces(self, state):
        self.useData.set_setting_bool("MatchBraces", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                editor2 = editorTabWidget.getCloneEditor(j)
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
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(j)
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
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(j)
                    editor.showWhiteSpaces()
                    editor2.showWhiteSpaces()

    def enableAutoCompletion(self, state):
        self.useData.set_setting_bool("EnableAutoCompletion", state)
        self._sync_completion_enabled(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for j in range(editorTabWidget.count()):
                editorTabWidget.getEditor(j).setAutoCompletion()
                editorTabWidget.getCloneEditor(j).setAutoCompletion()

    def setAutoCompletion(self):
        if self.autoCompDocBox.isChecked():
            self.useData.SETTINGS["AutoCompletion"] = "Document"
        elif self.autoCompApiBox.isChecked():
            self.useData.SETTINGS["AutoCompletion"] = "Api"
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                editor.setAutoCompletion()
                editor2 = editorTabWidget.getCloneEditor(j)
                editor2.setAutoCompletion()

    def setDynamicSearch(self, state):
        self.useData.set_setting_bool("DynamicSearch", state)

    def setMarkSearchOccurrence(self, state):
        self.useData.set_setting_bool("MarkSearchOccurrence", state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                snapshot = editorTabWidget.getSnapshot(j)
                editor.clearMatchIndicators()
                snapshot.clearMatchIndicators()

    def setShowEdgeLine(self, state):
        self.useData.set_setting_bool("ShowEdgeLine", state)
        self._sync_edge_enabled(state)
        for i in range(self.projectWindowStack.count() - 1):
            editorTabWidget = self.projectWindowStack.widget(i).editorTabWidget
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(j)
                    editor.showWhiteSpaces()
                    editor2.showWhiteSpaces()
                    if state:
                        if self.edgeModeBox.currentText() == "Background":
                            editor.setEdgeMode(QsciScintilla.EdgeBackground)
                            editor2.setEdgeMode(QsciScintilla.EdgeBackground)
                        else:
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
            for j in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(j)
                if editor.DATA["fileType"] == "python":
                    editor2 = editorTabWidget.getCloneEditor(j)
                    editor.setMarkOperationalLines()
                    editor2.setMarkOperationalLines()

    def updateStyleBox(self):
        self.themeBox.clear()
        self.themeBox.addItem('Default')
        self.themeBox.insertSeparator(1)
        for i in os.listdir(self.useData.appPathDict["stylesdir"]):
            self.themeBox.addItem(os.path.splitext(i)[0])
