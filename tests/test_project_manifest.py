"""Tests for project.json manifest read/write."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.ProjectManifest import read, write  # noqa: E402


PROJECT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <pcode_project Version="0.1" Name="Demo" Type="Console Application"
                 MainScript="main.py"/>
</properties>
"""


def test_write_creates_json_and_xml(tmp_path):
    write(str(tmp_path), "Demo", "Console Application", "main.py")
    json_path = tmp_path / "project.json"
    xml_path = tmp_path / "project.xml"
    assert json_path.is_file()
    assert xml_path.is_file()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["name"] == "Demo"
    assert data["mainscript"] == "main.py"


def test_read_prefers_json(tmp_path):
    write(str(tmp_path), "FromJson", "Console Application", "app.py")
    (tmp_path / "project.xml").write_text(PROJECT_XML, encoding="utf-8")
    tag, data = read(str(tmp_path))
    assert tag == "pcode_project"
    assert data["Name"] == "FromJson"


def test_read_legacy_xml_only(tmp_path):
    (tmp_path / "project.xml").write_text(PROJECT_XML, encoding="utf-8")
    tag, data = read(str(tmp_path))
    assert data["Name"] == "Demo"
    assert data["MainScript"] == "main.py"
