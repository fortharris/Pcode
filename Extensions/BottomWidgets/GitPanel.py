"""Git status panel with basic stage/commit actions."""

import os
import subprocess

from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QVBoxLayout, QWidget,
)


class GitPanel(QWidget):

    def __init__(self, project_path_dict, parent=None):
        super().__init__(parent)
        self.root = project_path_dict.get("sourcedir", "")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        toolbar = QHBoxLayout()
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.refresh)
        toolbar.addWidget(self.refreshButton)

        self.stageButton = QPushButton("Stage All")
        self.stageButton.clicked.connect(self.stage_all)
        toolbar.addWidget(self.stageButton)

        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        commit_row = QHBoxLayout()
        commit_row.addWidget(QLabel("Commit:"))
        self.commitLine = QLineEdit()
        self.commitLine.setPlaceholderText("Commit message")
        commit_row.addWidget(self.commitLine)
        self.commitButton = QPushButton("Commit")
        self.commitButton.clicked.connect(self.commit)
        commit_row.addWidget(self.commitButton)
        layout.addLayout(commit_row)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.output)

        self.refresh()

    def _run_git(self, *args):
        try:
            proc = subprocess.run(
                ["git", "-C", self.root] + list(args),
                capture_output=True, text=True, timeout=30,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            out = (proc.stdout or "") + (proc.stderr or "")
            return proc.returncode, out.strip() or "(no output)"
        except FileNotFoundError:
            return 127, "git is not installed or not on PATH."
        except Exception as err:
            return 1, str(err)

    def _is_repo(self):
        return self.root and os.path.isdir(os.path.join(self.root, ".git"))

    def refresh(self):
        if not self._is_repo():
            self.output.setPlainText(
                "Not a git repository.\n\n"
                "Initialize with: git init")
            self.stageButton.setEnabled(False)
            self.commitButton.setEnabled(False)
            return
        self.stageButton.setEnabled(True)
        self.commitButton.setEnabled(True)
        code, branch = self._run_git("branch", "--show-current")
        _, status = self._run_git("status", "--short", "--branch")
        _, log = self._run_git("log", "-5", "--oneline", "--decorate")
        text = "Branch: {0}\n\n=== status ===\n{1}\n\n=== recent commits ===\n{2}".format(
            branch if code == 0 else "?", status, log)
        self.output.setPlainText(text)

    def stage_all(self):
        if not self._is_repo():
            return
        code, out = self._run_git("add", "-A")
        self.output.appendPlainText("\n=== stage ===\n" + out)
        if code == 0:
            self.refresh()

    def commit(self):
        if not self._is_repo():
            return
        message = self.commitLine.text().strip()
        if not message:
            self.output.appendPlainText("\n(commit message required)")
            return
        code, out = self._run_git("commit", "-m", message)
        self.output.appendPlainText("\n=== commit ===\n" + out)
        if code == 0:
            self.commitLine.clear()
            self.refresh()
