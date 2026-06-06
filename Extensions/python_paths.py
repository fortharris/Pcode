"""Interpreter and stdlib path helpers (rope, cx_Freeze, etc.)."""

import os
import sys
import sysconfig


def venv_python(venv_dir):
    """Return the python executable inside a virtual environment."""
    if sys.platform == "win32":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")


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
