"""Git status panel with stage/commit and per-file diff."""

import os
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)


class GitPanel(QWidget):

    def __init__(self, project_path_dict, editor_tab_widget=None, parent=None):
        super().__init__(parent)
        self.root = project_path_dict.get("sourcedir", "")
        self.editor_tab = editor_tab_widget
        self._changed_files = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        toolbar = QHBoxLayout()
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.refresh)
        toolbar.addWidget(self.refreshButton)

        self.stageButton = QPushButton("Stage All")
        self.stageButton.clicked.connect(self.stage_all)
        toolbar.addWidget(self.stageButton)

        self.stageFileButton = QPushButton("Stage File")
        self.stageFileButton.clicked.connect(self.stage_selected)
        toolbar.addWidget(self.stageFileButton)

        self.diffButton = QPushButton("Diff at Cursor")
        self.diffButton.clicked.connect(self.diff_at_cursor)
        toolbar.addWidget(self.diffButton)

        self.unstageButton = QPushButton("Unstage File")
        self.unstageButton.clicked.connect(self.unstage_selected)
        toolbar.addWidget(self.unstageButton)

        self.openButton = QPushButton("Open File")
        self.openButton.clicked.connect(self.open_selected)
        toolbar.addWidget(self.openButton)

        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.fileList = QListWidget()
        self.fileList.setMaximumHeight(120)
        self.fileList.itemDoubleClicked.connect(self.open_selected)
        layout.addWidget(self.fileList)

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

    def _parse_status_files(self, status_text):
        files = []
        for line in status_text.splitlines():
            if line.startswith("##"):
                continue
            if len(line) < 4:
                continue
            code = line[:2]
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ")[-1]
            files.append((code, path))
        return files

    def refresh(self):
        if not self._is_repo():
            self.output.setPlainText(
                "Not a git repository.\n\n"
                "Initialize with: git init")
            self.stageButton.setEnabled(False)
            self.stageFileButton.setEnabled(False)
            self.commitButton.setEnabled(False)
            self.diffButton.setEnabled(False)
            self.fileList.clear()
            return
        self.stageButton.setEnabled(True)
        self.stageFileButton.setEnabled(True)
        self.commitButton.setEnabled(True)
        self.diffButton.setEnabled(True)
        code, branch = self._run_git("branch", "--show-current")
        _, status = self._run_git("status", "--short", "--branch")
        _, log = self._run_git("log", "-5", "--oneline", "--decorate")
        text = "Branch: {0}\n\n=== status ===\n{1}\n\n=== recent commits ===\n{2}".format(
            branch if code == 0 else "?", status, log)
        self.output.setPlainText(text)

        self._changed_files = self._parse_status_files(status)
        self.fileList.clear()
        for code, path in self._changed_files:
            item = QListWidgetItem("{0} {1}".format(code, path))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.fileList.addItem(item)

    def _selected_path(self):
        item = self.fileList.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def stage_selected(self):
        if not self._is_repo():
            return
        path = self._selected_path()
        if not path:
            self.output.appendPlainText("\n(select a changed file to stage)")
            return
        code, out = self._run_git("add", "--", path)
        self.output.appendPlainText("\n=== stage file ===\n" + out)
        if code == 0:
            self.refresh()

    def unstage_selected(self):
        if not self._is_repo():
            return
        path = self._selected_path()
        if not path:
            self.output.appendPlainText("\n(select a file to unstage)")
            return
        code, out = self._run_git("restore", "--staged", "--", path)
        self.output.appendPlainText("\n=== unstage file ===\n" + out)
        if code == 0:
            self.refresh()

    def open_selected(self):
        path = self._selected_path()
        if path is None and self.editor_tab is not None:
            path = self.editor_tab.getEditorData("filePath")
        if not path:
            return
        full = path if os.path.isabs(path) else os.path.join(self.root, path)
        if self.editor_tab is not None and os.path.isfile(full):
            self.editor_tab.loadfile(full)
        elif os.path.isfile(full):
            self.output.appendPlainText("\n(open in editor: {0})".format(full))
        else:
            self.output.appendPlainText("\n(file not found: {0})".format(full))

    def stage_all(self):
        if not self._is_repo():
            return
        code, out = self._run_git("add", "-A")
        self.output.appendPlainText("\n=== stage ===\n" + out)
        if code == 0:
            self.refresh()

    def diff_at_cursor(self):
        if not self._is_repo():
            return
        path = self._selected_path()
        if path is None and self.editor_tab is not None:
            path = self.editor_tab.getEditorData("filePath")
        if not path:
            self.output.appendPlainText("\n(no file selected for diff)")
            return
        code, out = self._run_git("diff", "--", path)
        self.output.appendPlainText(
            "\n=== diff: {0} ===\n{1}".format(path, out if code == 0 else out))

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
