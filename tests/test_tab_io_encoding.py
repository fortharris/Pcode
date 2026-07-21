from Extensions.tab_io import write_editor_to_path


class _FakeEditor:
    def __init__(self, text):
        self._text = text
        self._modified = True

    def text(self):
        return self._text

    def setModified(self, value):
        self._modified = value


def test_write_honors_encoding(tmp_path):
    path = tmp_path / "latin.txt"
    editor = _FakeEditor("caf\u00e9")
    ok, used = write_editor_to_path(editor, str(path), "latin-1")
    assert ok
    assert used == "latin-1"
    assert path.read_bytes() == "caf\u00e9".encode("latin-1")
    assert editor._modified is False


def test_write_falls_back_to_utf8(tmp_path):
    path = tmp_path / "wide.txt"
    editor = _FakeEditor("hello \u2603")
    ok, used = write_editor_to_path(editor, str(path), "ascii")
    assert ok
    assert used == "utf-8"
    assert "\u2603" in path.read_text(encoding="utf-8")
