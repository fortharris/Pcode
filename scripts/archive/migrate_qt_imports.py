#!/usr/bin/env python3
"""One-shot helper: rewrite PyQt4 imports to Extensions.qt_bindings."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"cx_Freeze", "rope", "pyflakes", "Xtra", "venv", "Resources", "scripts"}

IMPORT_RE = re.compile(
    r"^from PyQt4(?:\.Qsci import (.+)| import (.+))\s*$",
    re.MULTILINE,
)

QSCI_IMPORT = "from Extensions.qt_bindings import QtCore, QtGui\nfrom PyQt6.Qsci import {names}"

BINDINGS_IMPORT = "from Extensions.qt_bindings import {names}"


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "PyQt4" not in text:
        return False

    new_lines = []
    changed = False
    qsci_imports = []

    for line in text.splitlines(keepends=True):
        m = IMPORT_RE.match(line.rstrip("\n"))
        if m:
            changed = True
            if m.group(1):
                qsci_imports.append(m.group(1).strip())
                continue
            names = m.group(2).strip()
            if "QtXml" in names or "QtXml " in names:
                new_lines.append(BINDINGS_IMPORT.format(names=names) + "\n")
            else:
                new_lines.append(BINDINGS_IMPORT.format(names=names) + "\n")
            continue
        new_lines.append(line)

    if qsci_imports:
        names = ", ".join(qsci_imports)
        # merge duplicate qsci lines
        all_names = []
        for part in qsci_imports:
            all_names.extend(p.strip() for p in part.split(","))
        names = ", ".join(dict.fromkeys(all_names))
        insert = f"from PyQt6.Qsci import {names}\n"
        # insert after first bindings import
        out = "".join(new_lines)
        if "from Extensions.qt_bindings" in out and insert.strip() not in out:
            out = out.replace(
                "from Extensions.qt_bindings import",
                insert + "from Extensions.qt_bindings import",
                1,
            )
            changed = True
        else:
            new_lines.insert(0, insert)
            out = "".join(new_lines)
            changed = True
    else:
        out = "".join(new_lines)

    if not changed:
        return False

    # API mechanical fixes
    out = re.sub(
        r"\.setMargin\((\d+)\)",
        r".setContentsMargins(\1, \1, \1, \1)",
        out,
    )

    replacements = [
        (".exec_()", ".exec()"),
        (".exec_(", ".exec("),
        ("QtCore.pyqtSignal", "QtCore.Signal"),
        ("QtGui.QDesktopWidget().screenGeometry()",
         "primary_screen_geometry()"),
    ]
    for old, new in replacements:
        if old in out:
            out = out.replace(old, new)
            changed = True

    if "primary_screen_geometry()" in out and "primary_screen_geometry" not in out.split("def ")[0]:
        if "from Extensions.qt_bindings import" in out:
            if "primary_screen_geometry" not in out:
                out = out.replace(
                    "from Extensions.qt_bindings import",
                    "from Extensions.qt_bindings import primary_screen_geometry, ",
                    1,
                )

    if "fontMetrics().width(" in out or "fontMetrics.width(" in out:
        out = out.replace("self.fontMetrics().width(", "font_metrics_width(self.fontMetrics(), ")
        out = out.replace("self.fontMetrics.width(", "font_metrics_width(self.fontMetrics(), ")
        if "font_metrics_width" in out and "font_metrics_width," not in out and "import font_metrics_width" not in out:
            if "from Extensions.qt_bindings import" in out:
                out = out.replace(
                    "from Extensions.qt_bindings import",
                    "from Extensions.qt_bindings import font_metrics_width, ",
                    1,
                )

    path.write_text(out, encoding="utf-8")
    return True


def main():
    count = 0
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP for part in path.parts):
            continue
        if process_file(path):
            print(path.relative_to(ROOT))
            count += 1
    print(f"Updated {count} files")


if __name__ == "__main__":
    main()
