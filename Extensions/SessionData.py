"""Editor session persistence (JSON with legacy XML migration)."""

import json
import logging
import os
import traceback

from Extensions.qt_bindings import QtXml
from Extensions.settings_utils import to_bool


def _session_json_path(project_path_dict):
    return os.path.join(project_path_dict["root"], "Data", "session.json")


def _session_xml_path(project_path_dict):
    return project_path_dict.get("session_xml") or os.path.join(
        project_path_dict["root"], "Data", "session.xml")


def _backup_json_path(project_path_dict):
    root = project_path_dict["root"]
    return os.path.join(root, "temp", "Backup", "bak.json")


def _backup_legacy_path(project_path_dict):
    return project_path_dict["backupfile"]


def _parse_xml_session(path):
    dom_document = QtXml.QDomDocument()
    with open(path, "r", encoding="utf-8") as f:
        dom_document.setContent(f.read())

    entries = []
    node = dom_document.documentElement().firstChild()
    while node.isNull() is False:
        tag = node.toElement()
        entry = {
            "path": tag.attribute("path") or None,
            "active": to_bool(tag.attribute("active")),
            "locked": to_bool(tag.attribute("locked")),
            "lines": int(tag.attribute("lines") or 0),
            "cursorPosition": tag.attribute("cursorPosition") or "0,0",
            "firstVisibleLine": int(tag.attribute("firstVisibleLine") or 0),
            "bookmarks": tag.attribute("bookmarks") or "",
            "folds": tag.attribute("folds") or "",
        }
        if tag.hasAttribute("backupKey"):
            entry["backupKey"] = tag.attribute("backupKey")
            entry["baseName"] = tag.attribute("baseName")
        entries.append(entry)
        node = node.nextSibling()
    return entries


def _load_entries(project_path_dict, backup=False):
    if backup:
        json_path = _backup_json_path(project_path_dict)
        legacy_path = _backup_legacy_path(project_path_dict)
    else:
        json_path = _session_json_path(project_path_dict)
        legacy_path = _session_xml_path(project_path_dict)

    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("files", [])
        except Exception:
            logging.error(traceback.format_exc())

    if os.path.isfile(legacy_path):
        return _parse_xml_session(legacy_path)
    return []


def save(project_path_dict, entries, backup=False):
    if backup:
        json_path = _backup_json_path(project_path_dict)
    else:
        json_path = _session_json_path(project_path_dict)
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    payload = {"version": 1, "files": entries}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load(project_path_dict, backup=False):
    return _load_entries(project_path_dict, backup=backup)


def write_empty_session(project_root):
    path = os.path.join(project_root, "Data", "session.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "files": []}, f, indent=2)
