"""Project manifest (project.json with legacy project.xml migration)."""

import json
import logging
import os
import traceback

from PyQt6.QtXml import QDomDocument


def _json_path(project_root):
    return os.path.join(project_root, "project.json")


def _xml_path(project_root):
    return os.path.join(project_root, "project.xml")


def _parse_xml(path):
    dom_document = QDomDocument()
    with open(path, "r") as f:
        dom_document.setContent(f.read())
    node = dom_document.documentElement().firstChild()
    while node.isNull() is False:
        tag = node.toElement()
        if tag.tagName() == "pcode_project":
            return {
                "version": tag.attribute("Version") or "0.1",
                "name": tag.attribute("Name"),
                "type": tag.attribute("Type"),
                "mainscript": tag.attribute("MainScript"),
            }
        node = node.nextSibling()
    return None


def read(project_root):
    json_path = _json_path(project_root)
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("name"):
                return "pcode_project", {
                    "Version": data.get("version", "0.1"),
                    "Name": data["name"],
                    "Type": data.get("type", "Console Application"),
                    "MainScript": data.get("mainscript", "main.py"),
                }
        except Exception:
            logging.error(traceback.format_exc())

    xml_path = _xml_path(project_root)
    if os.path.isfile(xml_path):
        parsed = _parse_xml(xml_path)
        if parsed:
            return "pcode_project", {
                "Version": parsed["version"],
                "Name": parsed["name"],
                "Type": parsed["type"],
                "MainScript": parsed["mainscript"],
            }
    return False


def write(project_root, name, project_type, mainscript, version="0.1"):
    os.makedirs(project_root, exist_ok=True)
    payload = {
        "version": version,
        "name": name,
        "type": project_type,
        "mainscript": mainscript,
    }
    with open(_json_path(project_root), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
