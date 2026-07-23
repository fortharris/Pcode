"""Git status panel with branch/log, stage/commit/amend, and per-file diff.

Git I/O runs on a background QThread so the UI stays responsive.
"""

import os
import shutil
import subprocess

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMenu, QMessageBox, QPlainTextEdit, QPushButton, QSizePolicy, QToolButton,
    QVBoxLayout, QWidget,
)


def _run_git(root, *args, timeout=30):
    try:
        proc = subprocess.run(
            ["git", "-C", root] + list(args),
            capture_output=True, text=True, timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip() or "(no output)"
    except FileNotFoundError:
        return 127, "git is not installed or not on PATH."
    except Exception as err:
        return 1, str(err)


def _git_available():
    return shutil.which("git") is not None


class GitWorker(QThread):
    """Runs a batch of tagged git commands off the UI thread."""

    batchFinished = pyqtSignal(str, object)  # request_id, {tag: (code, out)}

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = ""
        self._commands = []
        self._request_id = ""
        self._timeout = 30

    def run_batch(self, request_id, root, commands, timeout=30):
        """Queue work. If already running, the caller should wait or skip."""
        self._request_id = request_id
        self._root = root
        self._commands = list(commands)
        self._timeout = timeout
        self.start()

    def run(self):
        results = {}
        for tag, args in self._commands:
            if tag == "checkout" and len(args) == 1:
                code, out = _run_git(
                    self._root, "switch", args[0], timeout=self._timeout)
                if code != 0:
                    code, out = _run_git(
                        self._root, "checkout", args[0], timeout=self._timeout)
                results[tag] = (code, out)
            else:
                results[tag] = _run_git(
                    self._root, *args, timeout=self._timeout)
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
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # --- Empty / no-repo state ---
        self.emptyState = QWidget()
        self.emptyState.setObjectName("gitEmptyState")
        empty_layout = QVBoxLayout(self.emptyState)
        empty_layout.setContentsMargins(24, 32, 24, 24)
        empty_layout.setSpacing(10)
        empty_layout.addStretch(1)

        self.emptyTitle = QLabel("No Git repository")
        self.emptyTitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.emptyTitle.setStyleSheet("font-size: 14px; font-weight: bold;")
        empty_layout.addWidget(self.emptyTitle)

        self.emptyDetail = QLabel()
        self.emptyDetail.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.emptyDetail.setWordWrap(True)
        self.emptyDetail.setEnabled(False)
        empty_layout.addWidget(self.emptyDetail)

        empty_actions = QHBoxLayout()
        empty_actions.addStretch(1)
        self.initButton = QPushButton("Initialize Repository")
        self.initButton.setAccessibleName("Initialize git repository")
        self.initButton.setToolTip(
            "Run git init in the project source folder")
        self.initButton.clicked.connect(self.initialize_repo)
        empty_actions.addWidget(self.initButton)
        self.emptyRefreshButton = QPushButton("Refresh")
        self.emptyRefreshButton.setAccessibleName("Refresh git status")
        self.emptyRefreshButton.setToolTip("Check again for a Git repository")
        self.emptyRefreshButton.clicked.connect(self.refresh)
        empty_actions.addWidget(self.emptyRefreshButton)
        empty_actions.addStretch(1)
        empty_layout.addLayout(empty_actions)
        empty_layout.addStretch(2)
        layout.addWidget(self.emptyState)

        # --- Active repo chrome ---
        self.repoChrome = QWidget()
        repo_layout = QVBoxLayout(self.repoChrome)
        repo_layout.setContentsMargins(0, 0, 0, 0)
        repo_layout.setSpacing(8)

        branch_row = QHBoxLayout()
        branch_label = QLabel("Branch:")
        branch_label.setAccessibleName("Git branch label")
        branch_row.addWidget(branch_label)
        self.branchBox = QComboBox()
        self.branchBox.setAccessibleName("Git branch")
        self.branchBox.setMinimumWidth(160)
        self.branchBox.activated.connect(self._checkout_branch)
        branch_row.addWidget(self.branchBox, 1)

        self.actionsButton = QToolButton()
        self.actionsButton.setText("Actions")
        self.actionsButton.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)
        self.actionsButton.setAccessibleName("Git actions")
        self.actionsButton.setToolTip("Stage, sync, and other Git actions")
        actions_menu = QMenu(self.actionsButton)
        self.stageAction = actions_menu.addAction(
            "Stage", self.stage_smart)
        self.stageAction.setToolTip(
            "Stage selected file, or all changes if none selected")
        self.unstageAction = actions_menu.addAction(
            "Unstage", self.unstage_selected)
        self.diffAction = actions_menu.addAction(
            "Diff", self.diff_at_cursor)
        actions_menu.addSeparator()
        self.fetchAction = actions_menu.addAction("Fetch", self.fetch)
        self.pullAction = actions_menu.addAction("Pull", self.pull)
        self.pushAction = actions_menu.addAction("Push", self.push)
        actions_menu.addSeparator()
        self.openFileAction = actions_menu.addAction(
            "Open File", self.open_selected)
        self.fullLogAction = actions_menu.addAction(
            "Full Log", self.show_log)
        self.actionsButton.setMenu(actions_menu)
        branch_row.addWidget(self.actionsButton)

        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setAccessibleName("Refresh git status")
        self.refreshButton.setToolTip("Refresh status, branches, and log")
        self.refreshButton.clicked.connect(self.refresh)
        branch_row.addWidget(self.refreshButton)
        repo_layout.addLayout(branch_row)

        self.statusLabel = QLabel()
        self.statusLabel.setAccessibleName("Git status")
        self.statusLabel.hide()
        repo_layout.addWidget(self.statusLabel)

        changes_label = QLabel("Changes")
        changes_label.setAccessibleName("Changed files label")
        repo_layout.addWidget(changes_label)
        self.fileList = QListWidget()
        self.fileList.setAccessibleName("Changed files")
        self.fileList.setMaximumHeight(100)
        self.fileList.itemDoubleClicked.connect(self.open_selected)
        repo_layout.addWidget(self.fileList)

        repo_layout.addWidget(QLabel("Recent commits"))
        self.logList = QListWidget()
        self.logList.setAccessibleName("Recent commits")
        self.logList.setMaximumHeight(100)
        self.logList.itemActivated.connect(self._show_commit)
        repo_layout.addWidget(self.logList)

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
        repo_layout.addLayout(commit_row)

        self.output = QPlainTextEdit()
        self.output.setAccessibleName("Git output")
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.output.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        repo_layout.addWidget(self.output)

        layout.addWidget(self.repoChrome)

        self.refresh()

    def _is_repo(self):
        return self.root and os.path.isdir(os.path.join(self.root, ".git"))

    def _show_empty_state(self, title, detail, can_init=False):
        self.emptyTitle.setText(title)
        self.emptyDetail.setText(detail)
        self.initButton.setVisible(can_init)
        self.initButton.setEnabled(can_init and not self._busy)
        self.emptyRefreshButton.setEnabled(bool(self.root) and not self._busy)
        self.emptyState.show()
        self.repoChrome.hide()

    def _show_repo_chrome(self):
        self.emptyState.hide()
        self.repoChrome.show()

    def _set_actions_enabled(self, enabled):
        for w in (
            self.commitButton, self.amendButton, self.branchBox,
            self.commitLine, self.actionsButton,
        ):
            w.setEnabled(enabled and not self._busy)
        for action in (
            self.stageAction, self.unstageAction, self.diffAction,
            self.fetchAction, self.pullAction, self.pushAction,
            self.openFileAction, self.fullLogAction,
        ):
            action.setEnabled(enabled and not self._busy)
        # Refresh stays available whenever we have a project root.
        can_refresh = bool(self.root) and not self._busy
        self.refreshButton.setEnabled(can_refresh)
        self.emptyRefreshButton.setEnabled(can_refresh)

    def _set_busy(self, busy, message=None):
        self._busy = busy
        if busy:
            self.statusLabel.setText(message or "Working\u2026")
            self.statusLabel.show()
            if self.emptyState.isVisible():
                self.emptyDetail.setText(message or "Working\u2026")
        else:
            self.statusLabel.hide()
            self.statusLabel.clear()
        can_refresh = bool(self.root) and not busy
        self.refreshButton.setEnabled(can_refresh)
        self.emptyRefreshButton.setEnabled(can_refresh)
        self.initButton.setEnabled(
            self.initButton.isVisible() and not busy and _git_available())
        if self._is_repo():
            self._show_repo_chrome()
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

    def _start_batch(self, kind, commands, follow_refresh=False, timeout=30,
                     busy_message=None):
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
        self._set_busy(True, busy_message or "Working\u2026")
        self.worker.run_batch(request_id, self.root, commands, timeout=timeout)

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
            if tag == "init":
                if code == 0:
                    self.refresh()
                else:
                    self._show_empty_state(
                        "Could not initialize",
                        out or "git init failed.",
                        can_init=_git_available())
                    self.output.setPlainText(out)
            else:
                self._show_repo_chrome()
                self.output.appendPlainText(
                    "\n=== {0} ===\n{1}".format(tag, out))
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
            self._present_non_repo()
            return

        self._show_repo_chrome()
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
            item = QListWidgetItem("No commits yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.logList.addItem(item)

        text = "Branch: {0}\n\n=== status ===\n{1}".format(
            current or "?", status)
        self.output.setPlainText(text)

        self._changed_files = self._parse_status_files(status)
        self.fileList.clear()
        if not self._changed_files:
            item = QListWidgetItem("No changed files")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.fileList.addItem(item)
        else:
            for file_code, path in self._changed_files:
                item = QListWidgetItem("{0} {1}".format(file_code, path))
                item.setData(Qt.ItemDataRole.UserRole, path)
                self.fileList.addItem(item)

    def _present_non_repo(self):
        self.fileList.clear()
        self.logList.clear()
        self.branchBox.clear()
        self.output.clear()
        self._set_actions_enabled(False)

        if not self.root:
            self._show_empty_state(
                "No project open",
                "Open a project to use Git here.",
                can_init=False)
            return

        if not _git_available():
            self._show_empty_state(
                "Git not found",
                "Install Git and ensure it is on PATH, then click Refresh.",
                can_init=False)
            return

        self._show_empty_state(
            "No Git repository",
            "This project folder is not a Git repository yet.\n"
            "Initialize to start tracking changes here:\n{0}".format(self.root),
            can_init=True)

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
        lines = [
            line for line in (out or "").splitlines()
            if line.strip() and line != "(no output)"
        ]
        if not lines:
            item = QListWidgetItem("No commits yet")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.logList.addItem(item)
            return
        for line in lines:
            item = QListWidgetItem(line)
            sha = line.split()[0]
            item.setData(Qt.ItemDataRole.UserRole, sha)
            self.logList.addItem(item)

    def refresh(self):
        if not self._is_repo():
            self._present_non_repo()
            return
        self._show_repo_chrome()
        self._start_batch("refresh", [
            ("branch", ("branch", "--show-current")),
            ("branches", ("branch", "--format=%(refname:short)")),
            ("status", ("status", "--short", "--branch")),
            ("log", ("log", "-20", "--oneline", "--decorate")),
        ])

    def initialize_repo(self):
        if not self.root:
            return
        if not _git_available():
            self._present_non_repo()
            return
        if self._is_repo():
            self.refresh()
            return
        reply = QMessageBox.question(
            self, "Initialize Git Repository",
            "Create a new Git repository in:\n\n{0}\n\nContinue?".format(
                self.root),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._start_batch(
            "action",
            [("init", ("init",))],
            busy_message="Initializing\u2026")

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

    def fetch(self):
        if not self._is_repo():
            return
        self._start_batch("action", [
            ("fetch", ("fetch", "--all", "--prune")),
        ], timeout=120, busy_message="Fetching\u2026")

    def pull(self):
        if not self._is_repo():
            return
        self._start_batch("action", [
            ("pull", ("pull", "--ff-only")),
        ], timeout=120, busy_message="Pulling\u2026")

    def push(self):
        if not self._is_repo():
            return
        reply = QMessageBox.question(
            self, "Git Push",
            "Push the current branch to its remote?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._start_batch("action", [
            ("push", ("push",)),
        ], timeout=120, busy_message="Pushing\u2026")
