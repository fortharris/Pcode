"""Tests for cx_Freeze build profile JSON persistence."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.BuildProfile import default_profile, load, save  # noqa: E402

BUILD_XML = """<?xml version="1.0" encoding="UTF-8"?>
<build>
  <name>TestApp</name>
  <author>Author</author>
  <version>2.0</version>
  <base>Win32GUI</base>
  <compress>Compress</compress>
  <optimize>Optimize</optimize>
  <Includes><item>os</item></Includes>
  <Excludes></Excludes>
</build>
"""


def test_default_profile_save_creates_json_and_xml(tmp_path):
    build_dir = tmp_path / "Build"
    profile = default_profile("Win32GUI")
    scalars = {k: v for k, v in profile.items() if k != "lists"}
    save(str(build_dir), scalars, profile["lists"])
    assert (build_dir / "profile.json").is_file()
    assert (build_dir / "profile.xml").is_file()
    data = json.loads((build_dir / "profile.json").read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["base"] == "Win32GUI"
    assert data["version_field"] == "0.1"


def test_load_prefers_json_over_xml(tmp_path):
    build_dir = tmp_path / "Build"
    build_dir.mkdir()
    profile = default_profile("Console")
    scalars = {k: v for k, v in profile.items() if k != "lists"}
    scalars["name"] = "FromJson"
    save(str(build_dir), scalars, profile["lists"])
    (build_dir / "profile.xml").write_text(BUILD_XML, encoding="utf-8")
    data = load(str(build_dir))
    assert data["name"] == "FromJson"
    assert data["version"] == "0.1"


def test_load_migrates_xml(tmp_path):
    build_dir = tmp_path / "Build"
    build_dir.mkdir()
    (build_dir / "profile.xml").write_text(BUILD_XML, encoding="utf-8")
    data = load(str(build_dir))
    assert data["name"] == "TestApp"
    assert data["version"] == "2.0"
    assert data["base"] == "Win32GUI"
    assert data["Includes"] == ["os"]
