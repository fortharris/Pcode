Pcode
=====

##  Python 3 IDE

Pcode seeks to simplify the process of development in python by means of:

1. A simple and intuitive UI ( Zero clutter )
1. Utilization of very powerful open source libraries
1. Implementation of carefully chosen features
1. Support for other file formats that commonly accompany python development

###  Features:
1. Builds source code into executable
1. Refactoring
1. Project Management
1. Go-to-Definition
1. Snippets
1. Support for syntax coloring for XML, HTML and CSS
1. Error Analysis
1. Pep8 checker and fixer
1. Auto-completion
1. Outline Explorer
1. Profiler
1. Find-in-Files/Replace
1. Code Library
1. Split Editor ( Horizontal and Vertical )
1. Command palette (Ctrl+Shift+P)
1. Quick Open file finder (Ctrl+P)
1. Git panel (status, branch, log, stage/commit/amend, fetch/pull/push)
1. Light/Dark/System UI themes (System follows OS; Default lexer follows theme tokens)
1. Etc.

### Install (0.2.0)

Pcode 0.2.0 is distributed as **source**. There is no standalone IDE installer yet.

```bash
pip install -r requirements.txt        # run from source
python Pcode.py

pip install -e .                       # optional: install the `pcode` command
pip install -e .[dev]                  # optional: pytest + ruff for development
QT_QPA_PLATFORM=offscreen pytest       # unit + smoke tests (headless)
```

See [RUN.md](RUN.md) for virtualenv setup, the headless smoke test, and troubleshooting.
See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for a short user guide.

Release notes: [GitHub Releases](https://github.com/fortharris/Pcode/releases).

### Dependencies:
1. Python 3.10+ ( for running programs )
1. PyQt6 and PyQt6-QScintilla ( if you are running from source — see [RUN.md](RUN.md) )

The previously-vendored libraries (`rope`, `pyflakes`, `autopep8`, `pycodestyle`,
`cx_Freeze`) are now installed from PyPI via `requirements.txt`.

### From source & development

**PyQt6 branch (`pyside`):** production code uses direct `PyQt6` imports. Legacy
`Extensions/qt_bindings.py` has been removed. Color scheme / lexer definitions
under the workspace `stylesdir` remain XML (editor format).

**PR:** https://github.com/fortharris/Pcode/compare/master...pyside?expand=1

### License:
* GPL v3

### Latest version: 0.2.0 (PyQt6 / `pyside` branch)

Mailing List: [pcode-ide@googlegroups.com](https://groups.google.com/forum/#!forum/pcode-ide)

### Screenshots

Add GUI captures as `docs/screens/1.png` … `3.png` (see [docs/screens/README.md](docs/screens/README.md)).
