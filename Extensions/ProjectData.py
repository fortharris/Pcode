"""Project-level data persistence (JSON with legacy XML migration)."""

import json
import logging
import os
import traceback

from Extensions.qt_bindings import QtXml
from Extensions.settings_utils import (
    normalize_project_settings, project_settings_for_json, to_bool,
)


def _projectdata_json_path(project_root):
    return os.path.join(project_root, "Data", "projectdata.json")


def _projectdata_xml_path(project_root):
    return os.path.join(project_root, "Data", "projectdata.xml")


def _parse_xml_projectdata(path):
    dom_document = QtXml.QDomDocument()
    with open(path, "r") as file:
        dom_document.setContent(file.read())

    shortcuts, recentfiles, favourites, launchers = [], [], [], {}
    settings_list = []
    node = dom_document.documentElement().firstChild()
    while node.isNull() is False:
        sub_node = node.toElement().firstChild()
        while sub_node.isNull() is False:
            sub_prop = sub_node.toElement()
            if node.nodeName() == "shortcuts":
                shortcuts.append(sub_prop.text())
            elif node.nodeName() == "recentfiles":
                if os.path.exists(sub_prop.text()):
                    recentfiles.append(sub_prop.text())
            elif node.nodeName() == "favourites":
                favourites.append(sub_prop.text())
            elif node.nodeName() == "settings":
                settings_list.append(tuple(sub_prop.text().split('=', 1)))
            elif node.nodeName() == "launchers":
                tag = sub_prop.toElement()
                launchers[tag.attribute("path")] = tag.attribute("param")
            sub_node = sub_node.nextSibling()
        node = node.nextSibling()
    settings = dict(settings_list)
    return {
        "version": 1,
        "shortcuts": shortcuts,
        "recentfiles": recentfiles,
        "favourites": favourites,
        "launchers": launchers,
        "settings": settings,
    }


def load(project_root):
    json_path = _projectdata_json_path(project_root)
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            logging.error(traceback.format_exc())
            data = {}
    else:
        xml_path = _projectdata_xml_path(project_root)
        data = _parse_xml_projectdata(xml_path) if os.path.isfile(xml_path) else {}

    settings = data.get("settings", {})
    settings["LastCloseSuccessful"] = settings.get("Closed", True)
    if isinstance(settings.get("LastCloseSuccessful"), str):
        settings["LastCloseSuccessful"] = to_bool(settings["LastCloseSuccessful"])
    settings["Closed"] = False
    data["settings"] = normalize_project_settings(settings)
    return {
        "shortcuts": data.get("shortcuts", []),
        "favourites": data.get("favourites", []),
        "recentfiles": data.get("recentfiles", []),
        "settings": data.get("settings", {}),
        "launchers": data.get("launchers", {}),
    }


def save(project_root, project_data):
    json_path = _projectdata_json_path(project_root)
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    payload = {
        "version": 1,
        "shortcuts": project_data.get("shortcuts", []),
        "recentfiles": project_data.get("recentfiles", []),
        "favourites": project_data.get("favourites", []),
        "launchers": project_data.get("launchers", {}),
        "settings": project_settings_for_json(project_data.get("settings", {})),
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def project_setting_bool(project_data, key, default=False):
    return to_bool(project_data.get("settings", {}).get(key), default)


def set_project_setting_bool(project_data, key, value):
    project_data.setdefault("settings", {})
    project_data["settings"][key] = to_bool(value)
