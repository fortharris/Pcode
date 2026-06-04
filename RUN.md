# Running Pcode from source (Qt 6)

## Requirements

- Python 3.10+ (tested on 3.11)
- Windows: enable [long paths](https://pip.pypa.io/warnings/enable-long-paths) if installing Qt into the Store Python location fails

**Note:** The editor uses [QScintilla](https://www.riverbankcomputing.com/software/qscintilla/), which only ships official Python bindings for **PyQt6**, not PySide6. This migration uses **PyQt6** + `PyQt6-QScintilla`.

The repo’s top-level `venv/` folder is an app package, not Python’s stdlib `venv` module — create `.pcode-venv` from the **parent** directory (see below).

## Setup

From the repository root (not inside the `venv/` package folder):

```powershell
cd C:\Users\Harrison\Documents\GitHub\Pcode

# Create virtualenv from parent dir (repo has a `venv/` package that shadows stdlib venv)
cd ..
python -m venv Pcode\.pcode-venv
cd Pcode

.\.pcode-venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.pcode-venv\Scripts\python.exe Pcode.py
```

Or double-click `run.bat` (Windows).

On first run, a default workspace is created under `workspace/PcodeProjects/` when `settings.ini` has no valid workspace path.

## Troubleshooting

- **`No module named 'PySide6.Qsci'`** — use this branch’s `requirements.txt` (PyQt6-QScintilla), not PySide6 alone.
- **`python -m venv` fails** — run venv creation from the parent directory (see above).
- **Build / cx_Freeze** — vendored cx_Freeze 4.3 is legacy; desktop builds need a separate upgrade (not required to run the IDE).
