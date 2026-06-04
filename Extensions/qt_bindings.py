"""
PySide6 bindings with PyQt4-compatible QtGui namespace for incremental migration.

Import Qt widgets via QtGui as in the original PyQt4 code (e.g. QtGui.QWidget).
"""

from PySide6 import QtCore, QtGui, QtWidgets, QtXml

# PyQt4 used pyqtSignal; PySide6 uses Signal
if not hasattr(QtCore, "pyqtSignal"):
    QtCore.pyqtSignal = QtCore.Signal

# Re-export QWidget and other QtWidgets classes on QtGui (PyQt4 layout)
_WIDGET_NAMES = []
for _name in dir(QtWidgets):
    if _name.startswith("Q"):
        _obj = getattr(QtWidgets, _name)
        if isinstance(_obj, type):
            if not hasattr(QtGui, _name):
                setattr(QtGui, _name, _obj)
            _WIDGET_NAMES.append(_name)

# QApplication lives in QtWidgets in Qt6 but was in QtGui in PyQt4
if not hasattr(QtGui, "QApplication"):
    QtGui.QApplication = QtWidgets.QApplication


def patch_layout_margins(layout):
    """PyQt4 QLayout.setMargin -> Qt6 setContentsMargins."""
    if layout is None:
        return layout
    if not hasattr(layout, "setMargin"):
        _margin = [0]

        def setMargin(m):
            _margin[0] = m
            layout.setContentsMargins(m, m, m, m)

        layout.setMargin = setMargin
    return layout


def patch_widget(widget):
    """Patch top-level widget layouts after setLayout."""
    layout = widget.layout()
    if layout is not None:
        patch_layout_margins(layout)
    return widget


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


def font_metrics_width(font_metrics, text):
    """QFontMetrics.width -> horizontalAdvance (Qt 5.11+)."""
    if hasattr(font_metrics, "horizontalAdvance"):
        return font_metrics.horizontalAdvance(text)
    return font_metrics.width(text)


def patch_font_metrics(widget):
    fm = widget.fontMetrics()
    if not hasattr(fm, "width") or fm.width.__func__ != font_metrics_width:
        _orig = fm

        class _FMProxy:
            def __getattr__(self, name):
                return getattr(_orig, name)

            def width(self, text):
                return font_metrics_width(_orig, text)

        widget.fontMetrics = lambda: _FMProxy()
    return widget


def exec_dialog(dialog):
    """QDialog.exec_ -> exec."""
    return dialog.exec()


def exec_menu(menu, pos):
    return menu.exec(pos)


def file_dialog_path(result):
    """Normalize QFileDialog return value (str in PyQt4, tuple in Qt6)."""
    if result is None:
        return None
    if isinstance(result, (tuple, list)):
        if not result or not result[0]:
            return None
        return result[0]
    if isinstance(result, str) and not result:
        return None
    return result


def file_dialog_paths(result):
    """Normalize getOpenFileNames return value."""
    if result is None:
        return []
    if isinstance(result, (tuple, list)):
        if len(result) >= 1 and isinstance(result[0], (tuple, list)):
            paths = result[0]
        elif len(result) >= 1 and isinstance(result[0], str):
            paths = [result[0]] if len(result) == 1 or not result[1] else list(result[0])
        else:
            paths = [p for p in result if isinstance(p, str) and p]
            return paths
        return [p for p in paths if p]
    return [result] if result else []


def _wrap_file_dialog_method(method_name, normalizer):
    original = getattr(QtWidgets.QFileDialog, method_name)

    def wrapper(*args, **kwargs):
        return normalizer(original(*args, **kwargs))

    setattr(QtWidgets.QFileDialog, method_name, staticmethod(wrapper))
    if hasattr(QtGui, "QFileDialog"):
        setattr(QtGui.QFileDialog, method_name, staticmethod(wrapper))


_wrap_file_dialog_method("getOpenFileName", file_dialog_path)
_wrap_file_dialog_method("getSaveFileName", file_dialog_path)
_wrap_file_dialog_method("getExistingDirectory", file_dialog_path)
_wrap_file_dialog_method("getOpenFileNames", file_dialog_paths)
