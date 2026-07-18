"""Shared pytest hooks for headless Qt tests and CI."""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.path.join(REPO_ROOT, "workspace", "PcodeProjects")


def _ensure_test_workspace():
    """Create the default workspace tree so UseData never blocks on Workspace.exec()."""
    for sub in (
        "Projects",
        "Snippets",
        "Library",
        os.path.join("Settings", "ColorSchemes", "Python"),
        os.path.join("Settings", "ColorSchemes", "Xml"),
        os.path.join("Settings", "ColorSchemes", "Html"),
        os.path.join("Settings", "ColorSchemes", "Css"),
    ):
        os.makedirs(os.path.join(WORKSPACE, sub), exist_ok=True)


def _stub_modal_dialogs():
    from PyQt6.QtWidgets import QMessageBox
    from Extensions import ErrorHandler

    for name in ("warning", "critical", "information", "question"):
        setattr(QMessageBox, name, staticmethod(lambda *a, **k: None))
    ErrorHandler._show_dialog = lambda *a, **k: None


@pytest.fixture(scope="session", autouse=True)
def _headless_ci_env():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    _ensure_test_workspace()
    _stub_modal_dialogs()

    from Extensions.UseData import UseData

    UseData.getPythonExecutables = lambda self: [sys.executable]
    yield
