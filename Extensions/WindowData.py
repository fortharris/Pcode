"""Per-project window layout persistence (JSON)."""

import base64
import json
import logging
import os
import traceback

from Extensions.qt_bindings import QtCore


def _windata_path(project_root):
    return os.path.join(project_root, "Data", "windata.json")


def _encode_state(byte_array):
    if byte_array is None:
        return None
    return base64.b64encode(bytes(byte_array)).decode("ascii")


def _decode_state(data):
    if not data:
        return None
    return QtCore.QByteArray(base64.b64decode(data.encode("ascii")))


def capture(editor_window):
    geo = editor_window.writePad.geometry()
    return {
        "version": 1,
        "hsplitter": _encode_state(editor_window.hSplitter.saveState()),
        "vsplitter": _encode_state(editor_window.vSplitter.saveState()),
        "sidesplitter": _encode_state(editor_window.sideSplitter.saveState()),
        "writepad": [geo.x(), geo.y(), geo.width(), geo.height()],
    }


def apply(editor_window, data):
    if not data:
        return
    for key, target in (
        ("hsplitter", editor_window.hSplitter),
        ("vsplitter", editor_window.vSplitter),
        ("sidesplitter", editor_window.sideSplitter),
    ):
        state = _decode_state(data.get(key))
        if state is not None:
            target.restoreState(state)
    wp = data.get("writepad")
    if isinstance(wp, (list, tuple)) and len(wp) == 4:
        editor_window.writePad.setGeometry(*wp)
    editor_window.vSplitter.updateStatus()


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
