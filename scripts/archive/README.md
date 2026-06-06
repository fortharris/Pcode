# Archived migration scripts

One-off helpers used during the PyQt4 → PyQt6 peel. **Not used by the app or CI.**
Kept for reference only.

| Script | Purpose |
|--------|---------|
| `migrate_qt_imports.py` | Rewrite PyQt4 imports to `qt_bindings` |
| `peel_pyqt6_file.py` | Peel a single file to direct PyQt6 imports |
| `cleanup_peel_imports.py` | Remove duplicate import blocks after peeling |
| `fix_peeled_qtcore.py` | Post-peel Qt enum / signal fixes |
