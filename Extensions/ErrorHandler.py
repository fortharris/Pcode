"""Global exception handling.

PyQt6 aborts the process when a Python exception escapes a slot (unlike PyQt4,
which printed and continued). That turned real bugs into silent "nothing
happens" failures. Installing a ``sys.excepthook`` keeps the app alive: it logs
the full traceback and shows a non-fatal dialog so the user (and the log) learn
what went wrong instead of the window simply disappearing.
"""

import sys
import logging
import traceback

from Extensions.qt_bindings import QtGui


_installed = False


def _show_dialog(text, detailed):
    app = QtGui.QApplication.instance()
    if app is None:
        return
    try:
        box = QtGui.QMessageBox()
        box.setIcon(QtGui.QMessageBox.Icon.Critical)
        box.setWindowTitle("Pcode - Unexpected Error")
        box.setText("An unexpected error occurred.\n\n" + text)
        box.setInformativeText(
            "The application will keep running, but may be in an "
            "inconsistent state. The full traceback was written to the log.")
        box.setDetailedText(detailed)
        box.setStandardButtons(QtGui.QMessageBox.StandardButton.Ok)
        box.exec()
    except Exception:
        # Never let the handler itself crash the process.
        logging.error("Error handler failed to display dialog:\n%s",
                      traceback.format_exc())


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    detailed = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error("Unhandled exception:\n%s", detailed)
    summary = "{0}: {1}".format(exc_type.__name__, exc_value)
    _show_dialog(summary, detailed)


def install():
    """Install the global excepthook (idempotent)."""
    global _installed
    if _installed:
        return
    sys.excepthook = handle_exception
    _installed = True
