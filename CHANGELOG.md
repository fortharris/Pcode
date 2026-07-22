# Changelog

## Unreleased

### UX polish
- Shortcut collisions fixed: Split Horizontal/Remove remapped off F10/F11; debug F5/F10/F11 only while a debug session is active; Command Palette and Quick Open are remappable
- Busy overlay is non-modal (WindowModal `show`) with themed chrome; Escape cancels when Cancel is enabled
- Workspace first-run accepts any folder (or creates layout); clearer validation messages
- New Project Help dialog + field-level validation errors
- Bottom panels renamed Output→Run, Alerts→Assistant; Git Fetch/Pull/Push on the toolbar with busy status
- Theme tokens for busy overlay, splitter notifications, debug status, style editors, search borders
- Empty states for Messages, Tasks, Git file list, Quick Open, Command Palette
- Messages no longer steals the active bottom panel; badge + collapsed-pane flash only
- Quick Open explains when no project is open; View Editor/Snapshot/Diff in the command palette
- Cross-platform “Reveal in file manager”; Recent Files empty action disabled; Start page respects UI font scale
- Venv install/upgrade progress dialog is cancellable

### Workflow
- Run arguments are split with `shlex` (quoted paths work); profiler forwards args too
- Go-to-Definition runs on a background thread
- Project venvs are created with the selected base interpreter via
  `python -m venv` (with pip); Configure / Run / Build / rope share path helpers
- Enabling **Use virtual environment** requires an installed project venv first
- Quick Open skips `VirtualEnv` project trees
- Project venv install/upgrade runs off the UI thread with a progress dialog
- Quick Open (Ctrl+P) fuzzy file finder; Print default shortcut moved to Ctrl+Alt+P
- Git panel: Fetch / Pull / Push (async, 120s timeout)
- Encoding-aware save (honors `codingFormat`, falls back to UTF-8)
- Search find options relabeled (Case / Word / Regex / Wrap); broader accessible names
- Assistant context menu: removed unfinished “Fix Selected/All Occurrences” stubs
- **Thin DAP debugger**: Debug run attaches to debugpy, applies margin/Alt+B breakpoints, Continue/Step controls (F5/F10/F11)
- General Settings UX: two-column layout, Appearance first, radios for completion, filter box, clearer labels

### Migration cleanup
- Removed historical peel scripts (`scripts/archive/`)
- Documented color-scheme XML under `stylesdir` as intentional (editor format)
- Dropped unused `projectdata_xml` / `buildprofile_xml` / `ropeprofile_xml` path keys; kept `session_xml` for migrate-on-load
- Legacy XML **read** paths retained for one release cycle; XML writes already stopped

## 0.2.0

### Polish
- Central `Extensions/version.py` (`0.2.0`); About dialog stays in sync with `pyproject.toml`
- User Guide at `docs/USER_GUIDE.md`; Help → User Guide opens it; Check For Updates queries GitHub Releases
- Git panel I/O moved off the UI thread; toolbar slimmed (Stage / Unstage / Diff / More)
- Outline explorer uses `ast.parse` (async defs, annotated assigns); rope completion/doc threads coalesce pending work
- debugpy listens on `127.0.0.1:5678` only; external launchers require absolute paths and split args without a shell
- Start page refresh; tool-overlay stylesheet cleanup; UI Font Scale setting (75–150%) and accessible names on main chrome
- README install story clarified (source-only); broader ruff select set; legacy XML **read/migrate** kept for old workspaces
- Release checklist: `docs/RELEASE_CHECKLIST.md`

### Migration
- **PyQt6 migration complete** for production code — all `Extensions/` modules use direct PyQt6 imports
- Workspace and project settings migrate from XML to JSON on first load
- New projects write JSON only (`project.json`, `Data/*.json`, `Rope/profile.json`, `Build/profile.json`)
- Legacy XML manifests still **readable** for older projects; no longer written on save
- Color scheme / lexer style files remain XML under the workspace `stylesdir` (editor format, by design)
- `font_metrics_width` → `Extensions/font_metrics.py`; QFileDialog helpers → `Extensions/file_dialog_utils.py`
- `qscintilla_compat.py` re-exposes QScintilla scoped enums for legacy flat names
- `qt_bindings.py` removed
- JSON-only saves for project/build/rope manifests (XML read-only for legacy projects)

### Features
- Command palette (Ctrl+Shift+P): build, rename symbol, close project, recent files, git amend/log
- Git panel: branch switcher, commit log list, amend, stage/unstage, commit, diff
- Assistant: progressive check updates, visible Cancel while pyflakes/pep8 run
- UI theme tokens drive Default lexer colours (paper/text/comment/keyword/string)
- CLI project freeze: `scripts/freeze_project.py`
- debugpy debug run type with optional wait-for-client; status bar indicator while listening

### Infrastructure
- pytest unit + smoke suites (including `test_no_shim_import`), ruff linting, GitHub Actions CI (Linux + Windows)
- cx_Freeze freeze smoke on `workflow_dispatch` (Linux and Windows)
- CI prepares `workspace/PcodeProjects/` before tests to avoid blocking on the workspace dialog
