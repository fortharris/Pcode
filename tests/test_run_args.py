from Extensions.BottomWidgets.RunWidget import split_run_arguments, script_argv


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
