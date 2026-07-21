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
Release steps: [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

There is no standalone IDE installer yet. Releases ship as source plus notes on
[GitHub Releases](https://github.com/fortharris/Pcode/releases).

## Getting started

1. Create a **New Project** (Desktop App or Package) or **Open Project**.
2. Edit files in the Editor page. Use the Outline sidebar to jump to classes
   and functions.
3. Run the current file or the project from the toolbar / Run panel.
4. Use **Ctrl+P** for Quick Open (fuzzy file finder) and **Ctrl+Shift+P** for
   the command palette.

## Everyday features

| Feature | How |
|---------|-----|
| Quick Open | **Ctrl+P** — fuzzy find a file in the project |
| Find / Replace | Editor find bar (Case / Word / Regex / Wrap); Find-in-Files |
| Completions | Rope-based project completions (Settings → Auto-Completion) |
| Go to Definition | Refactor menu / palette (background rope lookup) |
| Rename / refactor | Rope actions from the editor or palette |
| Lint / PEP8 | Assistant bottom panel; context menu **Fix All Issues** |
| Git | Status, branch, stage, commit, amend, fetch, pull, push, diff |
| Run args | Quoted tokens supported, e.g. `--flag "my file"` |
| Debug | Run type **Debug** attaches via DAP; margin click / **Alt+B** sets breakpoints; **F5/F10/F11** continue/step |
| Freeze | Desktop Application projects → Build (cx_Freeze) |
| Themes | Settings → Theme (Light / Dark / System) |
| UI style | Settings → UI style: **Custom** (uses Theme) or **System** (OS light/dark + Pcode chrome) |
| Layout | Sidebar on the left; outline collapsed by default; thin toolbar with **⋯** overflow |
| UI scale | Settings → UI Font Scale (accessibility) |
| Print | Default shortcut **Ctrl+Alt+P** |

## Projects and data

Each project stores:

- `project.json` — name, type, main script
- `Data/projectdata.json` — favourites, recent files, run settings
- `Data/session.json` — open tabs and editor state

Files save with the detected encoding when possible; if that fails, Pcode falls
back to UTF-8 and updates the status bar coding label.

Legacy `*.xml` project files still open and migrate to JSON on load.

## Security notes

- **Debug** listens only on localhost (`127.0.0.1:5678`). In **Internal Console**
  mode, Pcode attaches as a DAP client, applies editor breakpoints, and offers
  Continue / Step Over / Into / Out. External Console mode still starts debugpy
  for attach from another tool.
- **External launchers** run programs you configure. Prefer absolute paths to
  trusted tools; parameters are passed as argument lists (not a shell).

## Help and updates

- **Help → User Guide** opens this document.
- **Help → Check For Updates** queries GitHub Releases for a newer tag.
- **Help → Python Manuals** opens the local Python documentation when installed.

Homepage: https://github.com/fortharris/Pcode
