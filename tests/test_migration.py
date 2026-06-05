"""Tests for the legacy settings (XML) -> consolidated JSON migration.

These exercise UseData's migration helpers in isolation by bypassing the heavy
__init__ (which would touch the real workspace), so they stay fast and have no
side effects.
"""

import os
import sys
import json

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.qt_bindings import QtWidgets  # noqa: E402
from Extensions.UseData import UseData  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _app():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app


USEDATA_XML = """<?xml version="1.0" encoding="UTF-8"?>
<usedata>
  <openedprojects>
    <project>{proj}</project>
    <project>/does/not/exist</project>
  </openedprojects>
  <settings>
    <key>Theme=Dark</key>
    <key>EdgeColumn=100</key>
  </settings>
</usedata>
"""

MODULES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<modules>
  <os use="True"><item>path</item><item>getcwd</item></os>
  <sys use="False"><item>argv</item></sys>
</modules>
"""

KEYMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<keymap>
  <Ide><Find shortcut="Ctrl+Shift+F"/></Ide>
  <Editor><Copy-Selection shortcut="Ctrl+C" value="2178"/></Editor>
</keymap>
"""


def _make_usedata(tmp_path):
    # Bypass __init__ so we don't read/write the real workspace.
    u = UseData.__new__(UseData)
    u.appPathDict = {
        "usedata": str(tmp_path / "usedata.xml"),
        "modules": str(tmp_path / "modules.xml"),
        "keymap": str(tmp_path / "keymap.xml"),
        "datafile": str(tmp_path / "usedata.json"),
    }
    return u


def test_migrate_full_trio(tmp_path):
    proj = str(tmp_path)  # an existing path so it survives the load filter
    (tmp_path / "usedata.xml").write_text(USEDATA_XML.format(proj=proj))
    (tmp_path / "modules.xml").write_text(MODULES_XML)
    (tmp_path / "keymap.xml").write_text(KEYMAP_XML)

    u = _make_usedata(tmp_path)
    data = u._migrateLegacyXml()

    assert data["version"] == 1
    assert data["settings"]["Theme"] == "Dark"
    assert data["settings"]["EdgeColumn"] == "100"
    assert proj in data["openedProjects"]
    assert data["modules"]["os"] == [["path", "getcwd"], "True"]
    assert data["modules"]["sys"] == [["argv"], "False"]
    assert data["keymap"]["Ide"]["Find"] == "Ctrl+Shift+F"
    assert data["keymap"]["Editor"]["Copy-Selection"] == ["Ctrl+C", 2178]


def test_migrate_no_legacy_files_returns_empty(tmp_path):
    u = _make_usedata(tmp_path)
    assert u._migrateLegacyXml() == {}


def test_migrate_partial(tmp_path):
    # Only modules.xml present; settings/keymap default to empty.
    (tmp_path / "modules.xml").write_text(MODULES_XML)
    u = _make_usedata(tmp_path)
    data = u._migrateLegacyXml()
    assert data["modules"]["os"][1] == "True"
    assert data["settings"] == {}
    assert data["openedProjects"] == []
    assert data["keymap"] == {}


def test_read_workspace_data_migrates_and_writes_json(tmp_path):
    (tmp_path / "modules.xml").write_text(MODULES_XML)
    u = _make_usedata(tmp_path)

    data = u._readWorkspaceData()

    assert data["modules"]["sys"] == [["argv"], "False"]
    # The consolidated JSON must now exist on disk.
    datafile = u.appPathDict["datafile"]
    assert os.path.isfile(datafile)
    with open(datafile, "r", encoding="utf-8") as f:
        on_disk = json.load(f)
    assert on_disk["modules"]["os"] == [["path", "getcwd"], "True"]
