from Extensions.BottomWidgets.RunWidget import (
    split_run_arguments, script_argv, decode_process_bytes, pick_free_tcp_port,
)


def test_split_run_arguments_empty():
    assert split_run_arguments("") == []
    assert split_run_arguments(None) == []


def test_split_run_arguments_quoted():
    assert split_run_arguments('--flag "my file"') == ["--flag", "my file"]
    assert split_run_arguments("-a -b c") == ["-a", "-b", "c"]


def test_script_argv():
    assert script_argv("main.py", False, "--x") == ["main.py"]
    assert script_argv("main.py", True, '--flag "a b"') == [
        "main.py", "--flag", "a b"]


def test_decode_process_bytes_utf8():
    assert decode_process_bytes("café".encode("utf-8")) == "café"


def test_decode_process_bytes_invalid_does_not_raise():
    text = decode_process_bytes(b"ok\xff\xfe")
    assert text.startswith("ok")
    assert "\ufffd" in text or len(text) >= 2


def test_pick_free_tcp_port():
    port = pick_free_tcp_port()
    assert isinstance(port, int)
    assert 0 < port < 65536
