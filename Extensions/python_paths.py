"""Interpreter and stdlib path helpers (rope, cx_Freeze, etc.)."""

import os
import re
import sys
import sysconfig


def venv_python(venv_dir):
    """Return the python executable inside a virtual environment."""
    if sys.platform == "win32":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")


def venv_bin_dir(venv_dir):
    """Return the Scripts/ (Windows) or bin/ (Unix) directory."""
    if sys.platform == "win32":
        return os.path.join(venv_dir, "Scripts")
    return os.path.join(venv_dir, "bin")


def venv_exists(venv_dir):
    """True if *venv_dir* contains a usable Python executable."""
    return bool(venv_dir) and os.path.isfile(venv_python(venv_dir))


def venv_create_command(python_path, venvdir, upgrade=False):
    """Return argv for creating or upgrading a project venv via stdlib venv."""
    args = [python_path, "-m", "venv"]
    if upgrade:
        args.append("--upgrade")
    else:
        args.append("--upgrade-deps")
    args.append(venvdir)
    return args


def _pyvenv_version(venv_dir):
    """Return (major, minor) from pyvenv.cfg, or None."""
    cfg = os.path.join(venv_dir, "pyvenv.cfg")
    if not os.path.isfile(cfg):
        return None
    try:
        with open(cfg, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or " = " not in line:
                    continue
                key, value = line.split(" = ", 1)
                if key.strip() == "version":
                    match = re.match(r"(\d+)\.(\d+)", value.strip())
                    if match:
                        return int(match.group(1)), int(match.group(2))
    except OSError:
        return None
    return None


def venv_site_packages(venv_dir):
    """Return the site-packages directory for a project virtual environment."""
    win_path = os.path.join(venv_dir, "Lib", "site-packages")
    if os.path.isdir(win_path):
        return win_path
    version = _pyvenv_version(venv_dir)
    if version is not None:
        unix_path = os.path.join(
            venv_dir, "lib", "python{0}.{1}".format(*version), "site-packages")
        if os.path.isdir(unix_path):
            return unix_path
    lib_root = os.path.join(venv_dir, "lib")
    if os.path.isdir(lib_root):
        for name in sorted(os.listdir(lib_root)):
            if name.startswith("python"):
                candidate = os.path.join(lib_root, name, "site-packages")
                if os.path.isdir(candidate):
                    return candidate
    if sys.platform == "win32":
        return win_path
    if version is not None:
        return os.path.join(
            venv_dir, "lib", "python{0}.{1}".format(*version), "site-packages")
    return os.path.join(
        venv_dir, "lib",
        "python{0}.{1}".format(sys.version_info.major, sys.version_info.minor),
        "site-packages")


def venv_search_paths(venv_dir, sourcedir=None):
    """Return existing freeze/search directories for a project venv."""
    candidates = []
    if sourcedir:
        candidates.append(sourcedir)
    candidates.extend([
        venv_bin_dir(venv_dir),
        os.path.join(venv_dir, "Lib"),
        os.path.join(venv_dir, "lib"),
        venv_site_packages(venv_dir),
        os.path.join(venv_dir, "Include"),
        os.path.join(venv_dir, "include"),
    ])
    seen = set()
    existing = []
    for path in candidates:
        if not path:
            continue
        path = os.path.normpath(path)
        if os.path.isdir(path) and path not in seen:
            seen.add(path)
            existing.append(path)
    return existing


def interpreter_stdlib_paths(interpreter=None):
    """Return existing stdlib/site-packages directories for *interpreter*."""
    if interpreter is None:
        interpreter = sys.executable
    interpreter = os.path.abspath(interpreter)
    py_dir = os.path.dirname(interpreter)
    venv_root = os.path.dirname(py_dir)
    candidates = [
        os.path.join(venv_root, "Lib"),
        os.path.join(venv_root, "lib"),
        os.path.join(py_dir, "Lib"),
        os.path.join(py_dir, "lib"),
    ]
    try:
        paths = sysconfig.get_paths(
            vars={"installed_base": venv_root, "base": venv_root,
                  "platbase": venv_root})
        for key in ("stdlib", "platstdlib", "purelib", "platlib"):
            candidates.append(paths.get(key, ""))
    except Exception:
        pass
    base = getattr(sys, "base_prefix", None)
    if base:
        candidates.extend([
            base,
            os.path.join(base, "Lib"),
            os.path.join(base, "lib"),
            os.path.join(base, "Lib", "site-packages"),
            os.path.join(base, "lib", "python{0}.{1}".format(
                sys.version_info.major, sys.version_info.minor),
                "site-packages"),
        ])
    seen = set()
    existing = []
    for path in candidates:
        if not path:
            continue
        path = os.path.normpath(path)
        if os.path.isdir(path) and path not in seen:
            seen.add(path)
            existing.append(path)
    return existing
