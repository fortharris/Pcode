"""Tests for per-project window layout JSON."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.WindowData import save, load  # noqa: E402


def test_save_and_load_roundtrip(tmp_path):
    payload = {
        "version": 1,
        "hsplitter": None,
        "vsplitter": "YWJj",
        "sidesplitter": None,
        "writepad": [1, 2, 300, 200],
    }
    save(str(tmp_path), payload)
    path = tmp_path / "Data" / "windata.json"
    assert path.is_file()
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["writepad"] == [1, 2, 300, 200]
    assert load(str(tmp_path)) == on_disk
