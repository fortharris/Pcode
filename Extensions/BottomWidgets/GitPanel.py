"""Read-only git status panel for the project source tree."""

import os
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
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
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.output)

        self.refresh()

    def _run_git(self, *args):
        try:
            proc = subprocess.run(
                ["git", "-C", self.root] + list(args),
                capture_output=True, text=True, timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            out = (proc.stdout or "") + (proc.stderr or "")
            return proc.returncode, out.strip() or "(no output)"
        except FileNotFoundError:
            return 127, "git is not installed or not on PATH."
        except Exception as err:
            return 1, str(err)

    def refresh(self):
        if not self.root or not os.path.isdir(os.path.join(self.root, ".git")):
            self.output.setPlainText(
                "Not a git repository.\n\n"
                "Initialize with: git init")
            return
        code, branch = self._run_git("branch", "--show-current")
        _, status = self._run_git("status", "--short", "--branch")
        _, log = self._run_git("log", "-5", "--oneline", "--decorate")
        text = "Branch: {0}\n\n=== status ===\n{1}\n\n=== recent commits ===\n{2}".format(
            branch if code == 0 else "?", status, log)
        self.output.setPlainText(text)
