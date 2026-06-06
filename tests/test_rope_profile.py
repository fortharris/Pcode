"""Tests for rope profile JSON persistence."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.RopeProfile import default_profile, load, save  # noqa: E402

ROPE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rope>
  <ignoresyntaxerrors>Ignore Syntax Errors</ignoresyntaxerrors>
  <ignorebadimports></ignorebadimports>
  <maxhistoryitems>16</maxhistoryitems>
  <Extensions><item>*.py</item></Extensions>
  <IgnoredResources><item>*.pyc</item></IgnoredResources>
  <CustomFolders></CustomFolders>
</rope>
"""


def test_default_profile_save_creates_json_only(tmp_path):
    rope_dir = tmp_path / "Rope"
    save(str(rope_dir), default_profile())
    assert (rope_dir / "profile.json").is_file()
    assert not (rope_dir / "profile.xml").exists()
    data = json.loads((rope_dir / "profile.json").read_text(encoding="utf-8"))
    assert data["max_history_items"] == 32
    assert "*.py" in data["extensions"]


def test_load_migrates_xml(tmp_path):
    rope_dir = tmp_path / "Rope"
    rope_dir.mkdir()
    (rope_dir / "profile.xml").write_text(ROPE_XML, encoding="utf-8")
    data = load(str(rope_dir))
    assert data["ignore_syntax_errors"] == "Ignore Syntax Errors"
    assert data["max_history_items"] == 16
    assert data["extensions"] == ["*.py"]
