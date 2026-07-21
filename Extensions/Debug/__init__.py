"""Debug helpers (breakpoints collection)."""

from Extensions.Debug.dap_client import DapClient

__all__ = ["DapClient", "collect_breakpoints"]


def collect_breakpoints(editor_tab_widget):
    """Return ``{absolute_path: [1-based lines]}`` for open editors."""
    result = {}
    if editor_tab_widget is None:
        return result
    for i in range(editor_tab_widget.count()):
        path = editor_tab_widget.getEditorData("filePath", i)
        if not path:
            continue
        editor = editor_tab_widget.getEditor(i)
        if not hasattr(editor, "getBreakpointLines"):
            continue
        lines = editor.getBreakpointLines()
        if lines:
            # Editor lines are 0-based; DAP wants 1-based.
            result[path] = [line + 1 for line in lines]
    return result
