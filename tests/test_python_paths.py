"""Unit tests for interpreter / venv path helpers."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.python_paths import (  # noqa: E402
    venv_bin_dir,
    venv_create_command,
    venv_exists,
    venv_python,
    venv_search_paths,
    venv_site_packages,
)


def _fake_venv(root):
    """Create a minimal on-disk venv layout for path helpers."""
    root = os.path.abspath(root)
    if sys.platform == "win32":
        scripts = os.path.join(root, "Scripts")
        os.makedirs(scripts)
        open(os.path.join(scripts, "python.exe"), "w").close()
        site = os.path.join(root, "Lib", "site-packages")
        os.makedirs(site)
    else:
        bin_dir = os.path.join(root, "bin")
        os.makedirs(bin_dir)
        open(os.path.join(bin_dir, "python"), "w").close()
        site = os.path.join(
            root, "lib",
            "python{0}.{1}".format(sys.version_info.major, sys.version_info.minor),
            "site-packages")
        os.makedirs(site)
    with open(os.path.join(root, "pyvenv.cfg"), "w", encoding="utf-8") as cfg:
        cfg.write("home = /tmp\n")
        cfg.write("version = {0}.{1}.0\n".format(
            sys.version_info.major, sys.version_info.minor))
    return root, site


def test_venv_create_command():
    assert venv_create_command("py", "dir") == [
        "py", "-m", "venv", "--upgrade-deps", "dir"]
    assert venv_create_command("py", "dir", upgrade=True) == [
        "py", "-m", "venv", "--upgrade", "dir"]


def test_venv_python_and_bin_dir(tmp_path):
    root, _site = _fake_venv(tmp_path / "Venv")
    assert venv_exists(root)
    assert os.path.isfile(venv_python(root))
    assert os.path.isdir(venv_bin_dir(root))
    assert venv_bin_dir(root) == os.path.dirname(venv_python(root))


def test_venv_exists_false_when_missing(tmp_path):
    assert not venv_exists(str(tmp_path / "missing"))
    assert not venv_exists("")


def test_venv_site_packages(tmp_path):
    root, site = _fake_venv(tmp_path / "Venv")
    assert os.path.normpath(venv_site_packages(root)) == os.path.normpath(site)


def test_venv_search_paths(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    root, site = _fake_venv(tmp_path / "Venv")
    paths = venv_search_paths(root, sourcedir=str(src))
    assert all(os.path.isdir(p) for p in paths)
    assert os.path.normpath(str(src)) in [os.path.normpath(p) for p in paths]
    assert os.path.normpath(site) in [os.path.normpath(p) for p in paths]
    assert os.path.normpath(venv_bin_dir(root)) in [
        os.path.normpath(p) for p in paths]
