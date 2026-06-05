# Changelog

## Unreleased (pyside branch)

### Migration
- PyQt6 + PyQt6-QScintilla; `Extensions/qt_bindings.py` compat shim (peeling in progress)
- Workspace and project settings migrate from XML to JSON on first load
- New projects write `project.json`, `Data/projectdata.json`, `Data/session.json`, `Data/windata.json`, and `pyproject.toml`
- Legacy `project.xml` / `projectdata.xml` / `session.xml` still readable
- Rope profile JSON (`Rope/profile.json`) with XML mirror for compatibility

### Features
- Command palette (Ctrl+Shift+P) with fuzzy multi-token filter, keymap entries, project switching
- Git panel: status, stage/unstage per file, diff, open file in editor
- debugpy debug run type with optional wait-for-client; status bar indicator while listening
- Assistant debounce and cancellation when switching tabs

### Infrastructure
- pytest unit + smoke suites, ruff linting, GitHub Actions CI
- cx_Freeze freeze smoke available via `workflow_dispatch` only
