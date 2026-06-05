"""Tests for session JSON persistence."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.SessionData import load, save, write_empty_session, _parse_xml_session  # noqa: E402


SESSION_XML = """<?xml version="1.0" encoding="UTF-8"?>
<session>
  <file path="{path}" active="True" locked="False" lines="10"
        cursorPosition="3,0" firstVisibleLine="0" bookmarks="1-2" folds=""/>
</session>
"""


def test_parse_xml_session(tmp_path):
    main_py = tmp_path / "src" / "main.py"
    main_py.parent.mkdir(parents=True)
    main_py.write_text("pass\n")
    (tmp_path / "session.xml").write_text(
        SESSION_XML.format(path=str(main_py)), encoding="utf-8")
    entries = _parse_xml_session(str(tmp_path / "session.xml"))
    assert len(entries) == 1
    assert entries[0]["active"] is True
    assert entries[0]["bookmarks"] == "1-2"


def test_save_and_load_json(tmp_path):
    project = {"root": str(tmp_path), "backupfile": str(tmp_path / "bak")}
    entries = [{"path": "/x.py", "active": True, "locked": False,
                "lines": 1, "cursorPosition": "0,0",
                "firstVisibleLine": 0, "bookmarks": "", "folds": ""}]
    save(project, entries)
    loaded = load(project)
    assert loaded[0]["path"] == "/x.py"
    assert os.path.isfile(tmp_path / "Data" / "session.json")


def test_write_empty_session(tmp_path):
    write_empty_session(str(tmp_path))
    data = json.loads((tmp_path / "Data" / "session.json").read_text())
    assert data["files"] == []
