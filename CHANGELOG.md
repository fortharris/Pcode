# Changelog

## Unreleased

### Workflow
- Run arguments are split with `shlex` (quoted paths work); profiler forwards args too
- Go-to-Definition runs on a background thread
- Project venv install/upgrade runs off the UI thread with a progress dialog
- Quick Open (Ctrl+P) fuzzy file finder; Print default shortcut moved to Ctrl+Alt+P
- Git panel: Fetch / Pull / Push (async, 120s timeout)
- Encoding-aware save (honors `codingFormat`, falls back to UTF-8)
- Search find options relabeled (Case / Word / Regex / Wrap); broader accessible names
- Assistant context menu: removed unfinished “Fix Selected/All Occurrences” stubs
- **Thin DAP debugger**: Debug run attaches to debugpy, applies margin/Alt+B breakpoints, Continue/Step controls (F5/F10/F11)
- General Settings UX: two-column layout, Appearance first, radios for completion, filter box, clearer labels

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
- Color scheme / lexer style files remain XML under the workspace `stylesdir` (editor format, unchanged)
- `font_metrics_width` → `Extensions/font_metrics.py`; QFileDialog helpers → `Extensions/file_dialog_utils.py`
- `qscintilla_compat.py` re-exposes QScintilla scoped enums for legacy flat names
- `qt_bindings.py` removed; migration peel scripts archived under `scripts/archive/`
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
