"""Git status panel with branch/log, stage/commit/amend, and per-file diff.

Git I/O runs on a background QThread so the UI stays responsive.
"""

import os
import subprocess

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMenu, QPlainTextEdit, QPushButton, QToolButton, QVBoxLayout, QWidget,
)


def _run_git(root, *args):
    try:
        proc = subprocess.run(
            ["git", "-C", root] + list(args),
            capture_output=True, text=True, timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip() or "(no output)"
    except FileNotFoundError:
        return 127, "git is not installed or not on PATH."
    except Exception as err:
        return 1, str(err)


class GitWorker(QThread):
    """Runs a batch of tagged git commands off the UI thread."""

    batchFinished = pyqtSignal(str, object)  # request_id, {tag: (code, out)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = ""
        self._commands = []
        self._request_id = ""

    def run_batch(self, request_id, root, commands):
        """Queue work. If already running, the caller should wait or skip."""
        self._request_id = request_id
        self._root = root
        self._commands = list(commands)
        self.start()

    def run(self):
        results = {}
        for tag, args in self._commands:
            if tag == "checkout" and len(args) == 1:
                code, out = _run_git(self._root, "switch", args[0])
                if code != 0:
                    code, out = _run_git(self._root, "checkout", args[0])
                results[tag] = (code, out)
            else:
                results[tag] = _run_git(self._root, *args)
        self.batchFinished.emit(self._request_id, results)


class GitPanel(QWidget):

    def __init__(self, project_path_dict, editor_tab_widget=None, parent=None):
        super().__init__(parent)
        self.root = project_path_dict.get("sourcedir", "")
        self.editor_tab = editor_tab_widget
        self._changed_files = []
        self._refreshing_branches = False
        self._busy = False
        self._pending_refresh = False
        self._request_seq = 0

        self.worker = GitWorker(self)
        self.worker.batchFinished.connect(self._on_batch_finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        branch_row = QHBoxLayout()
        branch_label = QLabel("Branch:")
        branch_label.setAccessibleName("Git branch label")
        branch_row.addWidget(branch_label)
        self.branchBox = QComboBox()
        self.branchBox.setAccessibleName("Git branch")
        self.branchBox.setMinimumWidth(160)
        self.branchBox.activated.connect(self._checkout_branch)
        branch_row.addWidget(self.branchBox, 1)
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setAccessibleName("Refresh git status")
        self.refreshButton.setToolTip("Refresh status, branches, and log")
        self.refreshButton.clicked.connect(self.refresh)
        branch_row.addWidget(self.refreshButton)
        layout.addLayout(branch_row)

        toolbar = QHBoxLayout()
        self.stageButton = QPushButton("Stage")
        self.stageButton.setToolTip(
            "Stage selected file, or all changes if none selected")
        self.stageButton.setAccessibleName("Stage git changes")
        self.stageButton.clicked.connect(self.stage_smart)
        toolbar.addWidget(self.stageButton)

        self.unstageButton = QPushButton("Unstage")
        self.unstageButton.setToolTip("Unstage the selected file")
        self.unstageButton.setAccessibleName("Unstage selected file")
        self.unstageButton.clicked.connect(self.unstage_selected)
        toolbar.addWidget(self.unstageButton)

        self.diffButton = QPushButton("Diff")
        self.diffButton.setToolTip("Show diff for selected or current file")
        self.diffButton.setAccessibleName("Show git diff")
        self.diffButton.clicked.connect(self.diff_at_cursor)
        toolbar.addWidget(self.diffButton)

        self.moreButton = QToolButton()
        self.moreButton.setText("More")
        self.moreButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.moreButton.setAccessibleName("More git actions")
        more_menu = QMenu(self.moreButton)
        more_menu.addAction("Open File", self.open_selected)
        more_menu.addAction("Full Log", self.show_log)
        self.moreButton.setMenu(more_menu)
        toolbar.addWidget(self.moreButton)

        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.fileList = QListWidget()
        self.fileList.setAccessibleName("Changed files")
        self.fileList.setMaximumHeight(100)
        self.fileList.itemDoubleClicked.connect(self.open_selected)
        layout.addWidget(self.fileList)

        layout.addWidget(QLabel("Recent commits"))
        self.logList = QListWidget()
        self.logList.setAccessibleName("Recent commits")
        self.logList.setMaximumHeight(100)
        self.logList.itemActivated.connect(self._show_commit)
        layout.addWidget(self.logList)

        commit_row = QHBoxLayout()
        commit_row.addWidget(QLabel("Commit:"))
        self.commitLine = QLineEdit()
        self.commitLine.setAccessibleName("Commit message")
        self.commitLine.setPlaceholderText("Commit message")
        commit_row.addWidget(self.commitLine)
        self.commitButton = QPushButton("Commit")
        self.commitButton.setAccessibleName("Create commit")
        self.commitButton.clicked.connect(self.commit)
        commit_row.addWidget(self.commitButton)
        self.amendButton = QPushButton("Amend")
        self.amendButton.setAccessibleName("Amend last commit")
        self.amendButton.setToolTip(
            "Amend the last commit (uses message if set, else --no-edit)")
        self.amendButton.clicked.connect(self.amend)
        commit_row.addWidget(self.amendButton)
        layout.addLayout(commit_row)

        self.output = QPlainTextEdit()
        self.output.setAccessibleName("Git output")
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.output)

        self.refresh()

    def _is_repo(self):
        return self.root and os.path.isdir(os.path.join(self.root, ".git"))

    def _set_actions_enabled(self, enabled):
        for w in (
            self.stageButton, self.commitButton, self.diffButton,
            self.unstageButton, self.moreButton, self.amendButton,
            self.branchBox, self.refreshButton,
        ):
            w.setEnabled(enabled and not self._busy)

    def _set_busy(self, busy):
        self._busy = busy
        self.refreshButton.setEnabled(not busy)
        if self._is_repo():
            self._set_actions_enabled(True)
        else:
            self._set_actions_enabled(False)

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

    def _start_batch(self, kind, commands, follow_refresh=False):
        if not self.root:
            return
        if self.worker.isRunning():
            if kind == "refresh":
                self._pending_refresh = True
            return
        self._request_seq += 1
        request_id = "{0}:{1}".format(kind, self._request_seq)
        self._current_kind = kind
        self._follow_refresh = follow_refresh
        self._set_busy(True)
        self.worker.run_batch(request_id, self.root, commands)

    def _on_batch_finished(self, request_id, results):
        kind = request_id.split(":", 1)[0]
        self._set_busy(False)

        if kind == "refresh":
            self._apply_refresh(results)
        elif kind == "checkout":
            out = results.get("checkout", (1, ""))[1]
            name = getattr(self, "_checkout_name", "")
            self.output.appendPlainText(
                "\n=== checkout {0} ===\n{1}".format(name, out))
            self.refresh()
        elif kind == "action":
            tag = next(iter(results), "")
            code, out = results.get(tag, (1, ""))
            self.output.appendPlainText("\n=== {0} ===\n{1}".format(tag, out))
            if code == 0:
                if tag in ("commit", "amend"):
                    self.commitLine.clear()
                self.refresh()
        elif kind == "log":
            out = results.get("log", (1, ""))[1]
            self.output.appendPlainText("\n=== log ===\n" + out)
            self._populate_log_from_text(results.get("log", (1, ""))[1]
                                         if results.get("log", (1, ""))[0] == 0
                                         else "")
        elif kind == "show":
            sha = getattr(self, "_show_sha", "")
            out = results.get("show", (1, ""))[1]
            self.output.appendPlainText(
                "\n=== show {0} ===\n{1}".format(sha, out))
        elif kind == "diff":
            path = getattr(self, "_diff_path", "")
            code, out = results.get("diff", (1, ""))
            self.output.appendPlainText(
                "\n=== diff: {0} ===\n{1}".format(path, out))

        if self._pending_refresh:
            self._pending_refresh = False
            self.refresh()

    def _apply_refresh(self, results):
        if not self._is_repo():
            self.output.setPlainText(
                "Not a git repository.\n\n"
                "Initialize with: git init")
            self._set_actions_enabled(False)
            self.fileList.clear()
            self.logList.clear()
            self.branchBox.clear()
            return

        self._set_actions_enabled(True)
        branch_code, branch = results.get("branch", (1, ""))
        current = branch if branch_code == 0 else ""
        branches_code, branches_out = results.get("branches", (1, ""))
        branches = []
        if branches_code == 0:
            branches = [b.strip() for b in branches_out.splitlines() if b.strip()]
        self._populate_branches(current, branches)

        status_code, status = results.get("status", (1, ""))
        if status_code != 0:
            status = status or "(status failed)"
        log_code, log_out = results.get("log", (1, ""))
        if log_code == 0:
            self._populate_log_from_text(log_out)
        else:
            self.logList.clear()

        text = "Branch: {0}\n\n=== status ===\n{1}".format(
            current or "?", status)
        self.output.setPlainText(text)

        self._changed_files = self._parse_status_files(status)
        self.fileList.clear()
        for file_code, path in self._changed_files:
            item = QListWidgetItem("{0} {1}".format(file_code, path))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.fileList.addItem(item)

    def _populate_branches(self, current, branches):
        self._refreshing_branches = True
        self.branchBox.clear()
        if current and current not in branches and current != "(no output)":
            branches = [current] + list(branches)
        for name in branches:
            self.branchBox.addItem(name)
        if current:
            idx = self.branchBox.findText(current)
            if idx >= 0:
                self.branchBox.setCurrentIndex(idx)
        self._refreshing_branches = False

    def _populate_log_from_text(self, out):
        self.logList.clear()
        for line in (out or "").splitlines():
            if not line.strip() or line == "(no output)":
                continue
            item = QListWidgetItem(line)
            sha = line.split()[0]
            item.setData(Qt.ItemDataRole.UserRole, sha)
            self.logList.addItem(item)

    def refresh(self):
        if not self._is_repo():
            self.output.setPlainText(
                "Not a git repository.\n\n"
                "Initialize with: git init")
            self._set_actions_enabled(False)
            self.fileList.clear()
            self.logList.clear()
            self.branchBox.clear()
            return
        self._start_batch("refresh", [
            ("branch", ("branch", "--show-current")),
            ("branches", ("branch", "--format=%(refname:short)")),
            ("status", ("status", "--short", "--branch")),
            ("log", ("log", "-20", "--oneline", "--decorate")),
        ])

    def _checkout_branch(self, index):
        if self._refreshing_branches or not self._is_repo() or self._busy:
            return
        name = self.branchBox.itemText(index).strip()
        if not name:
            return
        self._checkout_name = name
        self._start_batch("checkout", [
            ("checkout", (name,)),
        ])

    def show_log(self):
        if not self._is_repo():
            return
        self._start_batch("log", [
            ("log", ("log", "-30", "--oneline", "--decorate", "--graph")),
        ])

    def _show_commit(self, item):
        if not self._is_repo() or item is None:
            return
        sha = item.data(Qt.ItemDataRole.UserRole)
        if not sha:
            return
        self._show_sha = sha
        self._start_batch("show", [
            ("show", ("show", "--stat", sha)),
        ])

    def _selected_path(self):
        item = self.fileList.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def stage_smart(self):
        if not self._is_repo():
            return
        path = self._selected_path()
        if path:
            self._start_batch("action", [
                ("stage file", ("add", "--", path)),
            ], follow_refresh=True)
        else:
            self._start_batch("action", [
                ("stage", ("add", "-A")),
            ], follow_refresh=True)

    def unstage_selected(self):
        if not self._is_repo():
            return
        path = self._selected_path()
        if not path:
            self.output.appendPlainText("\n(select a file to unstage)")
            return
        self._start_batch("action", [
            ("unstage file", ("restore", "--staged", "--", path)),
        ], follow_refresh=True)

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
        """Compatibility helper for command palette / smoke tests."""
        if not self._is_repo():
            return
        self._start_batch("action", [
            ("stage", ("add", "-A")),
        ], follow_refresh=True)

    def stage_selected(self):
        """Compatibility helper for older callers."""
        if not self._is_repo():
            return
        path = self._selected_path()
        if not path:
            self.output.appendPlainText("\n(select a changed file to stage)")
            return
        self._start_batch("action", [
            ("stage file", ("add", "--", path)),
        ], follow_refresh=True)

    def diff_at_cursor(self):
        if not self._is_repo():
            return
        path = self._selected_path()
        if path is None and self.editor_tab is not None:
            path = self.editor_tab.getEditorData("filePath")
        if not path:
            self.output.appendPlainText("\n(no file selected for diff)")
            return
        self._diff_path = path
        self._start_batch("diff", [
            ("diff", ("diff", "--", path)),
        ])

    def commit(self):
        if not self._is_repo():
            return
        message = self.commitLine.text().strip()
        if not message:
            self.output.appendPlainText("\n(commit message required)")
            return
        self._start_batch("action", [
            ("commit", ("commit", "-m", message)),
        ])

    def amend(self):
        if not self._is_repo():
            return
        message = self.commitLine.text().strip()
        if message:
            commands = [("amend", ("commit", "--amend", "-m", message))]
        else:
            commands = [("amend", ("commit", "--amend", "--no-edit"))]
        self._start_batch("action", commands)
