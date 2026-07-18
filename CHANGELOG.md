# Changelog

## Unreleased (pyside branch)

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
- Command palette (Ctrl+Shift+P) with fuzzy multi-token filter, keymap entries, project switching, git actions
- Git panel: status, stage/unstage per file, commit, diff, open file in editor
- debugpy debug run type with optional wait-for-client; status bar indicator while listening
- Assistant debounce and cancellation when switching tabs

### Infrastructure
- pytest unit + smoke suites (including `test_no_shim_import`), ruff linting, GitHub Actions CI (Linux + Windows)
- cx_Freeze freeze smoke on `workflow_dispatch` (Linux and Windows)
- CI prepares `workspace/PcodeProjects/` before tests to avoid blocking on the workspace dialog

### Post-merge checklist
- Manual GUI smoke on Windows (open project, edit, run, git panel)
- Trigger **CI → freeze-smoke** / **freeze-smoke-windows** via GitHub Actions `workflow_dispatch`
- Tag a release once merge is verified
- Optional follow-up: remove legacy XML *read* paths after a release cycle with JSON-only saves
