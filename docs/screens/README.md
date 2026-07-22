# Screenshots

Release gallery images for the README:

| File | Content |
|------|---------|
| `1.png` | Start page |
| `2.png` | Editor with a project open |
| `3.png` | General Settings |

Regenerate after theming or layout changes:

```bash
python scripts/capture_screenshots.py
```

(Uses a real display when available; `QT_QPA_PLATFORM=offscreen` works but may omit fonts.)
