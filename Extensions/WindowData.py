"""Per-project window layout persistence (JSON)."""

import base64
import json
import logging
import os
import traceback

from PyQt6.QtCore import QByteArray

# v2: sidebar on the left; outline starts collapsed. Older layouts that
# stored a right-hand sidebar are ignored for hsplitter/sidesplitter.
LAYOUT_VERSION = 2


def _windata_path(project_root):
    return os.path.join(project_root, "Data", "windata.json")


def _encode_state(byte_array):
    if byte_array is None:
        return None
    return base64.b64encode(bytes(byte_array)).decode("ascii")


def _decode_state(data):
    if not data:
        return None
    return QByteArray(base64.b64decode(data.encode("ascii")))


def capture(editor_window):
    geo = editor_window.writePad.geometry()
    return {
        "version": LAYOUT_VERSION,
        "hsplitter": _encode_state(editor_window.hSplitter.saveState()),
        "vsplitter": _encode_state(editor_window.vSplitter.saveState()),
        "sidesplitter": _encode_state(editor_window.sideSplitter.saveState()),
        "writepad": [geo.x(), geo.y(), geo.width(), geo.height()],
    }


def apply_defaults(editor_window, include_vertical=True):
    """Sidebar left (~240px), outline collapsed, editor takes remaining width."""
    total = max(editor_window.width(), 900)
    side = 240
    editor = max(480, total - side)
    editor_window.hSplitter.setSizes([side, editor])
    editor_window.sideSplitter.setSizes([0, side])
    if include_vertical:
        editor_window.vSplitter.setSizes([max(400, total - 140), 120])


def apply(editor_window, data):
    if not data:
        apply_defaults(editor_window)
        return
    version = int(data.get("version") or 1)
    restore_side = version >= LAYOUT_VERSION
    v_state = _decode_state(data.get("vsplitter"))
    if v_state is not None:
        editor_window.vSplitter.restoreState(v_state)
    if restore_side:
        for key, target in (
            ("hsplitter", editor_window.hSplitter),
            ("sidesplitter", editor_window.sideSplitter),
        ):
            state = _decode_state(data.get(key))
            if state is not None:
                target.restoreState(state)
    else:
        apply_defaults(editor_window, include_vertical=(v_state is None))
    wp = data.get("writepad")
    if isinstance(wp, (list, tuple)) and len(wp) == 4:
        editor_window.writePad.setGeometry(*wp)
    update_status = getattr(editor_window.vSplitter, "updateStatus", None)
    if callable(update_status):
        update_status()


def save(project_root, data):
    path = _windata_path(project_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load(project_root):
    path = _windata_path(project_root)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logging.error(traceback.format_exc())
        return None
