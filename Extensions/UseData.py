import os
import sys
import re
import json
import codecs
import traceback
import logging

from PyQt6.Qsci import QsciScintilla
from Extensions.qt_bindings import QtCore, QtXml

from Extensions.Workspace import Workspace


def textEncoding(bb):
    """ Get the encoding used to encode a file.
    Accepts the bytes of the file. Returns the codec name. If the
    codec could not be determined, uses UTF-8.
    """

    # Get first two lines
    parts = bb.split(b'\n', 2)

    # Init to default encoding
    encoding = 'UTF-8'

    # Determine encoding from first two lines
    for i in range(len(parts) - 1):

        # Get line
        try:
            line = parts[i].decode('ASCII')
        except Exception:
            continue

        # Search for encoding directive

        # Has comment?
        if line and line[0] == '#':

            # Matches regular expression given in PEP 0263?
            expression = "coding[:=]\s*([-\w.]+)"
            result = re.search(expression, line)
            if result:

                # Is it a known encoding? Correct name if it is
                candidate_encoding = result.group(1)
                try:
                    c = codecs.lookup(candidate_encoding)
                    candidate_encoding = c.name
                except Exception:
                    pass
                else:
                    encoding = candidate_encoding

    # Done
    return encoding


def lineEnding(text):
    c_win = text.count("\r\n")
    c_mac = text.count("\r") - c_win
    c_lin = text.count("\n") - c_win

    if c_win > c_mac and c_win > c_lin:
        mode = QsciScintilla.EolWindows
    elif c_mac > c_win and c_mac > c_lin:
        mode = QsciScintilla.EolMac
    else:
        mode = QsciScintilla.EolUnix

    return mode


class FindInstalledPython(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    # Find all python executables

    def python_executables(self):
        try:
            found = []
            ext = ''
            searchpath = os.environ.get("PATH", "").split(os.pathsep)
            if sys.platform.startswith("win"):
                ext = '.exe'
                for path in self.windows():
                    searchpath.insert(0, path)
                
                searchpath.insert(0, os.curdir)  # implied by Windows shell
            
            for i in range(len(searchpath)):
                dirName = searchpath[i]
                # On windows the dirName *could* be quoted, drop the quotes
                if sys.platform.startswith("win") and len(dirName) >= 2\
                   and dirName[0] == '"' and dirName[-1] == '"':
                    dirName = dirName[1:-1]
                absName = os.path.abspath(
                    os.path.normpath(os.path.join(dirName, 'python'+ext)))
                if os.path.isfile(absName) and not absName in found:
                    found.append(absName)
            
            # Done
            return found
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))

            return []

    def windows(self):

        import winreg

        versionList = []
        key = None
        # Open base key
        regkeys = (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE)
        for regkey in regkeys:
            base = winreg.ConnectRegistry(None, regkey)
            try:
                key = winreg.OpenKey(
                    base, 'SOFTWARE\\Python\\PythonCore', 0, winreg.KEY_READ)
                break
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(repr(traceback.format_exception(exc_type, exc_value,
                             exc_traceback)))

        if key is not None:
            # Get info about subkeys
            nsub, nval, modified = winreg.QueryInfoKey(key)

            # Query Python versions from registry
            
            for i in range(nsub):
                try:
                    # Get name and subkey
                    name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(
                        key, name + '\\InstallPath', 0, winreg.KEY_READ)
                    # Get install location and store
                    location = winreg.QueryValue(subkey, '')
                    versionList.append(os.path.normpath(location))
                    # Close
                    winreg.CloseKey(subkey)
                except Exception:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    logging.error(
                        repr(traceback.format_exception(exc_type, exc_value,
                                 exc_traceback)))

                # Close keys
                winreg.CloseKey(key)
                winreg.CloseKey(base)
        # Query Python versions from file system
        for rootname in ['C:/', 'C:/Program Files', 'C:/Program Files (x86)']:
            if not os.path.isdir(rootname):
                continue
            for dir_item in os.listdir(rootname):
                if dir_item.lower().startswith('python'):
                    path = os.path.normpath(os.path.join(rootname, dir_item))
                    if path not in versionList:
                        versionList.append(path)
        
        for path in versionList:
            yield path

class UseData(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

        # usedata lists
        self.SETTINGS = {}
        self.libraryDict = {}
        self.OPENED_PROJECTS = []
        self.supportedFileTypes = ["python", ".xml", ".css", ".html"]

        # default shortcuts
        self.DEFAULT_SHORTCUTS = {
            'Ide': {
                "Go-to-Line": "Alt+G",
                "New-File": "Ctrl+N",
                "Open-File": "Ctrl+O",
                "Save-File": "Ctrl+S",
                "Save-All": "Ctrl+Shift+S",
                "Print": "Ctrl+P",
                "Run-File": "F4",
                "Run-Project": "F5",
                "Build": "Ctrl+Shift+B",
                "Stop-Execution": "F6",
                "Fullscreen": "F8",
                "Find": "Ctrl+F",
                "Replace": "Ctrl+H",
                "Find-Next": "Ctrl+G",
                "Find-Previous": "Shift+F3",
                "Help": "F2",
                "Python-Manuals": "F1",
                "Split-Horizontal": "F10",
                "Split-Vertical": "F9",
                "Remove-Split": "F11",
                "Reload-File": "F7",
                "Change-Tab": "F12",
                "Change-Tab-Reverse": "Ctrl+Tab",
                "Change-Split-Focus": "Ctrl+M",
                "Fold-Code": "",
                "Snippets": "Ctrl+K",
                "Toggle-Indentation-Guide": "Alt+I",
                "Toggle-Breakpoint": "Alt+B",
                "Select-to-Matching-Brace": "",
                "Next-Bookmark": "",
                "Previous-Bookmark": "",
                "Comment": "Ctrl+E",
                "Uncomment": "Alt+E",
                "Show-Completion": "Ctrl+Space",
                },
            'Editor': {'Move-To-End-Of-Document': ['Ctrl+End', 2318],
                       'Zoom-Out': ['Ctrl+-', 2334],
                       'Extend-Rectangular-Selection-Left-One-Character': ['Alt+Shift+Left', 2428],
                       'Move-Down-One-Paragraph': ['Ctrl+]', 2413],
                       'Move-To-Start-Of-Document': ['Ctrl+Home', 2316],
                       'Extend-Selection-To-Start-Of-Display-Line': ['', 2346],
                       'De-indent-One-Level': ['Shift+Tab', 2328],
                       'Delete-Right-To-End-Of-Next-Word': ['', 2518],
                       'Extend-Selection-Down-One-Line': ['Shift+Down', 2301],
                       'Scroll-Vertically-To-Centre-Current-Line': ['', 2619],
                       'Toggle-Insert-or-Overtype': ['Ins', 2324],
                       'Extend-Rectangular-Selection-Up-One-Line': ['Alt+Shift+Up', 2427],
                       'Extend-Rectangular-Selection-Down-One-Line': ['Alt+Shift+Down', 2426],
                       'Extend-Selection-Left-One-Character': ['Shift+Left', 2305],
                       'Select-All': ['Ctrl+A', 2013],
                       'Convert-Selection-To-Upper-Case': ['Ctrl+Shift+U', 2341],
                       'Insert-Newline': ['Return', 2329],
                       'Move-Right-One-Word-Part': ['Ctrl+\\', 2392],
                       'Move-To-First-Visible-Character-In-Document-Line': ['Home', 2331],
                       'Extend-Rectangular-Selection-To-First-Visible-Character-In-Document-Line': ['Alt+Shift+Home', 2431],
                       'Extend-Selection-Down-One-Page': ['Shift+PgDown', 2323],
                       'Move-Selected-Lines-Down-One-Line': ['', 2621],
                       'Move-Right-One-Word': ['Ctrl+Right', 2310],
                       'Move-Up-One-Page': ['PgUp', 2320],
                       'Extend-Rectangular-Selection-To-Start-Of-Document-Line': ['', 2430],
                       'Extend-Selection-Left-One-Word': ['Ctrl+Shift+Left', 2309],
                       'Scroll-View-Down-One-Line': ['Ctrl+Down', 2342],
                       'Extend-Selection-Left-One-Word-Part': ['Ctrl+Shift+/', 2391],
                       'Duplicate-Selection': ['Ctrl+D', 2469],
                       'Cut-Selection': ['Ctrl+X', 2177],
                       'Extend-Selection-Down-One-Paragraph': ['Ctrl+Shift+]', 2414],
                       'Extend-Selection-To-End-Of-Previous-Word': ['', 2440],
                       'Extend-Selection-To-Start-Of-Document-Line': ['', 2313],
                       'Move-Selected-Lines-Up-One-Line': ['', 2620],
                       'Stuttered-Move-Up-One-Page': ['', 2435],
                       'Extend-Selection-Right-One-Character': ['Shift+Right', 2307],
                       'Cancel': ['Esc', 2325],
                       'Scroll-View-Up-One-Line': ['Ctrl+Up', 2343],
                       'Cut-Current-Line': ['Ctrl+L', 2337],
                       'Stuttered-Extend-Selection-Down-One-Page': ['', 2438],
                       'Extend-Selection-To-End-Of-Display-Or-Document-Line': ['', 2452],
                       'Move-Up-One-Paragraph': ['Ctrl+[', 2415],
                       'Move-Left-One-Word': ['Ctrl+Left', 2308],
                       'Formfeed': ['', 2330],
                       'Undo-Last-Command': ['Ctrl+Z', 2176],
                       'Delete-Line-To-Left': ['Ctrl+Shift+Backspace', 2395],
                       'Delete-Word-To-Left': ['Ctrl+Backspace', 2335],
                       'Extend-Rectangular-Selection-To-End-Of-Document-Line': ['Alt+Shift+End', 2432],
                       'Move-To-End-Of-Display-Or-Document-Line': ['', 2451],
                       'Delete-Current-Character': ['Del', 2180],
                       'Stuttered-Move-Down-One-Page': ['', 2437],
                       'Move-Right-One-Character': ['Right', 2306],
                       'Move-To-End-Of-Previous-Word': ['', 2439],
                       'Extend-Selection-To-First-Visible-Character-In-Document-Line': ['Shift+Home', 2332],
                       'Move-Down-One-Line': ['Down', 2300],
                       'Scroll-To-Start-Of-Document': ['', 2628],
                       'Extend-Selection-To-Start-Of-Display-Or-Document-Line': ['', 2450],
                       'Move-Down-One-Page': ['PgDown', 2322],
                       'Move-To-End-Of-Document-Line': ['End', 2314],
                       'Delete-Word-To-Right': ['Ctrl+Del', 2336],
                       'Convert-Selection-To-Lower-Case': ['Ctrl+U', 2340],
                       'Extend-Selection-Up-One-Paragraph': ['Ctrl+Shift+[', 2416],
                       'Move-Up-One-Line': ['Up', 2302],
                       'Extend-Selection-To-Start-Of-Document': ['Ctrl+Shift+Home', 2317],
                       'Delete-Current-Line': ['Ctrl+Shift+L', 2338],
                       'Paste': ['Ctrl+V', 2179],
                       'Extend-Selection-Right-One-Word-Part': ['Ctrl+Shift+\\', 2393],
                       'Extend-Selection-To-First-Visible-Character-In-Display-Or-Document-Line': ['', 2454],
                       'Extend-Selection-To-End-Of-Next-Word': ['', 2442],
                       'Move-Left-One-Character': ['Left', 2304],
                       'Redo-Last-Command': ['Ctrl+Y', 2011],
                       'Move-Left-One-Word-Part': ['Ctrl+/', 2390],
                       'Stuttered-Extend-Selection-Up-One-Page': ['', 2436],
                       'Delete-Line-To-Right': ['Ctrl+Shift+Del', 2396],
                       'Extend-Rectangular-Selection-Right-One-Character': ['Alt+Shift+Right', 2429],
                       'Transpose-Current-And-Previous-Lines': ['Ctrl+T', 2339],
                       'Indent-One-Level': ['Tab', 2327],
                       'Extend-Selection-Right-One-Word': ['Ctrl+Shift+Right', 2311],
                       'Copy-Selection': ['Ctrl+C', 2178],
                       'Extend-Selection-To-End-Of-Display-Line': ['', 2315],
                       'Extend-Selection-To-End-Of-Document-Line': ['Shift+End', 2315],
                       'Extend-Rectangular-Selection-Up-One-Page': ['Alt+Shift+PgUp', 2433],
                       'Extend-Rectangular-Selection-Down-One-Page': ['Alt+Shift+PgDown', 2434],
                       'Move-To-Start-Of-Document-Line': ['', 2312],
                       'Delete-Previous-Character': ['Backspace', 2326],
                       'Delete-Previous-Character-If-Not-At-Start-Of-Line': ['', 2344],
                       'Zoom-In': ['Ctrl++', 2333],
                       'Move-To-Start-Of-Display-Or-Document-Line': ['', 2349],
                       'Move-To-First-Visible-Character-Of-Display-In-Document-Line': ['', 2453],
                       'Extend-Selection-Up-One-Line': ['Shift+Up', 2303],
                       'Copy-Current-Line': ['Ctrl+Shift+T', 2455],
                       'Move-To-Start-Of-Display-Line': ['Alt+Home', 2345],
                       'Move-To-End-Of-Next-Word': ['', 2441],
                       'Duplicate-The-Current-Line': ['', 2404],
                       'Move-To-End-Of-Display-Line': ['Alt+End', 2347],
                       'Extend-Selection-To-End-Of-Document': ['Ctrl+Shift+End', 2319],
                       'Extend-Selection-Up-One-Page': ['Shift+PgUp', 2321],
                       'Scroll-To-End-Of-Document': ['', 2629]}
            }

        self.CUSTOM_SHORTCUTS = {'Ide': {}, 'Editor': {}}

        self.DEFAULT_SETTINGS = {
            "AutoCompletion": "Api",
            "EnableAutoCompletion": "True",
            "DynamicSearch": "True",
            "MarkSearchOccurrence": "True",
            "CallTips": "True",
            "ShowWhiteSpaces": "False",
            "ShowCaretLine": "True",
            "ShowLineNumbers": "True",
            "MatchBraces": "True",
            "EnableFolding": "True",
            "DocOnHover": "True",
            "MarkOperationalLines": "False",
            "ShowEdgeLine": "True",
            "EdgeColumn": "80",
            "EdgeMode": "Line",
            "LineWrap": "False",
            "WrapMode": "Word",
            "EnableAlerts": "True",
            "enableStyleGuide": "True",
            "EnableAssistance": "True",
            "UI": "Custom",
            "Theme": "Light",
            "SoundsEnabled": "False",
            "EditorStylePython": "Default",
            "EditorStyleXml": "Default",
            "EditorStyleHtml": "Default",
            "EditorStyleCss": "Default",
            "LastOpenedPath": QtCore.QDir().homePath(),
            "DefaultInterpreter": sys.executable,
        }

        # App-level bootstrap config (workspace pointer + run flags). Stored as
        # JSON; the legacy plain-text settings.ini is migrated on first run.
        self.BOOTSTRAP_FILE = "settings.json"
        self.LEGACY_BOOTSTRAP_FILE = "settings.ini"
        # Consolidated workspace data (settings, opened projects, completion
        # modules, keymap) lives in a single JSON file in the workspace; this
        # cache is populated by loadUseData().
        self._data = {}

        self.settings = self._loadBootstrap()

        self.loadAppData()
        self.loadUseData()

        self.SETTINGS["InstalledInterpreters"] = self.getPythonExecutables()

    def _loadBootstrap(self):
        """Load the app-level bootstrap config.

        Prefers ``settings.json``; falls back to (and migrates) the legacy
        ``settings.ini`` plain-text ``key=value`` file. Values are kept as
        strings so existing ``settings["firstRun"] == "True"`` comparisons
        elsewhere keep working.
        """
        bootstrap = {"workspace": None, "firstRun": "True", "running": "False"}
        if os.path.isfile(self.BOOTSTRAP_FILE):
            try:
                with open(self.BOOTSTRAP_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                bootstrap.update({k: str(v) for k, v in data.items()})
                return bootstrap
            except Exception:
                logging.error(traceback.format_exc())
        if os.path.isfile(self.LEGACY_BOOTSTRAP_FILE):
            try:
                with open(self.LEGACY_BOOTSTRAP_FILE, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or "=" not in line:
                            continue
                        key, value = line.split("=", 1)
                        bootstrap[key] = value
            except Exception:
                logging.error(traceback.format_exc())
        return bootstrap

    def _default_workspace_dir(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return os.path.join(repo_root, 'workspace', 'PcodeProjects')

    def _ensure_workspace_dirs(self, path):
        for sub in ('Snippets', 'Library', 'Projects',
                    os.path.join('Settings', 'ColorSchemes')):
            os.makedirs(os.path.join(path, sub), exist_ok=True)
        for lang in ('Python', 'Xml', 'Html', 'Css'):
            os.makedirs(os.path.join(path, 'Settings', 'ColorSchemes', lang),
                        exist_ok=True)

    def loadAppData(self):
        self.workspaceDir = self.settings.get("workspace")
        if self.workspaceDir in (None, "None", ""):
            self.workspaceDir = self._default_workspace_dir()
        # Always work with an absolute path: a relative workspace (e.g. one
        # persisted in settings.ini) otherwise propagates into every derived
        # path and makes rope build duplicated, non-existent project paths.
        self.workspaceDir = os.path.abspath(self.workspaceDir)
        if not os.path.exists(self.workspaceDir):
            zip_path = os.path.join("Resources", "PcodeProjects.zip")
            if os.path.isfile(zip_path):
                newWorkspace = Workspace()
                if newWorkspace.created:
                    self.workspaceDir = newWorkspace.path
                    self.settings["workspace"] = self.workspaceDir
                else:
                    sys.exit()
            else:
                self._ensure_workspace_dirs(self.workspaceDir)
                self.settings["workspace"] = self.workspaceDir
                self.saveSettings()
        self.appPathDict = {
            "logfile": os.path.join(self.workspaceDir, "LOG.txt"),
            "snippetsdir": os.path.join(self.workspaceDir, "Snippets"),
            "librarydir": os.path.join(self.workspaceDir, "Library"),
            "projectsdir": os.path.join(self.workspaceDir, "Projects"),
            "settingsdir": os.path.join(self.workspaceDir, "Settings"),
            "stylesdir": os.path.join(self.workspaceDir, "Settings", "ColorSchemes"),
            "datafile": os.path.join(self.workspaceDir, "Settings", "usedata.json"),
            # Legacy XML files, kept only so they can be migrated on first run.
            "usedata": os.path.join(self.workspaceDir, "Settings", "usedata.xml"),
            "modules": os.path.join(self.workspaceDir, "Settings", "modules.xml"),
            "keymap": os.path.join(self.workspaceDir, "Settings", "keymap.xml")
            }

    def _apply_default_settings(self):
        for key, value in self.DEFAULT_SETTINGS.items():
            self.SETTINGS.setdefault(key, value)
        self.loadKeymap()
        self.loadModulesForCompletion()

    def loadUseData(self):
        self._data = self._readWorkspaceData()

        settings = self._data.get("settings", {})
        if isinstance(settings, dict):
            self.SETTINGS.update(settings)

        for path in self._data.get("openedProjects", []):
            if os.path.exists(path):
                self.OPENED_PROJECTS.append(path)

        self._apply_default_settings()

    def _readWorkspaceData(self):
        """Return the consolidated workspace data dict.

        Reads ``usedata.json``; on first run (no JSON yet) it migrates the
        legacy ``usedata.xml`` / ``modules.xml`` / ``keymap.xml`` trio and
        writes the consolidated file.
        """
        datafile = self.appPathDict["datafile"]
        if os.path.isfile(datafile):
            try:
                with open(datafile, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logging.error(traceback.format_exc())
                return {}

        data = self._migrateLegacyXml()
        if data:
            self._dumpWorkspaceData(data)
        return data

    def _buildWorkspaceData(self):
        settings = {k: v for k, v in self.SETTINGS.items()
                    if k != "InstalledInterpreters"}
        return {
            "version": 1,
            "settings": settings,
            "openedProjects": list(self.OPENED_PROJECTS),
            "modules": self.libraryDict,
            "keymap": self.CUSTOM_SHORTCUTS,
        }

    def _dumpWorkspaceData(self, data):
        try:
            with open(self.appPathDict["datafile"], "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            logging.error(traceback.format_exc())

    def _saveWorkspaceData(self):
        """Persist the full in-memory state to the consolidated JSON file.

        All persisted state lives in memory, so every save is a complete,
        consistent dump; the individual save* methods are kept as thin
        wrappers so existing callers keep working.
        """
        self._dumpWorkspaceData(self._buildWorkspaceData())

    def saveModulesForCompletion(self):
        self._saveWorkspaceData()

    def loadModulesForCompletion(self):
        self.libraryDict = {}
        modules = self._data.get("modules", {})
        if not isinstance(modules, dict):
            return
        for moduleName, value in modules.items():
            try:
                itemList, use = list(value[0]), value[1]
            except Exception:
                continue
            self.libraryDict[moduleName] = [itemList, str(use)]

    def saveUseData(self):
        self._saveWorkspaceData()
        self.settings["running"] = 'False'
        self.saveSettings()

    def saveKeymap(self):
        self._saveWorkspaceData()

    def loadKeymap(self):
        import copy
        self.CUSTOM_SHORTCUTS = copy.deepcopy(self.DEFAULT_SHORTCUTS)
        if self.settings.get("firstRun") == "True":
            return
        keymap = self._data.get("keymap")
        if not isinstance(keymap, dict):
            return
        for group, mapping in keymap.items():
            if group not in self.CUSTOM_SHORTCUTS or not isinstance(mapping, dict):
                continue
            for name, value in mapping.items():
                if group == "Editor":
                    try:
                        self.CUSTOM_SHORTCUTS[group][name] = [value[0],
                                                              int(value[1])]
                    except Exception:
                        continue
                else:
                    self.CUSTOM_SHORTCUTS[group][name] = value

    # ------------------------------------------------------------------
    # Legacy (XML) migration helpers
    # ------------------------------------------------------------------

    def _migrateLegacyXml(self):
        """Build a consolidated data dict from the legacy XML files, if any."""
        data = {"version": 1, "settings": {}, "openedProjects": [],
                "modules": {}, "keymap": {}}
        found = False

        usedata = self._readLegacyUseDataXml()
        if usedata is not None:
            data["settings"], data["openedProjects"] = usedata
            found = True

        modules = self._readLegacyModulesXml()
        if modules is not None:
            data["modules"] = modules
            found = True

        keymap = self._readLegacyKeymapXml()
        if keymap is not None:
            data["keymap"] = keymap
            found = True

        return data if found else {}

    def _readLegacyXmlDocument(self, path):
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r") as f:
                dom_document = QtXml.QDomDocument()
                dom_document.setContent(f.read())
                return dom_document
        except Exception:
            logging.error(traceback.format_exc())
            return None

    def _readLegacyUseDataXml(self):
        dom_document = self._readLegacyXmlDocument(self.appPathDict["usedata"])
        if dom_document is None:
            return None
        settings = {}
        openedProjects = []
        node = dom_document.documentElement().firstChild()
        while node.isNull() is False:
            sub_node = node.toElement().firstChild()
            while sub_node.isNull() is False:
                sub_prop = sub_node.toElement()
                if node.nodeName() == "openedprojects":
                    openedProjects.append(sub_prop.text())
                elif node.nodeName() == "settings":
                    key, _, value = sub_prop.text().partition('=')
                    settings[key] = value
                sub_node = sub_node.nextSibling()
            node = node.nextSibling()
        return settings, openedProjects

    def _readLegacyModulesXml(self):
        dom_document = self._readLegacyXmlDocument(self.appPathDict["modules"])
        if dom_document is None:
            return None
        modules = {}
        node = dom_document.documentElement().firstChild()
        while node.isNull() is False:
            property = node.toElement()
            sub_node = property.firstChild()
            moduleName = node.nodeName()
            use = property.attribute('use')
            itemList = []
            while sub_node.isNull() is False:
                itemList.append(sub_node.toElement().text())
                sub_node = sub_node.nextSibling()
            modules[moduleName] = [itemList, use]
            node = node.nextSibling()
        return modules

    def _readLegacyKeymapXml(self):
        dom_document = self._readLegacyXmlDocument(self.appPathDict["keymap"])
        if dom_document is None:
            return None
        keymap = {}
        node = dom_document.documentElement().firstChild()
        while node.isNull() is False:
            group = node.nodeName()
            keymap[group] = {}
            sub_node = node.toElement().firstChild()
            while sub_node.isNull() is False:
                tag = sub_node.toElement()
                name = tag.tagName()
                shortcut = tag.attribute("shortcut")
                if group == "Editor":
                    try:
                        keymap[group][name] = [shortcut,
                                               int(tag.attribute("value"))]
                    except Exception:
                        pass
                else:
                    keymap[group][name] = shortcut
                sub_node = sub_node.nextSibling()
            node = node.nextSibling()
        return keymap

    def getLastOpenedDir(self):
        if os.path.exists(self.SETTINGS["LastOpenedPath"]):
            pass
        else:
            self.SETTINGS["LastOpenedPath"] = QtCore.QDir().homePath()
        return self.SETTINGS["LastOpenedPath"]

    def saveLastOpenedDir(self, path):
        if self.SETTINGS["LastOpenedPath"] == path:
            pass
        else:
            self.SETTINGS["LastOpenedPath"] = path

    def saveSettings(self):
        try:
            with open(self.BOOTSTRAP_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            logging.error(traceback.format_exc())

    def readFile(self, fileName):
        file = open(fileName, 'rb')
        bb = file.read()
        file.close()
        encoding = textEncoding(bb)

        file = open(fileName, 'r')
        text = file.read()
        file.close()

        ending = lineEnding(text)

        return text, encoding, ending

    def getPythonExecutables(self):
        pythonExecutables = FindInstalledPython()
        interpreters = pythonExecutables.python_executables()

        return interpreters
