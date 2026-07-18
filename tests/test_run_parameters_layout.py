"""SetRunParameters layout: sizing, args enablement, venv coupling."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (  # noqa: E402
    QApplication, QCheckBox, QComboBox, QLabel, QSpinBox,
)

from Extensions.BottomWidgets.RunWidget import SetRunParameters  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _settings():
    return {
        "RunType": "Run",
        "TraceType": "0",
        "RunWithArguments": "False",
        "RunArguments": "",
        "ClearOutputWindowOnRun": "True",
        "BufferSize": "900",
        "RunInternal": "True",
        "UseVirtualEnv": "False",
        "DebugWait": "False",
        "DefaultInterpreter": sys.executable,
    }


def test_pass_arguments_toggles_field(app):
    use = type("U", (), {"SETTINGS": {"InstalledInterpreters": [sys.executable]}})()
    sheet = SetRunParameters(_settings(), {"venvdir": "/tmp/venv"}, use)
    assert not sheet.argumentsLine.isEnabled()
    sheet.runWithArgsBox.setChecked(True)
    assert sheet.argumentsLine.isEnabled()
    assert sheet.projectSettings["RunWithArguments"] in (True, "True")


def test_venv_disables_interpreter_combo(app):
    use = type("U", (), {"SETTINGS": {"InstalledInterpreters": [sys.executable]}})()
    sheet = SetRunParameters(_settings(), {"venvdir": "/tmp/venv"}, use)
    assert sheet.installedPythonVersionBox.isEnabled()
    sheet.useVirtualEnvBox.setChecked(True)
    assert not sheet.installedPythonVersionBox.isEnabled()


def test_section_labels_present(app):
    use = type("U", (), {"SETTINGS": {"InstalledInterpreters": [sys.executable]}})()
    sheet = SetRunParameters(_settings(), {"venvdir": "/tmp/venv"}, use)
    labels = [
        w.text()
        for w in sheet.findChildren(QLabel)
        if w.objectName() == "toolWidgetSectionLabel"
    ]
    assert labels == ["Run", "Console", "Interpreter"]


def test_sheet_tall_enough_for_layout(app):
    use = type("U", (), {"SETTINGS": {"InstalledInterpreters": [sys.executable]}})()
    sheet = SetRunParameters(_settings(), {"venvdir": "/tmp/venv"}, use)
    sheet.show()
    app.processEvents()
    assert sheet.height() >= sheet.layout().minimumSize().height()
    assert sheet.sizeHint().height() >= sheet.layout().minimumSize().height()


def test_no_control_overlaps(app):
    use = type("U", (), {"SETTINGS": {"InstalledInterpreters": [sys.executable]}})()
    sheet = SetRunParameters(_settings(), {"venvdir": "/tmp/venv"}, use)
    sheet.show()
    app.processEvents()

    controls = [
        w for w in (
            list(sheet.findChildren(QLabel))
            + list(sheet.findChildren(QComboBox))
            + list(sheet.findChildren(QCheckBox))
            + list(sheet.findChildren(QSpinBox))
        )
        if w is not sheet and w.isVisible() and w.geometry().isValid()
    ]
    for i, a in enumerate(controls):
        for b in controls[i + 1:]:
            if a.isAncestorOf(b) or b.isAncestorOf(a):
                continue
            assert not a.geometry().intersects(b.geometry()), (
                f"{a.__class__.__name__}:{getattr(a, 'text', lambda: '')()} "
                f"{a.geometry()} overlaps "
                f"{b.__class__.__name__} {b.geometry()}"
            )
