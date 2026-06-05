# Running Pcode from source (Qt 6)

## Requirements

- Python 3.10+ (tested on 3.11)
- Windows: enable [long paths](https://pip.pypa.io/warnings/enable-long-paths) if installing Qt into the Store Python location fails

**Note:** The editor uses [QScintilla](https://www.riverbankcomputing.com/software/qscintilla/), which only ships official Python bindings for **PyQt6**, not PySide6. This migration uses **PyQt6** + `PyQt6-QScintilla`.

The repo’s top-level `Pvenv/` folder is the app’s virtual-environment builder (renamed from `venv/` to avoid shadowing Python’s stdlib `venv` module). Create `.pcode-venv` from the **parent** directory (see below).

## Setup

From the repository root (not inside the `venv/` package folder):

```powershell
cd C:\Users\Harrison\Documents\GitHub\Pcode

# Create virtualenv from parent dir (legacy `Pvenv/` package must not shadow stdlib venv)
cd ..
python -m venv Pcode\.pcode-venv
cd Pcode

.\.pcode-venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` installs PyQt6 + QScintilla and the previously-vendored
libraries (`rope`, `pyflakes`, `autopep8`, `pycodestyle`, `cx_Freeze`) from PyPI.

### Editable install / `pcode` entry point (optional)

```powershell
.\.pcode-venv\Scripts\python.exe -m pip install -e .
# then run from anywhere:
pcode
```

Optional extras: `pip install -e .[dev]` (pytest + ruff) and
`pip install -e .[build]` (cx_Freeze, for the in-app build/freeze feature).

## Run

```powershell
.\.pcode-venv\Scripts\python.exe Pcode.py
```

Or double-click `run.bat` (Windows).

On first run, a default workspace is created under `workspace/PcodeProjects/`
when there is no valid workspace path yet. Per-user config is stored as
`settings.json` (app bootstrap) and `workspace/.../Settings/usedata.json`
(settings, opened projects, completion modules, keymap). Legacy `settings.ini`
and the old `*.xml` config files are migrated automatically on first run.

### Project layout (new projects)

| File | Purpose |
|------|---------|
| `project.json` | Project manifest (name, type, main script) |
| `Data/projectdata.json` | Shortcuts, favourites, recent files, settings |
| `Data/session.json` | Open tabs, cursor, bookmarks, folds |
| `Data/windata.json` | Splitter and write-pad layout |
| `pyproject.toml` | Modern Python project metadata template |
| `src/main.py` | Hello-world entry script |

Older projects with `project.xml` / `projectdata.xml` / `session.xml` still open;
data is migrated to JSON on load where supported. Rope/build profiles remain XML
for now (`Rope/profile.xml`, `Build/profile.xml`).

## Tests

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.pcode-venv\Scripts\python.exe -m pytest          # fast unit tests
.\.pcode-venv\Scripts\python.exe scripts\exercise_editor.py   # headless smoke test (~40s with build)
.\.pcode-venv\Scripts\python.exe -m ruff check .    # lint
```

Set `PCODE_SKIP_BUILD=1` to skip the cx_Freeze build step in the smoke test (~30s saved).

CI runs unit + smoke tests on every push/PR. The full cx_Freeze freeze smoke runs
only when you manually trigger the **freeze-smoke** job via GitHub Actions
`workflow_dispatch`.

## Troubleshooting

- **`No module named 'PySide6.Qsci'`** — use this branch’s `requirements.txt` (PyQt6-QScintilla), not PySide6 alone.
- **`python -m venv` fails** — run venv creation from the parent directory (see above).
- **Build / cx_Freeze** — the build/freeze feature uses modern `cx_Freeze` (installed via `requirements.txt` or the `build` extra).
