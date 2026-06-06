# Changelog

## Unreleased (pyside branch)

### Migration
- PyQt6 + PyQt6-QScintilla; `Extensions/qt_bindings.py` compat shim (peeling in progress)
- Workspace and project settings migrate from XML to JSON on first load
- New projects write `project.json`, `Data/projectdata.json`, `Data/session.json`, `Data/windata.json`, and `pyproject.toml`
- Legacy `project.xml` / `projectdata.xml` / `session.xml` still readable
- Rope profile JSON (`Rope/profile.json`) with XML mirror for compatibility
- Build profile JSON (`Build/profile.json`) with XML mirror for compatibility
- `EditorTabBar` extracted to `Extensions/editor_tab_bar.py`
- Peel `Outline`, `TasksWidget`, `MiniMap`, and `Diff` to direct PyQt6 imports
- Peel `editor_tab_bar`, snapshots, `tab_io`, build/project-manager dialogs, and profiler widgets to PyQt6
- Peel `Assistant`, `RunWidget`, and `Refactor` to direct PyQt6 imports
- Peel `EditorTabWidget`, `CodeEditor`, `TextEditor`, `BaseScintilla`, and settings stack to PyQt6
- Peel `Projects`, `ConfigureProject`, `ProjectView`, `Library`, and persistence modules to PyQt6
- Peel `EditorWindow`, `FindInFiles`, `FileExplorer`, and `screen_utils` to direct PyQt6 imports
- `font_metrics_width` and QFileDialog helpers extracted; production code no longer imports `qt_bindings`
- `qt_bindings` retained as a test-only PyQt4-compat shim (`tests/test_qt_bindings.py`)
- `test_no_shim_import` guards against hidden shim dependencies in the editor/project path

### Features
- Command palette (Ctrl+Shift+P) with fuzzy multi-token filter, keymap entries, project switching
- Git panel: status, stage/unstage per file, diff, open file in editor
- debugpy debug run type with optional wait-for-client; status bar indicator while listening
- Assistant debounce and cancellation when switching tabs

### Infrastructure
- pytest unit + smoke suites, ruff linting, GitHub Actions CI
- cx_Freeze freeze smoke available via `workflow_dispatch` only
