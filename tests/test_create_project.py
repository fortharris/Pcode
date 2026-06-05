"""Tests for new-project JSON artifacts."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.ProjectData import load  # noqa: E402
from Extensions.ProjectManifest import read  # noqa: E402
from Extensions.Projects.Projects import CreateProjectThread  # noqa: E402


def test_write_project_data_creates_json(tmp_path, monkeypatch):
    thread = CreateProjectThread.__new__(CreateProjectThread)
    thread.projectPath = str(tmp_path)
    thread.projDataDict = {
        "name": "TestProj",
        "type": "Console Application",
        "mainscript": "main.py",
    }
    thread.writeProjectData()
    thread.writePyproject()

    tag, manifest = read(str(tmp_path))
    assert tag == "pcode_project"
    assert manifest["Name"] == "TestProj"

    project_data = load(str(tmp_path))
    assert project_data["settings"]["DebugWait"] is False
    assert project_data["settings"]["Closed"] is False

    pyproject = tmp_path / "pyproject.toml"
    assert pyproject.is_file()
    assert "TestProj" in pyproject.read_text(encoding="utf-8")

    json_path = tmp_path / "Data" / "projectdata.json"
    assert json_path.is_file()
    on_disk = json.loads(json_path.read_text(encoding="utf-8"))
    assert on_disk["settings"]["RunType"] == "Run"
