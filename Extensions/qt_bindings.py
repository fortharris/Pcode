"""
PyQt6 bindings with PyQt4-compatible QtGui namespace for incremental migration.

Import Qt widgets via QtGui as in the original PyQt4 code (e.g. QtGui.QWidget).
QScintilla is imported from PyQt6.Qsci (see requirements.txt).
"""

from PyQt6 import QtCore, QtGui, QtWidgets, QtXml

from Extensions.file_dialog_utils import file_dialog_path, file_dialog_paths  # noqa: F401
from Extensions.font_metrics import font_metrics_width  # noqa: F401

# Migration used PySide6's Signal; PyQt6 uses pyqtSignal
QtCore.Signal = QtCore.pyqtSignal

# Re-export QWidget and other QtWidgets classes on QtGui (PyQt4 layout)
for _name in dir(QtWidgets):
    if _name.startswith("Q"):
        _obj = getattr(QtWidgets, _name)
        if isinstance(_obj, type) and not hasattr(QtGui, _name):
            setattr(QtGui, _name, _obj)

if not hasattr(QtGui, "QApplication"):
    QtGui.QApplication = QtWidgets.QApplication


def primary_screen_geometry(app=None):
    """Replacement for QDesktopWidget().screenGeometry()."""
    if app is None:
        app = QtWidgets.QApplication.instance()
    if app is None:
        return QtCore.QRect(0, 0, 1024, 768)
    screen = app.primaryScreen()
    if screen is None:
        return QtCore.QRect(0, 0, 1024, 768)
    return screen.availableGeometry()


# PyQt4 allowed QFileDialog.Options() and passing it positionally after the
# name filter. PyQt6 removed Options and reorders args. Provide a stand-in and
# strip any Option-typed argument out of the call (defaults are always empty).
_FileDialogOption = QtWidgets.QFileDialog.Option


def _qfiledialog_options(*args, **kwargs):
    return _FileDialogOption(0)


QtWidgets.QFileDialog.Options = staticmethod(_qfiledialog_options)
if hasattr(QtGui, "QFileDialog"):
    QtGui.QFileDialog.Options = staticmethod(_qfiledialog_options)


def _strip_option_args(args):
    cleaned = []
    options = None
    for a in args:
        if isinstance(a, _FileDialogOption):
            options = a
        else:
            cleaned.append(a)
    return cleaned, options


def _wrap_file_dialog_method(method_name, normalizer):
    original = getattr(QtWidgets.QFileDialog, method_name)

    def wrapper(*args, **kwargs):
        args, options = _strip_option_args(args)
        if options is not None and "options" not in kwargs:
            kwargs["options"] = options
        return normalizer(original(*args, **kwargs))

    setattr(QtWidgets.QFileDialog, method_name, staticmethod(wrapper))
    if hasattr(QtGui, "QFileDialog"):
        setattr(QtGui.QFileDialog, method_name, staticmethod(wrapper))


_wrap_file_dialog_method("getOpenFileName", file_dialog_path)
_wrap_file_dialog_method("getSaveFileName", file_dialog_path)
_wrap_file_dialog_method("getExistingDirectory", file_dialog_path)
_wrap_file_dialog_method("getOpenFileNames", file_dialog_paths)


# PyQt4 accepted int orientations (1=Horizontal, 2=Vertical). PyQt6 requires
# Qt.Orientation. Coerce ints on QSplitter.setOrientation.
def _patch_splitter_orientation():
    QSplitter = QtWidgets.QSplitter
    _orig = QSplitter.setOrientation

    def setOrientation(self, orientation):
        if isinstance(orientation, int):
            orientation = (QtCore.Qt.Vertical if orientation == 2
                           else QtCore.Qt.Horizontal)
        return _orig(self, orientation)

    try:
        QSplitter.setOrientation = setOrientation
    except (TypeError, AttributeError):
        pass


_patch_splitter_orientation()


def _enum_member_names(enum_cls):
    """Return the member names of a (possibly flag) PyQt6 scoped enum.

    ``dir()`` does not reliably list members of flag enums, so prefer
    ``__members__`` when available.
    """
    members = getattr(enum_cls, "__members__", None)
    if members:
        return list(members.keys())
    return [n for n in dir(enum_cls) if not n.startswith("_")]


def _copy_enum_members(target_cls, enum_cls):
    """Re-expose a scoped enum's members as flat attributes on target_cls."""
    for name in _enum_member_names(enum_cls):
        if not hasattr(target_cls, name):
            try:
                setattr(target_cls, name, getattr(enum_cls, name))
            except (TypeError, AttributeError):
                pass


def _patch_qt6_compat():
    """Map PyQt4-style flat Qt enums to PyQt6 scoped enums."""
    Qt = QtCore.Qt

    if not hasattr(Qt, "Window"):
        W = Qt.WindowType
        for name in (
            "Window", "WindowCloseButtonHint", "FramelessWindowHint",
            "Dialog", "CustomizeWindowHint",
        ):
            if hasattr(W, name):
                setattr(Qt, name, getattr(W, name))

    if not hasattr(Qt, "WA_TranslucentBackground"):
        WA = Qt.WidgetAttribute
        for name in dir(WA):
            if name.startswith("WA_"):
                setattr(Qt, name, getattr(WA, name))

    if not hasattr(Qt, "NoItemFlags"):
        Qt.NoItemFlags = Qt.ItemFlag.NoItemFlags

    if not hasattr(Qt, "AscendingOrder"):
        Qt.AscendingOrder = Qt.SortOrder.AscendingOrder

    if not hasattr(Qt, "AlignHCenter"):
        Qt.AlignHCenter = Qt.AlignmentFlag.AlignHCenter

    if not hasattr(Qt, "WaitCursor"):
        Qt.WaitCursor = Qt.CursorShape.WaitCursor

    if not hasattr(Qt, "PreventContextMenu"):
        Qt.PreventContextMenu = Qt.ContextMenuPolicy.PreventContextMenu

    if not hasattr(Qt, "Vertical"):
        O = Qt.Orientation
        Qt.Vertical = O.Vertical
        Qt.Horizontal = O.Horizontal

    if not hasattr(Qt, "ToolButtonTextBesideIcon"):
        TBS = Qt.ToolButtonStyle
        Qt.ToolButtonTextBesideIcon = TBS.ToolButtonTextBesideIcon

    if not hasattr(Qt, "LeftButton"):
        MOUSE = Qt.MouseButton
        for name in ("NoButton", "LeftButton", "RightButton",
                     "MiddleButton", "XButton1", "XButton2"):
            if hasattr(MOUSE, name):
                setattr(Qt, name, getattr(MOUSE, name))
        # MidButton was the Qt4/5 alias for MiddleButton, removed in Qt6.
        if hasattr(MOUSE, "MiddleButton"):
            Qt.MidButton = MOUSE.MiddleButton

    KM = Qt.KeyboardModifier
    for old, new in (
        ("ShiftModifier", "ShiftModifier"),
        ("ControlModifier", "ControlModifier"),
        ("AltModifier", "AltModifier"),
        ("MetaModifier", "MetaModifier"),
        ("SHIFT", "ShiftModifier"),
        ("CTRL", "ControlModifier"),
        ("ALT", "AltModifier"),
        ("META", "MetaModifier"),
    ):
        if not hasattr(Qt, old) and hasattr(KM, new):
            setattr(Qt, old, getattr(KM, new))

    K = Qt.Key
    for name in (
        "Key_Backtab", "Key_Tab", "Key_Control", "Key_Meta",
        "Key_Shift", "Key_Alt", "Key_Menu", "Key_Backspace",
    ):
        if not hasattr(Qt, name) and hasattr(K, name):
            setattr(Qt, name, getattr(K, name))

    MB = QtWidgets.QMessageBox
    SB = MB.StandardButton
    for name in ("Yes", "No", "Ok", "Cancel"):
        if not hasattr(MB, name):
            setattr(MB, name, getattr(SB, name))
    if hasattr(QtGui, "QMessageBox"):
        for name in ("Yes", "No", "Ok", "Cancel"):
            if not hasattr(QtGui.QMessageBox, name):
                setattr(QtGui.QMessageBox, name, getattr(SB, name))

    def _flatten_enum_members(cls, enum_attr_names):
        """Re-expose nested enum members as flat class attributes (Qt5 style)."""
        for enum_name in enum_attr_names:
            enum = getattr(cls, enum_name, None)
            if enum is None:
                continue
            for member in dir(enum):
                if member.startswith("_"):
                    continue
                if not hasattr(cls, member):
                    try:
                        setattr(cls, member, getattr(enum, member))
                    except (TypeError, AttributeError):
                        pass

    _flatten_enum_members(QtWidgets.QPlainTextEdit, ["LineWrapMode"])
    _flatten_enum_members(QtWidgets.QTextEdit, ["LineWrapMode"])
    _flatten_enum_members(
        QtWidgets.QAbstractItemView,
        ["SelectionMode", "SelectionBehavior", "ScrollMode",
         "EditTrigger", "DragDropMode"])
    _flatten_enum_members(QtWidgets.QListView, ["ViewMode", "Flow", "Movement"])
    _flatten_enum_members(QtWidgets.QSizePolicy, ["Policy"])
    _flatten_enum_members(QtWidgets.QFileDialog, ["Option", "FileMode",
                                                  "AcceptMode", "ViewMode"])
    if hasattr(QtGui, "QPlainTextEdit"):
        _flatten_enum_members(QtGui.QPlainTextEdit, ["LineWrapMode"])
    if hasattr(QtGui, "QTextEdit"):
        _flatten_enum_members(QtGui.QTextEdit, ["LineWrapMode"])

    QDir = QtCore.QDir
    if not hasattr(QDir, "Files") and hasattr(QDir, "Filter"):
        _copy_enum_members(QDir, QDir.Filter)
    if hasattr(QDir, "SortFlag"):
        _copy_enum_members(QDir, QDir.SortFlag)

    QIOD = QtCore.QIODevice
    if not hasattr(QIOD, "ReadWrite") and hasattr(QIOD, "OpenModeFlag"):
        _copy_enum_members(QIOD, QIOD.OpenModeFlag)

    QEC = QtCore.QEasingCurve
    if not hasattr(QEC, "OutCubic") and hasattr(QEC, "Type"):
        _copy_enum_members(QEC, QEC.Type)

    QKS = QtGui.QKeySequence
    if not hasattr(QKS, "Copy") and hasattr(QKS, "StandardKey"):
        _copy_enum_members(QKS, QKS.StandardKey)

    QP = QtGui.QPalette
    if not hasattr(QP, "Background"):
        CR = QP.ColorRole
        for old, new in (("Background", "Window"),
                         ("Foreground", "WindowText")):
            if hasattr(CR, new):
                setattr(QP, old, getattr(CR, new))
        for name in dir(CR):
            if not name.startswith("_") and not hasattr(QP, name):
                setattr(QP, name, getattr(CR, name))

    QF = QtWidgets.QFrame
    if not hasattr(QF, "HLine"):
        S = QF.Shape
        for name in ("HLine", "VLine", "StyledPanel", "Box", "Panel", "NoFrame"):
            if hasattr(S, name):
                setattr(QF, name, getattr(S, name))
    if not hasattr(QF, "Sunken"):
        SH = QF.Shadow
        for name in ("Sunken", "Plain", "Raised"):
            if hasattr(SH, name):
                setattr(QF, name, getattr(SH, name))
    if hasattr(QtGui, "QFrame"):
        for name in ("HLine", "VLine", "StyledPanel", "Box", "Panel", "NoFrame",
                     "Sunken", "Plain", "Raised"):
            if hasattr(QF, name) and not hasattr(QtGui.QFrame, name):
                setattr(QtGui.QFrame, name, getattr(QF, name))


_patch_qt6_compat()


def _patch_qscintilla():
    """Flatten QScintilla scoped enums back to flat attributes.

    Newer QScintilla moved constants such as ``WrapWord`` into scoped enums
    (``QsciScintilla.WrapMode.WrapWord``). The legacy code base accesses the
    flat names directly, so re-expose every enum member as a class attribute.
    The stored value is the enum member itself, so enum-typed setters accept
    it directly.
    """
    import enum
    try:
        from PyQt6.Qsci import QsciScintilla, QsciScintillaBase
    except ImportError:
        return
    for cls in (QsciScintillaBase, QsciScintilla):
        for attr in dir(cls):
            if attr.startswith("_"):
                continue
            obj = getattr(cls, attr)
            if isinstance(obj, type) and issubclass(obj, enum.Enum):
                _copy_enum_members(cls, obj)


_patch_qscintilla()
