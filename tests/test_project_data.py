"""Tests for project-level JSON persistence."""

import json
import os
import sys


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.ProjectData import load, save  # noqa: E402


PROJECT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<projectdata>
  <shortcuts><shortcut>src</shortcut></shortcuts>
  <recentfiles><recent>{recent}</recent></recentfiles>
  <favourites><fav>main.py</fav></favourites>
  <settings><key>RunInternal=True</key><key>Closed=True</key></settings>
  <launchers><item path="/bin/python" param="-V"/></launchers>
</projectdata>
"""


def test_load_migrates_xml_to_json(tmp_path):
    data_dir = tmp_path / "Data"
    data_dir.mkdir()
    recent = str(tmp_path / "src" / "main.py")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("pass\n")
    (data_dir / "projectdata.xml").write_text(
        PROJECT_XML.format(recent=recent))

    project_data = load(str(tmp_path))

    assert project_data["shortcuts"] == ["src"]
    assert recent in project_data["recentfiles"]
    assert project_data["launchers"]["/bin/python"] == "-V"
    assert project_data["settings"]["RunInternal"] is True
    assert project_data["settings"]["Closed"] is False

    json_path = data_dir / "projectdata.json"
    save(str(tmp_path), project_data)
    assert json_path.is_file()
    on_disk = json.loads(json_path.read_text(encoding="utf-8"))
    assert on_disk["version"] == 1
    assert on_disk["settings"]["RunInternal"] is True


def test_load_empty_project(tmp_path):
    project_data = load(str(tmp_path))
    assert project_data["shortcuts"] == []
    assert project_data["settings"]["Closed"] is False
