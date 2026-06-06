"""Rope refactor profile persistence (JSON with legacy XML migration)."""

import json
import logging
import os
import traceback

from PyQt6.QtXml import QDomDocument

DEFAULT_EXTENSIONS = ["*.py", "*.pyw"]
DEFAULT_IGNORED = [
    "*.pyc", "*~", ".ropeproject", ".hg", ".svn", "_svn", ".git", "__pycache__",
]


def _json_path(rope_folder):
    return os.path.join(rope_folder, "profile.json")


def _xml_path(rope_folder):
    return os.path.join(rope_folder, "profile.xml")


def _parse_xml(path):
    dom_document = QDomDocument()
    with open(path, "r", encoding="utf-8") as file:
        dom_document.setContent(file.read())

    data = {
        "ignore_syntax_errors": "",
        "ignore_bad_imports": "",
        "max_history_items": 32,
        "extensions": list(DEFAULT_EXTENSIONS),
        "ignored_resources": list(DEFAULT_IGNORED),
        "custom_folders": [],
    }
    node = dom_document.documentElement().firstChild()
    while node.isNull() is False:
        name = node.nodeName()
        if name == "ignoresyntaxerrors":
            data["ignore_syntax_errors"] = node.toElement().text()
        elif name == "ignorebadimports":
            data["ignore_bad_imports"] = node.toElement().text()
        elif name == "maxhistoryitems":
            try:
                data["max_history_items"] = int(node.toElement().text() or 32)
            except ValueError:
                pass
        elif name in ("Extensions", "IgnoredResources", "CustomFolders"):
            key = {
                "Extensions": "extensions",
                "IgnoredResources": "ignored_resources",
                "CustomFolders": "custom_folders",
            }[name]
            items = []
            sub = node.firstChild()
            while sub.isNull() is False:
                items.append(sub.toElement().text())
                sub = sub.nextSibling()
            data[key] = items
        node = node.nextSibling()
    return data


def default_profile():
    return {
        "version": 1,
        "ignore_syntax_errors": "",
        "ignore_bad_imports": "",
        "max_history_items": 32,
        "extensions": list(DEFAULT_EXTENSIONS),
        "ignored_resources": list(DEFAULT_IGNORED),
        "custom_folders": [],
    }


def load(rope_folder):
    json_path = _json_path(rope_folder)
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            base = default_profile()
            base.update(data)
            return base
        except Exception:
            logging.error(traceback.format_exc())

    xml_path = _xml_path(rope_folder)
    if os.path.isfile(xml_path):
        parsed = _parse_xml(xml_path)
        parsed["version"] = 1
        return parsed
    return default_profile()


def save(rope_folder, data):
    os.makedirs(rope_folder, exist_ok=True)
    payload = default_profile()
    payload.update(data)
    payload["version"] = 1
    with open(_json_path(rope_folder), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
