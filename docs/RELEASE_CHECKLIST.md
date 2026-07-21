# Release checklist (0.2.0+)

Use this when cutting a Pcode release. Version source of truth:
`Extensions/version.py` and `pyproject.toml` (must match).

## Pre-tag

1. Confirm `CHANGELOG.md` has a dated `## x.y.z` section for the release.
2. Confirm About dialog / `VERSION` / README agree.
3. Capture GUI screenshots into `docs/screens/1.png` … `3.png`.
4. Run locally:
   - `QT_QPA_PLATFORM=offscreen pytest`
   - `ruff check Extensions Pcode.py tests`
5. Optional: trigger GitHub Actions **freeze-smoke** / **freeze-smoke-windows**.

## Tag and GitHub Release

```bash
git tag -a v0.2.0 -m "Pcode 0.2.0"
git push origin v0.2.0
gh release create v0.2.0 --title "Pcode 0.2.0" --notes-file CHANGELOG.md
```

Attach an sdist if desired:

```bash
python -m build
gh release upload v0.2.0 dist/*
```

## Notes

- 0.2.0 ships as **source** (`pip install -r requirements.txt` / `pip install -e .`).
  There is no standalone IDE installer yet.
- User projects can still be frozen with cx_Freeze via the in-app Build feature
  or `scripts/freeze_project.py`.
