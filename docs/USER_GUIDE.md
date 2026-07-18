# Pcode User Guide

Pcode is a lightweight Python 3 IDE focused on a simple, low-clutter workflow:
create or open a project, edit, run, and optionally refactor or freeze a desktop
app.

## Install and run

**From source (recommended for 0.2.0):**

```bash
pip install -r requirements.txt
python Pcode.py
```

Optional editable install for the `pcode` command:

```bash
pip install -e .
pcode
```

See [RUN.md](../RUN.md) for virtualenv setup, tests, and troubleshooting.

There is no standalone IDE installer yet. Releases ship as source plus notes on
[GitHub Releases](https://github.com/fortharris/Pcode/releases).

## Getting started

1. Create a **New Project** (Desktop App or Package) or **Open Project**.
2. Edit files in the Editor page. Use the Outline sidebar to jump to classes
   and functions.
3. Run the current file or the project from the toolbar / Run panel.
4. Use **Ctrl+Shift+P** for the command palette (themes, git, build, etc.).

## Everyday features

| Feature | How |
|---------|-----|
| Find / Replace | Editor find bar; Find-in-Files in the bottom panel |
| Completions | Rope-based project completions (Settings → Auto-Completion) |
| Rename / refactor | Rope actions from the editor or palette |
| Lint / PEP8 | Assistant bottom panel (pyflakes + autopep8) |
| Git | Git bottom panel: status, branch, stage, commit, amend, diff |
| Debug | Run type **Debug** uses debugpy on `127.0.0.1:5678` |
| Freeze | Desktop Application projects → Build (cx_Freeze) |
| Themes | Settings → Theme (Light / Dark / System) |
| UI scale | Settings → UI Font Scale (accessibility) |

## Projects and data

Each project stores:

- `project.json` — name, type, main script
- `Data/projectdata.json` — favourites, recent files, run settings
- `Data/session.json` — open tabs and editor state

Legacy `*.xml` project files still open and migrate to JSON on load.

## Security notes

- **Debug** listens only on localhost (`127.0.0.1:5678`) for debugger attach.
- **External launchers** run programs you configure. Prefer absolute paths to
  trusted tools; parameters are passed as argument lists (not a shell).

## Help and updates

- **Help → User Guide** opens this document.
- **Help → Check For Updates** queries GitHub Releases for a newer tag.
- **Help → Python Manuals** opens the local Python documentation when installed.

Homepage: https://github.com/fortharris/Pcode
