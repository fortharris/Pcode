"""Qt font metrics helpers (PyQt4 ``width`` -> ``horizontalAdvance``)."""


def font_metrics_width(font_metrics, text):
    """Return the horizontal advance for *text* in *font_metrics*."""
    if hasattr(font_metrics, "horizontalAdvance"):
        return font_metrics.horizontalAdvance(text)
    return font_metrics.width(text)
