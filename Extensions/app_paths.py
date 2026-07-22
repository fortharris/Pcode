"""Resolve the application root for source and frozen (cx_Freeze) runs."""

from __future__ import annotations

import os
import sys


def is_frozen() -> bool:
    """True when running from a frozen executable (cx_Freeze / similar)."""
    return bool(getattr(sys, "frozen", False))


def get_app_root() -> str:
    """Directory that contains ``Resources/`` and is safe to ``chdir`` into.

    Frozen builds place ``Resources`` next to the executable. Source runs use
    the repository root (parent of ``Extensions/`` when called from there, or
    the directory of ``Pcode.py``).
    """
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    # Prefer the directory containing Pcode.py when importable.
    try:
        import Pcode as _pcode

        return os.path.dirname(os.path.abspath(_pcode.__file__))
    except Exception:
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), ".."))


def get_default_workspace_dir() -> str:
    """Writable workspace for projects/settings.

    Frozen installs default under LocalAppData so Program Files stays read-only.
    Source checkouts keep the in-repo ``workspace/PcodeProjects`` layout.
    """
    if is_frozen():
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "Pcode", "PcodeProjects")
    return os.path.join(get_app_root(), "workspace", "PcodeProjects")
