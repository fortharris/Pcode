from Extensions.Debug import collect_breakpoints
from Extensions.Debug.dap_client import DapClient


def test_collect_breakpoints_empty():
    assert collect_breakpoints(None) == {}


def test_dap_framing_roundtrip(qtbot=None):
    """Unit-test Content-Length framing without a live debugpy."""
    client = DapClient()
    # Simulate receiving one framed message.
    payload = {"seq": 1, "type": "event", "event": "initialized"}
    import json
    body = json.dumps(payload).encode("utf-8")
    frame = b"Content-Length: %d\r\n\r\n%s" % (len(body), body)
    client._buffer.append(frame)
    msg = client._read_one_message()
    assert msg["event"] == "initialized"
    assert client._read_one_message() is None


def test_breakpoint_line_conversion_helper():
    class FakeEditor:
        def getBreakpointLines(self):
            return [0, 4]  # 0-based

    class FakeTab:
        def count(self):
            return 1

        def getEditorData(self, attrib, index=None):
            return "C:/proj/main.py"

        def getEditor(self, index=None):
            return FakeEditor()

    bps = collect_breakpoints(FakeTab())
    assert bps["C:/proj/main.py"] == [1, 5]
