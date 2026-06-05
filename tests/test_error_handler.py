"""Unit tests for the global excepthook."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions import ErrorHandler  # noqa: E402


def test_install_is_idempotent():
    ErrorHandler._installed = False
    ErrorHandler.install()
    hook = sys.excepthook
    ErrorHandler.install()
    assert sys.excepthook is hook


def test_keyboard_interrupt_uses_default_hook(monkeypatch):
    ErrorHandler.install()
    calls = []

    def fake_default(exc_type, exc_value, exc_traceback):
        calls.append((exc_type, exc_value, exc_traceback))

    monkeypatch.setattr(sys, "__excepthook__", fake_default)
    ErrorHandler.handle_exception(KeyboardInterrupt, KeyboardInterrupt(), None)
    assert len(calls) == 1
    assert calls[0][0] is KeyboardInterrupt


def test_handle_exception_logs_and_does_not_reraise(monkeypatch, caplog):
    import logging

    ErrorHandler.install()
    monkeypatch.setattr(ErrorHandler, "_show_dialog", lambda *a, **k: None)

    with caplog.at_level(logging.ERROR):
        ErrorHandler.handle_exception(ValueError, ValueError("boom"), None)

    assert any("Unhandled exception" in r.message for r in caplog.records)
    assert any("ValueError: boom" in r.message for r in caplog.records)
