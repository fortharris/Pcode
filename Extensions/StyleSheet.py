"""Theme-aware stylesheets for Pcode.

Historically this module exposed a single hard-coded light ``globalStyle`` (and
a handful of companion style strings) full of duplicated hex colours and
blurry PNG-backed sub-control arrows. It is now token-based: every style is a
``string.Template`` filled from a palette, and we ship Light + Dark palettes.

Backwards compatibility: the module-level names used elsewhere
(``globalStyle``, ``editorStyle``, ``projectTitleBoxStyle``,
``bottomSwitcherStyle``, ``mainMenuStyle``, ``toolWidgetStyle``,
``viewSwitcherStyle``) still exist. They reflect the currently applied theme
and are refreshed by :func:`apply_theme`, so widgets constructed after a theme
change pick up the new palette.
"""

from string import Template

# --- Palettes ---------------------------------------------------------------

LIGHT = {
    "accent": "#007ACC",
    "accentText": "#FFFFFF",
    "accentHover": "#70A7DC",
    "bg": "#F0F0F0",
    "panel": "#E6E6E6",
    "panelAlt": "#FAFAFA",
    "text": "#000000",
    "textDim": "#6E6E6E",
    "border": "#C8C8C8",
    "hover": "#CCCCCC",
    "selInactiveBg": "#D0D0D0",
    "selInactiveText": "#000000",
    "scrollBg": "#F1F1F1",
    "scrollHandle": "#B2B8BE",
    "scrollHandleHover": "#6F767D",
    "scrollHandlePressed": "#141414",
    "tooltipBg": "#333333",
    "tooltipText": "#FFFFFF",
    "button": "#E4E4E4",
    "buttonHover": "#EFEFEF",
    "buttonPressed": "#CFCFCF",
    "buttonText": "#000000",
    "inputBg": "#FFFFFF",
    "menuBg": "#E6E6E6",
    "menuItemSel": "#007ACC",
    "menuItemSelText": "#FFFFFF",
    "dockTitleBg": "#D8D8D8",
    "dockTitleText": "#000000",
    # Editor / lexer tokens (used when scheme is "Default")
    "editorPaper": "#FFFFFF",
    "editorText": "#000000",
    "editorComment": "#008000",
    "editorKeyword": "#0000FF",
    "editorString": "#A31515",
}

DARK = {
    "accent": "#0E7AD1",
    "accentText": "#FFFFFF",
    "accentHover": "#1F6FB2",
    "bg": "#2D2D30",
    "panel": "#252526",
    "panelAlt": "#333337",
    "text": "#E8E8E8",
    "textDim": "#9A9A9A",
    "border": "#3F3F46",
    "hover": "#3E3E42",
    "selInactiveBg": "#3A3D41",
    "selInactiveText": "#E8E8E8",
    "scrollBg": "#2D2D30",
    "scrollHandle": "#555559",
    "scrollHandleHover": "#6E6E73",
    "scrollHandlePressed": "#9A9A9F",
    "tooltipBg": "#1E1E1E",
    "tooltipText": "#E8E8E8",
    "button": "#3C3C40",
    "buttonHover": "#46464B",
    "buttonPressed": "#2A2A2D",
    "buttonText": "#E8E8E8",
    "inputBg": "#1E1E1E",
    "menuBg": "#252526",
    "menuItemSel": "#0E7AD1",
    "menuItemSelText": "#FFFFFF",
    "dockTitleBg": "#333337",
    "dockTitleText": "#E8E8E8",
    # Editor / lexer tokens (used when scheme is "Default")
    "editorPaper": "#1E1E1E",
    "editorText": "#D4D4D4",
    "editorComment": "#6A9955",
    "editorKeyword": "#569CD6",
    "editorString": "#CE9178",
}

# Last palette applied by apply_theme (for lexer Default overlays).
CURRENT_PALETTE = dict(LIGHT)
CURRENT_THEME = "Light"

PALETTES = {"Light": LIGHT, "Dark": DARK}


def resolve_palette(name):
    """Resolve a theme name (incl. ``System``) to a palette dict."""
    if name == "System":
        name = _detect_system_theme()
    return PALETTES.get(name, LIGHT)


def _detect_system_theme():
    """Best-effort OS dark-mode detection; falls back to Light."""
    try:
        from PyQt6.QtGui import QPalette
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            win = app.palette().color(QPalette.ColorRole.Window)
            # Perceived luminance; < 0.5 means a dark window background.
            lum = (0.299 * win.red() + 0.587 * win.green()
                   + 0.114 * win.blue()) / 255.0
            return "Dark" if lum < 0.5 else "Light"
    except Exception:
        pass
    return "Light"


# --- Templates --------------------------------------------------------------

_GLOBAL_TEMPLATE = Template("""
        QsciScintilla#editor {
            border: none;
            border-top: 2px solid $accent;
        }

        QWidget { color: $text; }

        QToolButton {
            background: transparent;
            border-radius: 2px;
            padding: 1px;
            border: none;
        }
        QToolButton:hover { background: $hover; }
        QToolButton:pressed { background: $accent; }
        QToolButton:checked { background: $accent; }
        QToolButton:disabled { background: transparent; }
        QToolButton::menu-button { color: $text; }

        QGroupBox {
            background-color: none;
            border: none;
            font: bold;
            border-radius: 0px;
            margin-top: 5ex;
        }
        QGroupBox::title {
            padding-left: 8px;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            background-color: none;
        }

        QComboBox {
            color: $text;
            border: none;
            border-bottom: 1px solid $accent;
            border-radius: 0px;
            padding: 2px 2px 2px 3px;
            background: $inputBg;
        }
        QComboBox:disabled { color: $textDim; }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 16px;
            border: none;
        }
        QComboBox QAbstractItemView {
            border: 1px solid $border;
            background: $panel;
            color: $text;
            selection-background-color: $accent;
            selection-color: $accentText;
        }
        QComboBox QAbstractItemView::item { min-height: 24px; }

        QTabWidget::pane { border-top: none; }
        QTabWidget#settingsTab::pane {
            border-top: 1px solid $accent;
            position: absolute;
        }
        QTabWidget::pane#buildTab { border-top: 2px solid $accent; }
        QTabWidget::pane#sideBottomTab { border-top: 2px solid $accent; }
        QTabWidget::tab-bar { left: 0px; }
        QTabWidget#sideBottomTab::tab-bar { left: 0px; }
        QTabWidget#settingsTab::tab-bar { left: 10px; }

        QTabBar { qproperty-drawBase: 0; }
        QTabBar::tab {
            background: none;
            color: $textDim;
            border: none;
            min-width: 24ex;
            min-height: 5ex;
            padding: 2px 5px;
        }
        QTabBar::tab:hover { background: $accentHover; color: $text; }
        QTabBar::tab:selected { background: $accent; color: $accentText; }
        QTabBar::tab:!selected { margin-top: 0px; }

        QToolBar { border: none; background-color: transparent; }
        QToolBar QToolButton {
            border: 1px solid transparent;
            background: transparent;
            padding: 1px;
        }
        QToolBar QToolButton:hover:enabled { background-color: $hover; }
        QToolBar QToolButton:pressed:enabled { background-color: $accent; }
        QToolBar QToolButton:disabled { background-color: transparent; }
        QToolBar QToolButton:checked { background-color: $accent; }

        QStatusBar { background: transparent; }
        QStatusBar::item { border-radius: 3px; }

        QDockWidget { color: $dockTitleText; }
        QDockWidget::title {
            border: none;
            text-align: left;
            background-color: $dockTitleBg;
            padding-left: 5px;
        }
        QDockWidget::close-button, QDockWidget::float-button {
            border: none;
            background: transparent;
            padding: 2px;
        }

        QToolTip {
            color: $tooltipText;
            border: none;
            border-radius: 3px;
            background: $tooltipBg;
            padding: 3px;
        }

        QMenuBar { background-color: $bg; border-bottom: 1px solid $border; }
        QMenuBar::item {
            spacing: 3px;
            padding: 3px 8px;
            background: none;
            color: $text;
            border-radius: 0px;
        }
        QMenuBar::item:selected { background: $accent; color: $accentText; }
        QMenuBar::item:pressed { background: $accent; color: $accentText; }

        QMenu { background: $menuBg; color: $text; padding: 2px;
                border: 1px solid $border; }
        QMenu::item { padding: 5px 30px; border: none; }
        QMenu::item:selected:enabled {
            background: $menuItemSel; color: $menuItemSelText;
        }
        QMenu::separator { height: 1px; background-color: $border; }
        QMenu::indicator { width: 13px; height: 13px; }

        QListView { show-decoration-selected: 1; background: $panel;
                    color: $text; }
        QListView::item:selected:!active {
            color: $selInactiveText;
            background: $selInactiveBg;
        }
        QListView::item:selected:active {
            color: $accentText;
            background: $accent;
        }

        QHeaderView::section {
            background: $panel;
            color: $text;
            padding-left: 4px;
            border: none;
            border-bottom: 1px solid $border;
            height: 20px;
        }

        QTreeView {
            show-decoration-selected: 1;
            background: $panel;
            color: $text;
            border: none;
        }
        QTreeView#sidebarItem {
            border: none;
            show-decoration-selected: 1;
            background: $panel;
        }
        QTreeView::item:selected:!active {
            color: $selInactiveText;
            background: $selInactiveBg;
        }
        QTreeView::item:selected:active {
            color: $accentText;
            background: $accent;
        }
        QTreeView::item:hover { border: none; background: $hover; }

        QSlider::groove:horizontal {
            border: 1px solid $border;
            height: 6px;
            background: $panelAlt;
            margin: 2px 7px 0 7px;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: $accent;
            border: 1px solid $accent;
            width: 14px;
            margin: -4px 0;
            border-radius: 3px;
        }

        QScrollBar:vertical {
            padding: 0px;
            background: $scrollBg;
            width: 12px;
            margin: 0px;
        }
        QScrollBar:horizontal {
            padding: 0px;
            border: none;
            background: $scrollBg;
            height: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            margin: 2px;
            background: $scrollHandle;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:horizontal {
            margin: 2px;
            background: $scrollHandle;
            border-radius: 4px;
            min-width: 30px;
        }
        QScrollBar::handle:hover { background: $scrollHandleHover; }
        QScrollBar::handle:pressed { background: $scrollHandlePressed; }
        QScrollBar::add-line, QScrollBar::sub-line {
            width: 0px; height: 0px; background: none; border: none;
        }
        QScrollBar::add-page, QScrollBar::sub-page { background: none; }

        QPushButton {
            min-width: 70px;
            min-height: 22px;
            color: $buttonText;
            background: $button;
            border-radius: 3px;
            border: 1px solid $border;
            padding: 2px 8px;
        }
        QPushButton:hover { border: 1px solid $accent; background: $buttonHover; }
        QPushButton:pressed { background: $buttonPressed; }
        QPushButton:checked { background: $buttonPressed; border: 1px solid $accent; }
        QPushButton:disabled { color: $textDim; background: $panel; }

        QSplitter::handle { background: none; }
        QSplitter::handle:horizontal { width: 5px; background: $panel; }
        QSplitter::handle:vertical { height: 5px; background: $panel; }
        QSplitter::handle:hover { background: $accentHover; }
        QSplitter::handle:pressed { background: $accent; }

        QLineEdit {
            border: 1px solid $border;
            min-height: 20px;
            border-radius: 3px;
            padding: 0 4px;
            background: $inputBg;
            color: $text;
        }
        QLineEdit:focus { border: 1px solid $accent; }
        QLineEdit:disabled { border: 1px solid $border; color: $textDim; }

        QCheckBox, QRadioButton, QLabel { color: $text; background: none; }
        """)

_PROJECT_TITLE_TEMPLATE = Template("""
        QListView {
            border: none;
            border-top: 1px solid $border;
            background: $panel;
            color: $text;
            show-decoration-selected: 1;
        }
        QListView::item:selected:!active {
            color: $text;
            border: none;
            background: $selInactiveBg;
        }
        QListView::item:selected:active {
            color: $accentText;
            border: none;
            background: $accent;
        }
        """)

_BOTTOM_SWITCHER_TEMPLATE = Template("""
        QPushButton {
            min-height: 17px;
            background: none;
            color: $textDim;
            border: none;
            border-radius: 0px;
            min-width: 13ex;
            padding: 2px;
        }
        QPushButton:hover { color: $text; background: none; }
        QPushButton:pressed { background: none; }
        QPushButton:checked {
            color: $text;
            border-left: 1px solid $border;
            border-right: 1px solid $border;
        }
        QPushButton:disabled { color: $textDim; background: none; }
        """)

_EDITOR_TEMPLATE = Template("""
        QListView {
            border: 1px solid $border;
            color: $text;
            min-width: 500px;
            min-height: 190px;
            background: $panel;
            show-decoration-selected: 1;
        }
        QListView::item:selected { color: $accentText; font: bold;
            border: none; background: $accent; }
        QListView::item:selected:!active { color: $accentText; font: bold;
            border: none; background: $accent; }
        QListView::item:selected:active { color: $accentText;
            background: $accent; }
        QListView::item:hover { border-bottom: none; background: $hover; }
        """)

_MAIN_MENU_TEMPLATE = Template("""
        QPushButton {
            padding: 2px 6px;
            color: $textDim;
            background: transparent;
            border: none;
            border-radius: 0px;
        }
        QPushButton:hover { color: $text; }
        QPushButton:checked { color: $text; border-bottom: 2px solid $accent; }
        """)

_TOOL_WIDGET_TEMPLATE = Template("""
        QLabel#containerLabel {
            border-top: 2px solid $accent;
            border-left: 1px solid $border;
            border-right: 1px solid $border;
            border-bottom: 1px solid $border;
            background: $panelAlt;
        }
        QLabel#toolWidgetNameLabel {
            font: 600 13px;
            color: $text;
            letter-spacing: 0.2px;
        }
        QLabel#toolWidgetSectionLabel {
            font: 12px;
            color: $textDim;
            padding-top: 4px;
        }
        /* Combos inside pull-down sheets: full border, not header underlines. */
        QLabel#containerLabel QComboBox {
            border: 1px solid $border;
            border-radius: 2px;
            padding: 3px 6px;
            min-height: 22px;
            background: $inputBg;
            color: $text;
        }
        QLabel#containerLabel QComboBox:focus {
            border: 1px solid $accent;
        }
        QLabel#containerLabel QComboBox:disabled {
            color: $textDim;
            background: $panel;
        }
        QLabel#containerLabel QPushButton {
            border: 1px solid $border;
            border-radius: 2px;
            padding: 4px 10px;
            background: $button;
            color: $buttonText;
        }
        QLabel#containerLabel QPushButton:hover {
            background: $buttonHover;
            border-color: $accent;
        }
        """)

_VIEW_SWITCHER_TEMPLATE = Template("""
        QLabel { background: $accentHover; padding: 1px; }
        QToolButton {
            min-width: 30px;
            min-height: 30px;
            background: $panel;
            border-radius: 0px;
            border: none;
        }
        QToolButton:hover {
            background: $panelAlt;
            border: none;
            border-bottom: 3px solid $accentHover;
        }
        QToolButton:checked { background: $panelAlt; border-bottom: 3px solid $accent; }
        QToolButton:disabled { background: $panel; }
        """)


def _build(template, palette):
    return template.safe_substitute(palette)


def global_style(name="Light"):
    return _build(_GLOBAL_TEMPLATE, resolve_palette(name))


def themed(name="Light"):
    """Return all theme-dependent style strings for the given theme name."""
    p = resolve_palette(name)
    return {
        "globalStyle": _build(_GLOBAL_TEMPLATE, p),
        "projectTitleBoxStyle": _build(_PROJECT_TITLE_TEMPLATE, p),
        "bottomSwitcherStyle": _build(_BOTTOM_SWITCHER_TEMPLATE, p),
        "editorStyle": _build(_EDITOR_TEMPLATE, p),
        "mainMenuStyle": _build(_MAIN_MENU_TEMPLATE, p),
        "toolWidgetStyle": _build(_TOOL_WIDGET_TEMPLATE, p),
        "viewSwitcherStyle": _build(_VIEW_SWITCHER_TEMPLATE, p),
    }


def _qpalette(palette):
    """Build a QPalette from token colours so natively-painted surfaces
    (window/dialog backgrounds, etc.) match the stylesheet."""
    from PyQt6.QtGui import QColor, QPalette
    Role = QPalette.ColorRole
    qp = QPalette()
    mapping = {
        "Window": "bg",
        "WindowText": "text",
        "Base": "inputBg",
        "AlternateBase": "panel",
        "Text": "text",
        "Button": "button",
        "ButtonText": "buttonText",
        "ToolTipBase": "tooltipBg",
        "ToolTipText": "tooltipText",
        "Highlight": "accent",
        "HighlightedText": "accentText",
        "PlaceholderText": "textDim",
        "BrightText": "accentText",
    }
    for role_name, token in mapping.items():
        role = getattr(Role, role_name, None)
        if role is not None and token in palette:
            qp.setColor(role, QColor(palette[token]))
    return qp


_BASE_APP_FONT_SIZE = None


def apply_ui_font_scale(app, percent):
    """Scale the application font for accessibility (75–150%)."""
    global _BASE_APP_FONT_SIZE
    if app is None:
        return
    font = app.font()
    if _BASE_APP_FONT_SIZE is None:
        size = font.pointSize()
        _BASE_APP_FONT_SIZE = size if size > 0 else 10
    try:
        scale = max(75, min(150, int(percent))) / 100.0
    except (TypeError, ValueError):
        scale = 1.0
    font.setPointSize(max(8, int(round(_BASE_APP_FONT_SIZE * scale))))
    app.setFont(font)


def apply_theme(app, name):
    """Apply ``name`` as the active theme.

    Refreshes the module-level style strings (so widgets built afterwards use
    the new palette), sets a matching QPalette, and applies the application
    stylesheet immediately.
    """
    global CURRENT_PALETTE, CURRENT_THEME
    styles = themed(name)
    globals().update(styles)
    CURRENT_PALETTE = resolve_palette(name)
    CURRENT_THEME = name
    if app is not None:
        try:
            app.setPalette(_qpalette(CURRENT_PALETTE))
        except Exception:
            pass
        app.setStyleSheet(styles["globalStyle"])
    return styles


def apply_native(app):
    """Drop custom theming so Qt's native style/palette paint the UI.

    Clearing only the stylesheet is not enough: a prior Dark theme leaves a
    light ``ButtonText`` / ``WindowText`` palette that makes labels (e.g.
    toolbar \"Menu\") invisible on light native backgrounds.
    """
    global CURRENT_PALETTE, CURRENT_THEME
    CURRENT_THEME = None
    # Keep Light tokens for Default-lexer overlays while the chrome is native.
    CURRENT_PALETTE = dict(LIGHT)
    globals().update(themed("Light"))
    if app is not None:
        app.setStyleSheet("")
        try:
            style = app.style()
            if style is not None:
                app.setPalette(style.standardPalette())
            else:
                from PyQt6.QtWidgets import QApplication as _QA
                app.setPalette(_QA.style().standardPalette())
        except Exception:
            pass
        # Force chrome to repaint with the restored palette.
        try:
            for widget in app.allWidgets():
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()
        except Exception:
            pass
    return themed("Light")


def chrome_style(key, custom=True):
    """Return a themed chrome stylesheet, or empty string for native UI."""
    if not custom:
        return ""
    return globals().get(key, "")


def theme_overlay_style(style):
    """Overlay UI-theme editor tokens onto a lexer Default style dict.

    Mutates a shallow copy of ``style`` so custom XML schemes stay untouched
    when callers pass them through. Only keys present in both the style and
    the theme mapping are updated (fg + paper).
    """
    palette = CURRENT_PALETTE or LIGHT
    paper = palette.get("editorPaper", "#FFFFFF")
    mapping = {
        "Default": ("editorText", paper),
        "Identifier": ("editorText", paper),
        "Operator": ("editorText", paper),
        "Number": ("editorText", paper),
        "Comment": ("editorComment", paper),
        "CommentBlock": ("editorComment", paper),
        "Keyword": ("editorKeyword", paper),
        "ClassName": ("editorKeyword", paper),
        "FunctionMethodName": ("editorKeyword", paper),
        "DoubleQuotedString": ("editorString", paper),
        "SingleQuotedString": ("editorString", paper),
        "TripleSingleQuotedString": ("editorString", paper),
        "TripleDoubleQuotedString": ("editorString", paper),
    }
    out = dict(style)
    for key, (fg_token, bg) in mapping.items():
        if key not in out:
            continue
        attrib = list(out[key])
        if len(attrib) < 6:
            continue
        attrib[1] = palette.get(fg_token, attrib[1])
        attrib[5] = bg
        out[key] = attrib
    return out


def theme_paper():
    """Return (mode, color) paper tuple for Default lexers under the UI theme."""
    return ("Plain", CURRENT_PALETTE.get("editorPaper", "#FFFFFF"))


# Default module-level names (Light) for import-time compatibility.
globals().update(themed("Light"))
