"""Git panel empty-state and initialize UX."""

import os
import shutil
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from Extensions.BottomWidgets.GitPanel import GitPanel  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_no_project_empty_state(app):
    panel = GitPanel({"sourcedir": ""})
    assert not panel.emptyState.isHidden()
    assert panel.repoChrome.isHidden()
    assert panel.emptyTitle.text() == "No project open"
    assert panel.initButton.isHidden()


def test_non_repo_shows_init(app, tmp_path):
    if not shutil.which("git"):
        pytest.skip("git not on PATH")
    panel = GitPanel({"sourcedir": str(tmp_path)})
    assert not panel.emptyState.isHidden()
    assert panel.repoChrome.isHidden()
    assert panel.emptyTitle.text() == "No Git repository"
    assert not panel.initButton.isHidden()
    assert panel.initButton.isEnabled()
    assert panel.emptyRefreshButton.isEnabled()
    assert panel.actionsButton.isHidden() or not panel.actionsButton.isEnabled()
    assert not panel.stageAction.isEnabled()


def test_initialize_repo(app, tmp_path, monkeypatch):
    if not shutil.which("git"):
        pytest.skip("git not on PATH")
    panel = GitPanel({"sourcedir": str(tmp_path)})
    monkeypatch.setattr(
        QMessageBox, "question",
        lambda *a, **k: QMessageBox.StandardButton.Yes)

    panel.initialize_repo()
    assert panel.worker.wait(10000)
    app.processEvents()
    # Allow follow-up refresh batch to finish.
    if panel.worker.isRunning():
        panel.worker.wait(10000)
    for _ in range(20):
        app.processEvents()

    assert os.path.isdir(os.path.join(str(tmp_path), ".git"))
    assert not panel.repoChrome.isHidden()
    assert panel.emptyState.isHidden()
    assert panel.refreshButton.isEnabled()
