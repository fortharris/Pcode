# Release checklist (0.2.0+)

Use this when cutting a Pcode release. Version source of truth:
`Extensions/version.py` and `pyproject.toml` (must match).

## Pre-tag

1. Confirm `CHANGELOG.md` has a dated `## x.y.z` section for the release.
2. Confirm About dialog / `VERSION` / README agree.
3. Capture GUI screenshots into `docs/screens/1.png` … `3.png`
   (`python scripts/capture_screenshots.py`).
4. Run locally:
   - `QT_QPA_PLATFORM=offscreen pytest`
   - `ruff check Extensions Pcode.py tests`
5. Optional: trigger GitHub Actions **freeze-smoke** / **freeze-smoke-windows**.
6. Build Windows IDE packages (local or CI **freeze-ide-windows**):
   - `python scripts/freeze_ide.py`
   - Expect `dist/Pcode-<ver>-windows-x64.zip` and `.msi`

## Tag and GitHub Release

```bash
git tag -a v0.2.0 -m "Pcode 0.2.0"
git push origin v0.2.0
gh release create v0.2.0 --title "Pcode 0.2.0" --notes-file CHANGELOG.md
```

Attach packages:

```bash
python -m build
gh release upload v0.2.0 dist/Pcode-*-windows-x64.zip dist/Pcode-*-windows-x64.msi dist/*.tar.gz dist/*.whl
```

## Notes

- Windows users can install via MSI or run the portable zip (`Pcode.exe`).
  Source install remains supported on all platforms.
- Frozen installs store the workspace under `%LOCALAPPDATA%\Pcode\PcodeProjects`.
- User projects can still be frozen with cx_Freeze via the in-app Build feature
  or `scripts/freeze_project.py`.
