"""cx_Freeze build profile persistence (JSON with legacy XML migration)."""

import json
import logging
import os
import traceback

from PyQt6.QtXml import QDomDocument

LIST_KEYS = [
    "Includes", "Excludes", "Constants Modules", "Packages", "Replace Paths",
    "Bin Includes", "Bin Excludes", "Bin Path Includes", "Bin Path Excludes",
    "Zip Includes", "Include Files", "Namespace Packages",
]

SCALAR_KEYS = [
    "name", "author", "version", "comments", "description", "company",
    "copyright", "trademarks", "product", "base", "icon", "compress",
    "optimize", "copydeps", "appendscripttoexe", "appendscripttolibrary",
]


def _json_path(build_folder):
    return os.path.join(build_folder, "profile.json")


def _xml_path(build_folder):
    return os.path.join(build_folder, "profile.xml")


def default_profile(window_type="Console"):
    lists = {key: [] for key in LIST_KEYS}
    return {
        "name": "",
        "author": "",
        "version_field": "0.1",
        "comments": "",
        "description": "",
        "company": "",
        "copyright": "",
        "trademarks": "",
        "product": "",
        "base": window_type,
        "icon": "",
        "compress": "Compress",
        "optimize": "Optimize",
        "copydeps": "Copy Dependencies",
        "appendscripttoexe": "Append Script to Exe",
        "appendscripttolibrary": "Append Script to Library",
        "lists": lists,
    }


def _parse_xml(path):
    dom_document = QDomDocument()
    with open(path, "r", encoding="utf-8") as file:
        dom_document.setContent(file.read())

    lists = {key: [] for key in LIST_KEYS}
    scalars = {key: "" for key in SCALAR_KEYS}

    node = dom_document.documentElement().firstChild()
    while node.isNull() is False:
        name = node.nodeName()
        expanded = name.replace("-", " ")
        if expanded in lists:
            sub = node.firstChild()
            while sub.isNull() is False:
                lists[expanded].append(sub.toElement().text())
                sub = sub.nextSibling()
        else:
            scalars[name] = node.toElement().text()
        node = node.nextSibling()

    if scalars.get("version"):
        scalars["version_field"] = scalars.pop("version")
    else:
        scalars["version_field"] = "0.1"

    return scalars, lists


def _to_legacy_dict(scalars, lists):
    """Merge scalars + lists into the dict BuildConfig.load() returns."""
    data = dict(scalars)
    if "version_field" in data:
        data["version"] = data.pop("version_field")
    for key, items in lists.items():
        data[key] = items
    return data


def load(build_folder):
    json_path = _json_path(build_folder)
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            lists = {key: list(payload.get("lists", {}).get(key, []))
                     for key in LIST_KEYS}
            scalars = {key: payload.get(key, "") for key in SCALAR_KEYS
                       if key != "version"}
            scalars["version_field"] = payload.get("version_field", "0.1")
            return _to_legacy_dict(scalars, lists)
        except Exception:
            logging.error(traceback.format_exc())

    xml_path = _xml_path(build_folder)
    if os.path.isfile(xml_path):
        scalars, lists = _parse_xml(xml_path)
        return _to_legacy_dict(scalars, lists)

    profile = default_profile()
    scalars = {k: v for k, v in profile.items() if k != "lists"}
    return _to_legacy_dict(scalars, profile["lists"])


def save(build_folder, scalars, lists):
    os.makedirs(build_folder, exist_ok=True)
    payload = {"version": 1, "lists": lists}
    for key in SCALAR_KEYS:
        if key == "version":
            payload["version_field"] = scalars.get(
                "version_field", scalars.get("version", "0.1"))
        else:
            payload[key] = scalars.get(key, "")
    with open(_json_path(build_folder), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
