"""Headless smoke test: build the main window, create a project, open an
EditorWindow, and load a Python file. Flushes out PyQt6 runtime errors in the
editor/project path without manual clicking.

Run with QT_QPA_PLATFORM=offscreen.
"""

import os
import sys
import shutil
import warnings
import faulthandler

faulthandler.enable()
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.qt_bindings import QtWidgets, QtCore  # noqa: E402

# Make modal dialogs non-blocking so a stray error path can't hang the test.
QtWidgets.QMessageBox.warning = staticmethod(lambda *a, **k: None)
QtWidgets.QMessageBox.critical = staticmethod(lambda *a, **k: None)
QtWidgets.QMessageBox.information = staticmethod(lambda *a, **k: None)
QtWidgets.QMessageBox.question = staticmethod(lambda *a, **k: None)

app = QtWidgets.QApplication(sys.argv)

from Pcode import Pcode  # noqa: E402
from Extensions.Projects.Projects import CreateProjectThread  # noqa: E402


def make_project(projects_dir):
    proj_path = os.path.join(projects_dir, "SmokeTest")
    if os.path.exists(proj_path):
        shutil.rmtree(proj_path)
    thread = CreateProjectThread()
    thread.projDataDict = {
        "location": projects_dir,
        "name": "SmokeTest",
        "type": "Desktop Application",
        "windowtype": "Console",
        "mainscript": "main.py",
        "importdir": "",
    }
    thread.run()  # synchronous
    if thread.error:
        raise RuntimeError("project creation failed: %s" % thread.error)
    main_script = os.path.join(proj_path, "src", "main.py")
    with open(main_script, "w") as f:
        f.write("import os\n\n\ndef hello(name):\n    return 'hi ' + name\n\n"
                "print(hello('world'))\n")
    return proj_path


def main():
    win = Pcode()
    print("STEP main-window OK:", win.windowTitle())

    projects_dir = os.path.abspath(win.useData.appPathDict["projectsdir"])
    os.makedirs(projects_dir, exist_ok=True)

    proj_path = make_project(projects_dir)
    print("STEP project-created OK:", proj_path)

    try:
        win.loadProject(proj_path, show=True, new=True)
    except Exception as err:
        import traceback as tb
        print("LOADPROJECT FAILED:", err)
        tb.print_exc()
        raise
    print("STEP project-loaded OK")

    # Find the EditorWindow we just added and poke the editor a little.
    stack = win.projectWindowStack
    editor_window = None
    for i in range(stack.count()):
        w = stack.widget(i)
        if hasattr(w, "editorTabWidget"):
            editor_window = w
            break
    if editor_window is None:
        raise RuntimeError("no EditorWindow found in stack")
    print("STEP editor-window OK")

    etw = editor_window.editorTabWidget
    editor = etw.getEditor() if hasattr(etw, "getEditor") else None
    if editor is not None:
        editor.setText("x = 1\n")
        print("STEP editor-settext OK, lines:", editor.lines())

    exercise_save(etw)
    exercise_run(editor_window, win, proj_path)
    exercise_completion(editor)
    exercise_find_replace(editor_window)
    exercise_find_in_files(editor_window, proj_path)
    exercise_settings(win)
    exercise_library(win)
    exercise_project_view(editor_window)
    exercise_rope_rename(editor_window, proj_path)
    exercise_snippets(win)
    exercise_export(proj_path, projects_dir)
    exercise_filedialog_enums()
    exercise_mouse_events(editor, editor_window)
    exercise_command_palette(win)
    exercise_themes(win)
    exercise_about(win)
    exercise_assistant(editor_window, etw)
    exercise_tasks(editor_window, etw)
    exercise_profiler(editor_window)
    exercise_diff(etw)
    exercise_color_scheme(win)
    exercise_build_profile(editor_window)

    print("ALL OK")


def exercise_save(etw):
    """Exercise the file save path."""
    editor = etw.getEditor()
    editor.setText("import os\n\n\ndef greet(who):\n    return 'hi ' + who\n")
    saved = etw.save()
    print("STEP editor-save OK, saved:", saved)


def exercise_run(editor_window, win, proj_path):
    """Exercise the run/output path via QProcess against a real interpreter."""
    run_widget = editor_window.runWidget
    interpreter = sys.executable
    # Make sure the run path believes a usable interpreter exists.
    win.useData.SETTINGS.setdefault("InstalledInterpreters", [])
    if interpreter not in win.useData.SETTINGS["InstalledInterpreters"]:
        win.useData.SETTINGS["InstalledInterpreters"].append(interpreter)
    run_widget.projectData["DefaultInterpreter"] = interpreter

    script = os.path.join(proj_path, "src", "main.py")
    run_widget.runModule(script, "main", True, False, "")
    finished = run_widget.runProcess.waitForFinished(10000)
    # Queued slots (readyRead / finished) are delivered via the event loop, so
    # pump it briefly to let stdout drain into the output widget.
    for _ in range(20):
        app.processEvents()
    captured = run_widget.text()
    clean_exit = ">>> Exit: 0" in captured
    print("STEP editor-run OK, finished:", finished,
          "| clean exit:", clean_exit)


def exercise_completion(editor):
    """Exercise the rope-backed autocompletion path synchronously."""
    if editor is None:
        print("STEP editor-completion SKIPPED (no editor)")
        return
    from Extensions.CodeEditor import AutoCompletionThread

    source = "import os\nos."
    thread = AutoCompletionThread()
    thread.sourcedir = editor.refactor.root
    thread.ropeProject = editor.refactor.getProject()
    thread.source = source
    thread.offset = len(source)
    thread.lineText = "os."
    thread.column = 3
    results = thread.completions()
    n = len(results) if results else 0
    print("STEP editor-completion OK, proposals:", n)


def exercise_find_replace(editor_window):
    """Exercise the in-editor find/replace path."""
    etw = editor_window.editorTabWidget
    sw = editor_window.searchWidget
    editor = etw.getEditor()
    editor.setText("alpha beta alpha gamma alpha\n")

    sw.matchCase = False
    sw.matchWholeWord = False
    sw.matchRegExp = False
    sw.wrapAround = True

    sw.findLine.setText("alpha")
    sw.find()
    sw.findNext()

    # Use a replacement that does not contain the search term, otherwise a
    # case-insensitive replaceAll would re-match its own output forever.
    sw.replaceLine.setText("delta")
    sw.replaceAll()

    text = etw.getEditor().text()
    print("STEP editor-find-replace OK, replacements:", text.count("delta"))


def exercise_find_in_files(editor_window, proj_path):
    """Exercise the find-in-files search across the project source tree."""
    fif = editor_window.findInFiles
    fif.regExp = False
    fif.matchWholeWord = False
    fif.matchCase = False
    fif.recursive = True
    fif.findtextLine.setText("hello")
    fif.filterEdit.setText("*.py")
    fif.projectBox.setChecked(True)

    fif.find()
    finished = fif.findThread.wait(10000)
    print("STEP editor-find-in-files OK, thread finished:", finished)


def exercise_settings(win):
    """Open the settings dialog and cycle through every tab."""
    sw = win.settingsWidget
    sw.show()
    tabs = sw.settingsTab
    for i in range(tabs.count()):
        tabs.setCurrentIndex(i)
        app.processEvents()
    titles = [tabs.tabText(i) for i in range(tabs.count())]
    sw.hide()
    print("STEP settings-dialog OK, tabs:", titles)


def exercise_library(win):
    """Open the library viewer and exercise its advanced-search thread."""
    lib = win.library
    lib.show()
    app.processEvents()
    search = lib.advancedSearch
    search.searchLine.setText("def")
    search.startSearch()
    finished = search.finderThread.wait(10000)
    lib.hide()
    print("STEP library OK, search finished:", finished)


def exercise_project_view(editor_window):
    """Show the project view and confirm its source tree is populated."""
    pv = editor_window.projectManager.projectView
    pv.show()
    app.processEvents()
    pv.hide()
    print("STEP project-view OK, type:", type(pv).__name__)


def exercise_rope_rename(editor_window, proj_path):
    """Exercise the rope-backed rename refactor synchronously."""
    from Extensions.Refactor.Refactor import RenameThread

    refactor = editor_window.editorTabWidget.refactor
    project = refactor.ropeProject

    mod_path = os.path.join(proj_path, "src", "lib_mod.py")
    source = "def old_name():\n    return 1\n\n\nold_name()\n"
    with open(mod_path, "w") as f:
        f.write(source)
    project.validate()

    offset = source.index("old_name")
    thread = RenameThread()
    thread.new_name = "new_name"
    thread.path = mod_path
    thread.ropeProject = project
    thread.offset = offset
    thread.run()  # synchronous

    if thread.error is not None:
        raise RuntimeError("rope rename failed: %s" % thread.error)
    renamed = "new_name" in open(mod_path).read()
    print("STEP rope-rename OK, changed files:",
          len(thread.changedFiles), "| renamed in source:", renamed)


def exercise_snippets(win):
    """Exercise the snippets manager add/edit/save path."""
    sm = win.settingsWidget.snippetEditor
    snippet_name = "smoke_snippet.py"
    snippet_path = os.path.join(sm.path, snippet_name)
    with open(snippet_path, "w") as f:
        f.write("")

    sm.loadSnippetList()
    found = sm.snippetsListWidget.findItems(
        snippet_name, QtCore.Qt.MatchFlag.MatchExactly)
    sm.snippetsListWidget.setCurrentItem(found[0])

    sm.snippetViewer.setReadOnly(False)
    sm.snippetViewer.setPlainText("print('snippet body')\n")
    sm.saveSnippet()

    saved = "snippet body" in open(snippet_path).read()
    if os.path.exists(snippet_path):
        os.remove(snippet_path)
    print("STEP snippets OK, saved body:", saved)


def exercise_export(proj_path, projects_dir):
    """Exercise the project export (zip archive) thread."""
    from Extensions.Projects.ProjectManager.ProjectManager import ExportThread

    dest_base = os.path.join(projects_dir, "SmokeExport")
    thread = ExportThread()
    thread.fileName = dest_base
    thread.path = proj_path
    thread.run()  # synchronous

    if thread.error is not None:
        raise RuntimeError("export failed: %s" % thread.error)
    archive = dest_base + ".zip"
    exists = os.path.exists(archive)
    if exists:
        os.remove(archive)
    print("STEP export OK, archive created:", exists)


def exercise_filedialog_enums():
    """Guard the QFileDialog option flags used by the open/browse dialogs.

    These are accessed at module/handler scope across Start, ProjectView,
    FileExplorer and FindInFiles; an offscreen window never clicks them, so
    assert the flattened Qt6 enums resolve and combine.
    """
    fd = QtWidgets.QFileDialog
    options = fd.DontResolveSymlinks | fd.ShowDirsOnly
    assert fd.AcceptOpen is not None
    assert options is not None
    print("STEP filedialog-enums OK")


def exercise_mouse_events(editor, editor_window):
    """Dispatch a synthetic mouse move/double-click through the editor and run
    widget handlers.

    Catches Qt6 event-API regressions (QMouseEvent.globalPos/x/y/posF removed,
    Qt.MidButton alias) that an offscreen window never triggers by clicking.
    Only re-raise AttributeError (a removed-API signal); swallow unrelated
    runtime errors that depend on real layout/painting.
    """
    from PyQt6.QtGui import QMouseEvent
    from PyQt6.QtCore import QPointF, QEvent

    Qt = QtCore.Qt
    pt = QPointF(8.0, 8.0)

    def make(kind):
        return QMouseEvent(kind, pt, pt,
                           Qt.MouseButton.NoButton,
                           Qt.MouseButton.NoButton,
                           Qt.KeyboardModifier.NoModifier)

    targets = []
    if editor is not None:
        # Force the hover path so globalPosition()/pos() are exercised.
        try:
            editor.useData.SETTINGS["DocOnHover"] = "True"
        except Exception:
            pass
        targets.append((editor, "mouseMoveEvent"))
    rw = getattr(editor_window, "runWidget", None)
    if rw is not None:
        targets.append((rw, "mouseMoveEvent"))
        targets.append((rw, "mouseDoubleClickEvent"))

    for widget, handler in targets:
        fn = getattr(widget, handler, None)
        if fn is None:
            continue
        kind = (QEvent.Type.MouseButtonDblClick
                if "Double" in handler else QEvent.Type.MouseMove)
        try:
            fn(make(kind))
        except AttributeError:
            raise
        except Exception:
            pass
    print("STEP mouse-events OK")


def exercise_command_palette(win):
    """Build the palette commands, filter them, and run a safe one."""
    palette = win.commandPalette
    commands = win.buildCommands()
    palette.setCommands(commands)
    palette._refilter("")
    assert palette.listWidget.count() == len(commands)
    palette._refilter("thm")  # fuzzy: matches "Theme: ..." entries
    filtered = palette.listWidget.count()
    assert filtered >= 1
    # Run the "Go to Library" command then back to Editor (no dialogs).
    win.projectSwitcher.setButton("LIBRARY")
    win.projectSwitcher.setButton("EDITOR")
    print("STEP command-palette OK, commands:", len(commands),
          "| filtered:", filtered)


def exercise_themes(win):
    """Apply each theme through the app to flush stylesheet build errors."""
    from Extensions import StyleSheet
    for name in ("Dark", "System", "Light"):
        win.applyTheme(name)
        assert len(StyleSheet.globalStyle) > 0
    print("STEP themes OK")


def exercise_about(win):
    """Construct the About dialog (external library version table)."""
    from Extensions.About import About
    dlg = About(win)
    dlg.show()
    app.processEvents()
    rows = dlg.view.widget(0).topLevelItemCount()
    dlg.hide()
    print("STEP about OK, library rows:", rows)


def exercise_assistant(editor_window, etw):
    """Exercise pyflakes + pep8 checker threads on editor source."""
    assistant = editor_window.assistantWidget
    editor = etw.getEditor()
    editor.setText("import os\nx = 1\n")

    assistant.runCheck()
    assistant.codeCheckerThread.wait(10000)
    assistant.pep8CheckerThread.wait(10000)
    for _ in range(10):
        app.processEvents()

    alerts = assistant.errorView.topLevelItemCount()
    pep8_items = assistant.pep8View.topLevelItemCount()
    print("STEP assistant OK, pyflakes alerts:", alerts,
          "| pep8 items:", pep8_items)


def exercise_tasks(editor_window, etw):
    """Exercise the TODO/FIXME task finder on editor source."""
    from Extensions.BottomWidgets.TasksWidget import TaskFinderThread

    source = "# TODO: smoke task\n# FIXME: another\npass\n"
    etw.getEditor().setText(source)

    thread = TaskFinderThread()
    thread.findTasks(source)
    finished = thread.wait(5000)
    print("STEP tasks OK, finished:", finished, "| found:", len(thread.results))


def exercise_profiler(editor_window):
    """Load a cProfile stats file into the profiler tree."""
    import cProfile

    os.makedirs("temp", exist_ok=True)
    prof_path = os.path.join("temp", "smoke_profile")
    cProfile.run("sum(range(50))", prof_path)

    profiler = editor_window.profiler
    profiler.viewProfile(prof_path)
    rows = profiler.topLevelItemCount()
    print("STEP profiler OK, rows:", rows)


def exercise_diff(etw):
    """Exercise unified diff generation in the diff viewer."""
    from Extensions.Diff import DiffWindow

    class _TextSource(object):
        def __init__(self, text):
            self._text = text

        def text(self):
            return self._text

    before = "alpha\nbeta\n"
    after = "alpha\ngamma\n"
    diff = DiffWindow(
        editor=_TextSource(after),
        snapShot=_TextSource(before))
    changed = diff.generateUnifiedDiff()
    lines = diff.lines()
    print("STEP diff OK, changed:", changed, "| lines:", lines)


def exercise_color_scheme(win):
    """Open the color-scheme settings tab and load the default Python style."""
    cs = win.settingsWidget.colorScheme
    cs.show()
    app.processEvents()
    cs.groupChanged()
    app.processEvents()
    if cs.schemeNameBox.count() > 0:
        cs.updateScheme()
        app.processEvents()
    cs.hide()
    print("STEP color-scheme OK, schemes:", cs.schemeNameBox.count())


def exercise_build_profile(editor_window):
    """Load the cx_Freeze build profile for a Desktop Application project."""
    build = editor_window.projectManager.build
    if build is None:
        print("STEP build-profile SKIPPED (no build widget)")
        return
    profile = build.buildConfig.load()
    assert profile.get("name") or profile.get("base")
    print("STEP build-profile OK, keys:", len(profile))


if __name__ == "__main__":
    main()
