"""Re-expose QScintilla scoped enum members as flat class attributes (PyQt4 style).

Newer PyQt6-QScintilla nests constants under scoped enums; legacy Pcode code
uses the flat names (e.g. ``QsciScintilla.WrapWord``).
"""

import enum


def _copy_enum_members(target_cls, enum_cls):
    members = getattr(enum_cls, "__members__", None)
    names = list(members.keys()) if members else [
        n for n in dir(enum_cls) if not n.startswith("_")]
    for name in names:
        if not hasattr(target_cls, name):
            try:
                setattr(target_cls, name, getattr(enum_cls, name))
            except (TypeError, AttributeError):
                pass


def apply_qscintilla_compat():
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


apply_qscintilla_compat()
