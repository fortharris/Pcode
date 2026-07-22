"""Freeze the Pcode IDE itself with cx_Freeze (Windows primary target).

Produces:
  dist/ide/Pcode/          — runnable frozen tree (Pcode.exe + libs + Resources)
  dist/Pcode-<ver>-windows-x64.zip
  dist/Pcode-<ver>-windows-x64.msi  (when bdist_msi succeeds)

Usage (from repo root, with deps + cx_Freeze installed)::

    python scripts/freeze_ide.py
    python scripts/freeze_ide.py --skip-msi
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from Extensions.version import VERSION  # noqa: E402


EXCLUDE_RESOURCE_NAMES = {
    "Thumbs.db",
    "desktop.ini",
    ".DS_Store",
}


def _resource_include_files() -> list[tuple[str, str]]:
    """Copy Resources into the freeze tree, skipping junk and huge leftovers."""
    src_root = ROOT / "Resources"
    pairs: list[tuple[str, str]] = []
    for path in src_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in EXCLUDE_RESOURCE_NAMES:
            continue
        # Legacy cx_Freeze 4.x bases / initscripts are unused by the IDE freeze.
        rel = path.relative_to(src_root).as_posix()
        if rel.startswith("build/"):
            continue
        if rel.startswith("venv/"):
            continue
        pairs.append((str(path), str(Path("Resources") / path.relative_to(src_root))))
    return pairs


def _icon_path() -> str | None:
    ico = ROOT / "Resources" / "images" / "icon.ico"
    if ico.is_file():
        return str(ico)
    png = ROOT / "Resources" / "images" / "icon.png"
    if png.is_file():
        return str(png)
    return None


def _optional_packages() -> list[str]:
    packages = [
        "Extensions",
        "PyQt6",
        "PyQt6.Qsci",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.QtNetwork",
        "PyQt6.QtPrintSupport",
        "PyQt6.QtSvg",
        "rope",
        "pyflakes",
        "autopep8",
        "pycodestyle",
    ]
    try:
        import debugpy  # noqa: F401

        packages.append("debugpy")
    except ImportError:
        pass
    return packages


def _build_options() -> dict:
    packages = _optional_packages()
    excludes = [
        "tkinter",
        "test",
        "tests",
        "unittest",
        "pydoc",
        "doctest",
        "xmlrpc",
    ]
    options = {
        "build_exe": {
            "packages": packages,
            "excludes": excludes,
            "include_files": _resource_include_files(),
            "include_msvcr": True,
            "optimize": 0,
        },
        "bdist_msi": {
            # Stable upgrade GUID for Pcode Windows installer.
            "upgrade_code": "{A7C3E9F1-4B2D-4E8A-9C1F-6D5E8A2B3C4D}",
            "add_to_path": False,
            "initial_target_dir": r"[ProgramFiles64Folder]\Pcode",
            "summary_data": {
                "author": "Pcode",
                "comments": "Pcode Python IDE",
            },
        },
    }
    icon = _icon_path()
    if icon:
        options["bdist_msi"]["install_icon"] = icon
    return options


def _make_executable():
    from cx_Freeze import Executable

    icon = _icon_path()
    kwargs = {
        "script": str(ROOT / "Pcode.py"),
        "base": "gui",
        "target_name": "Pcode.exe",
        "shortcut_name": "Pcode",
        "shortcut_dir": "DesktopFolder",
        "copyright": "GPL-3.0-or-later",
    }
    if icon:
        kwargs["icon"] = icon
    return Executable(**kwargs)


def run_freeze(skip_msi: bool = False) -> Path:
    os.chdir(ROOT)
    # Fresh build dir avoids stale plugin DLL mixups across cx_Freeze versions.
    build_base = ROOT / "build" / "ide"
    dist_ide = ROOT / "dist" / "ide"
    if build_base.exists():
        shutil.rmtree(build_base)
    if dist_ide.exists():
        shutil.rmtree(dist_ide)

    from cx_Freeze import setup

    # cx_Freeze writes under build/ and dist/ relative to cwd.
    sys.argv = [
        "setup.py",
        "build_exe",
        f"--build-exe={dist_ide / 'Pcode'}",
    ]
    setup(
        name="Pcode",
        version=VERSION,
        description="Pcode — a lightweight Python IDE",
        options=_build_options(),
        executables=[_make_executable()],
    )

    exe_dir = dist_ide / "Pcode"
    exe = exe_dir / "Pcode.exe"
    if not exe.is_file():
        raise SystemExit(f"freeze failed: missing {exe}")

    zip_path = ROOT / "dist" / f"Pcode-{VERSION}-windows-x64.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in exe_dir.rglob("*"):
            if path.is_file():
                zf.write(path, Path("Pcode") / path.relative_to(exe_dir))
    print("wrote", zip_path)

    if not skip_msi:
        try:
            sys.argv = ["setup.py", "bdist_msi", f"--dist-dir={ROOT / 'dist'}"]
            setup(
                name="Pcode",
                version=VERSION,
                description="Pcode — a lightweight Python IDE",
                options=_build_options(),
                executables=[_make_executable()],
            )
            # Normalize MSI name if cx_Freeze used a different stem.
            msis = sorted(
                (ROOT / "dist").glob("*.msi"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            preferred = ROOT / "dist" / f"Pcode-{VERSION}-windows-x64.msi"
            if msis:
                newest = msis[0]
                if newest.resolve() != preferred.resolve():
                    if preferred.exists():
                        preferred.unlink()
                    newest.rename(preferred)
                print("wrote", preferred)
        except Exception as err:
            print("MSI build skipped/failed:", err)

    return exe_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-msi",
        action="store_true",
        help="Only build the portable tree + zip (faster local iteration).",
    )
    args = parser.parse_args(argv)

    try:
        import cx_Freeze  # noqa: F401
    except ImportError:
        print("cx_Freeze is required: pip install 'cx_Freeze>=6.15'", file=sys.stderr)
        return 1

    run_freeze(skip_msi=args.skip_msi)
    print("OK: frozen IDE at dist/ide/Pcode/Pcode.exe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
