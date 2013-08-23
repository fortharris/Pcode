import os
import sys
import re
import codecs
from PyQt4 import QtCore, QtGui, QtXml

from PyQt4.Qsci import QsciScintilla

from Extensions.Workspace import WorkSpace


def determineEncoding(bb):
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


def determineLineEnding(text):
    """ Get the line ending style used in the text.
    \n, \r, \r\n,
    The EOLmode is determined by counting the occurances of each
    line ending...
    """
    # test line ending by counting the occurances of each
    c_win = text.count("\r\n")
    c_mac = text.count("\r") - c_win
    c_lin = text.count("\n") - c_win
    # set the appropriate style
    if c_win > c_mac and c_win > c_lin:
        mode = QsciScintilla.EolWindows
    elif c_mac > c_win and c_mac > c_lin:
        mode = QsciScintilla.EolMac
    else:
        mode = QsciScintilla.EolUnix

    # return
    return mode


class PythonExecutables(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    # Find all python executables
    # todo: use new version that will probably be part of pyzolib

    def findPythonExecutables(self):
        if sys.platform.startswith('win'):
            return self.findPythonExecutables_win()
        else:
            return self.findPythonExecutables_posix()

    def findPythonExecutables_win(self):
        import winreg

        # Open base key
        base = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        try:
            key = winreg.OpenKey(
                base, 'SOFTWARE\\Python\\PythonCore', 0, winreg.KEY_READ)
        except Exception:
            return []

        # Get info about subkeys
        nsub, nval, modified = winreg.QueryInfoKey(key)

        # Query Python versions from registry
        versions = set()
        for i in range(nsub):
            try:
                # Get name and subkey
                name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(
                    key, name + '\\InstallPath', 0, winreg.KEY_READ)
                # Get install location and store
                location = winreg.QueryValue(subkey, '')
                versions.add(location)
                # Close
                winreg.CloseKey(subkey)
            except Exception:
                pass

        # Close keys
        winreg.CloseKey(key)
        winreg.CloseKey(base)

        # Query Python versions from file system
        for rootname in ['c:/', 'C:/program files/', 'C:/program files (x86)/']:
            if not os.path.isdir(rootname):
                continue
            for dname in os.listdir(rootname):
                if dname.lower().startswith('python'):
                    versions.add(os.path.join(rootname, dname))

        # Normalize all paths, and remove trailing backslashes
        versions = set([os.path.normcase(v).strip('\\') for v in versions])

        # Append "python.exe" and check if that file exists
        versions2 = []
        for dname in sorted(versions, key=lambda x: x[-2:]):
            exename = os.path.join(dname, 'python.exe')
            if os.path.isfile(exename):
                versions2.append(exename)

        # Done
        return versions2

    def findPythonExecutables_posix(self):
        found = []
        for searchpath in ['/usr/bin', '/usr/local/bin', '/opt/local/bin']:
            # Get files
            try:
                files = os.listdir(searchpath)
            except Exception:
                continue

            # Search for python executables
            for fname in files:
                if fname.startswith('python') and not fname.count('config'):
                    found.append(os.path.join(searchpath, fname))
        # Done
        return found


class UseData(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

        # usedata lists
        self.SETTINGS = {}
        self.OPENED_PROJECTS = []
        self.supportedFileTypes = ["python", ".xml", ".css", ".html"]

        # default shortcuts
        self.DEFAULT_SHORTCUTS = {
            'Ide': {
                "Go-to-Line": ["Alt+G", "Go to Line"],
                "New-File": ["Ctrl+N", "Create a New tab"],
                "Open-File": ["Ctrl+O", "Open a File"],
                "Save-File": ["Ctrl+S", "Save the current file"],
                "Save-All": ["Ctrl+Shift+S", "Save all filee"],
                "Print": ["Ctrl+P", "Print current file"],
                "Run-File": ["F4", "Execute current file"],
                "Run-Project": ["F5", "Execute current project"],
                "Build": ["Ctrl+Shift+B", "Build Project"],
                "Stop-Execution": ["F6", "Stop Execution"],
                "Fullscreen": ["F8", "Full Screen"],
                "Find": ["Ctrl+F", "Find"],
                "Replace": ["Ctrl+H", "Replace"],
                "Find-Next": ["Ctrl+G", "Find Next"],
                "Find-Previous": ["Shift+F3", "Find Previous"],
                "Help": ["F2", "Show Application Help"],
                "Python-Manuals": ["F1", "Python Manuals"],
                "Split-Horizontal": ["F10", "Split Tabs Horizontally"],
                "Split-Vertical": ["F9", "Split Tabs Vertically"],
                "Remove-Split": ["F11", "Remove Split"],
                "Reload-File": ["F7", "Reload File"],
                "Change-Tab": ["F12", "Change to the next Tab"],
                "Change-Tab-Reverse": ["Ctrl+Tab", "Change to the previous Tab"],
                "Change-Split-Focus": ["Ctrl+M", "Change the keyboard focus between the current splits"],
            },
            'Editor': {'Move-To-End-Of-Document': ['Ctrl+End', 'Move To End Of Document'],
                       'Zoom-Out': ['Ctrl+-', 'Zoom Out'],
                       'Extend-Rectangular-Selection-Left-One-Character': ['Alt+Shift+Left', 'Extend Rectangular Selection Left One Character'],
                       'Move-Down-One-Paragraph': ['Ctrl+]', 'Move Down One Paragraph'],
                       'Move-To-Start-Of-Document': ['Ctrl+Home', 'Move To Start Of Document'],
                       'Extend-Selection-To-Start-Of-Display-Line': ['', 'Extend Selection To Start Of Display Line'],
                       'De-indent-One-Level': ['Shift+Tab', 'De-indent One Level'],
                       'Delete-Right-To-End-Of-Next-Word': ['', 'Delete Right To End Of Next Word'],
                       'Extend-Selection-Down-One-Line': ['Shift+Down', 'Extend Selection Down One Line'],
                       'Scroll-Vertically-To-Centre-Current-Line': ['', 'Scroll Vertically To Centre Current Line'],
                       'Toggle-Insert-or-Overtype': ['Ins', 'Toggle Insert/overtype'],
                       'Extend-Rectangular-Selection-Up-One-Line': ['Alt+Shift+Up', 'Extend Rectangular Selection Up One Line'],
                       'Extend-Rectangular-Selection-Down-One-Line': ['Alt+Shift+Down', 'Extend Rectangular Selection Down One Line'],
                       'Extend-Selection-Left-One-Character': ['Shift+Left', 'Extend Selection Left One Character'],
                       'Select-All': ['Ctrl+A', 'Select All'],
                       'Convert-Selection-To-Upper-Case': ['Ctrl+Shift+U', 'Convert Selection To Upper Case'],
                       'Insert-Newline': ['Return', 'Insert Newline'],
                       'Move-Right-One-Word-Part': ['Ctrl+\\', 'Move Right One Word Part'],
                       'Move-To-First-Visible-Character-In-Document-Line': ['Home', 'Move To First Visible Character In Document Line'],
                       'Extend-Rectangular-Selection-To-First-Visible-Character-In-Document-Line': ['Alt+Shift+Home', 'Extend Rectangular Selection To First Visible Character In Document Line'],
                       'Extend-Selection-Down-One-Page': ['Shift+PgDown', 'Extend Selection Down One Page'],
                       'Move-Selected-Lines-Down-One-Line': ['', 'Move Selected Lines Down One Line'],
                       'Move-Right-One-Word': ['Ctrl+Right', 'Move Right One Word'],
                       'Move-Up-One-Page': ['PgUp', 'Move Up One Page'],
                       'Extend-Rectangular-Selection-To-Start-Of-Document-Line': ['', 'Extend Rectangular Selection To Start Of Document Line'],
                       'Extend-Selection-Left-One-Word': ['Ctrl+Shift+Left', 'Extend Selection Left One Word'],
                       'Scroll-View-Down-One-Line': ['Ctrl+Down', 'Scroll View Down One Line'],
                       'Extend-Selection-Left-One-Word-Part': ['Ctrl+Shift+/', 'Extend Selection Left One Word Part'],
                       'Duplicate-Selection': ['Ctrl+D', 'Duplicate Selection'],
                       'Cut-Selection': ['Ctrl+X', 'Cut Selection'],
                       'Extend-Selection-Down-One-Paragraph': ['Ctrl+Shift+]', 'Extend Selection Down One Paragraph'],
                       'Extend-Selection-To-End-Of-Previous-Word': ['', 'Extend Selection To End Of Previous Word'],
                       'Extend-Selection-To-Start-Of-Document-Line': ['', 'Extend Selection To Start Of Document Line'],
                       'Move-Selected-Lines-Up-One-Line': ['', 'Move Selected Lines Up One Line'],
                       'Stuttered-Move-Up-One-Page': ['', 'Stuttered Move Up One Page'],
                       'Extend-Selection-Right-One-Character': ['Shift+Right', 'Extend Selection Right One Character'],
                       'Cancel': ['Esc', 'Cancel'],
                       'Scroll-View-Up-One-Line': ['Ctrl+Up', 'Scroll View Up One Line'],
                       'Cut-Current-Line': ['Ctrl+L', 'Cut Current Line'],
                       'Stuttered-Extend-Selection-Down-One-Page': ['', 'Stuttered Extend Selection Down One Page'],
                       'Extend-Selection-To-End-Of-Display-Or-Document-Line': ['', 'Extend Selection To End Of Display Or Document Line'],
                       'Move-Up-One-Paragraph': ['Ctrl+[', 'Move Up One Paragraph'],
                       'Move-Left-One-Word': ['Ctrl+Left', 'Move Left One Word'],
                       'Formfeed': ['', 'Formfeed'],
                       'Undo-Last-Command': ['Ctrl+Z', 'Undo Last Command'],
                       'Delete-Line-To-Left': ['Ctrl+Shift+Backspace', 'Delete Line To Left'],
                       'Delete-Word-To-Left': ['Ctrl+Backspace', 'Delete Word To Left'],
                       'Extend-Rectangular-Selection-To-End-Of-Document-Line': ['Alt+Shift+End', 'Extend Rectangular Selection To End Of Document Line'],
                       'Move-To-End-Of-Display-Or-Document-Line': ['', 'Move To End Of Display Or Document Line'],
                       'Delete-Current-Character': ['Del', 'Delete Current Character'],
                       'Stuttered-Move-Down-One-Page': ['', 'Stuttered Move Down One Page'],
                       'Move-Right-One-Character': ['Right', 'Move Right One Character'],
                       'Move-To-End-Of-Previous-Word': ['', 'Move To End Of Previous Word'],
                       'Extend-Selection-To-First-Visible-Character-In-Document-Line': ['Shift+Home',
                                                                                        'Extend Selection To First Visible Character In Document Line'],
                       'Move-Down-One-Line': ['Down', 'Move Down One Line'],
                       'Scroll-To-Start-Of-Document': ['', 'Scroll To Start Of Document'],
                       'Extend-Selection-To-Start-Of-Display-Or-Document-Line': ['', 'Extend Selection To Start Of Display Or Document Line'],
                       'Move-Down-One-Page': ['PgDown', 'Move Down One Page'],
                       'Move-To-End-Of-Document-Line': ['End', 'Move To End Of Document Line'],
                       'Delete-Word-To-Right': ['Ctrl+Del', 'Delete Word To Right'],
                       'Convert-Selection-To-Lower-Case': ['Ctrl+U', 'Convert Selection To Lower Case'],
                       'Extend-Selection-Up-One-Paragraph': ['Ctrl+Shift+[', 'Extend Selection Up One Paragraph'],
                       'Move-Up-One-Line': ['Up', 'Move Up One Line'],
                       'Extend-Selection-To-Start-Of-Document': ['Ctrl+Shift+Home', 'Extend Selection To Start Of Document'],
                       'Delete-Current-Line': ['Ctrl+Shift+L', 'Delete Current Line'],
                       'Paste': ['Ctrl+V', 'Paste'],
                       'Extend-Selection-Right-One-Word-Part': ['Ctrl+Shift+\\', 'Extend Selection Right One Word Part'],
                       'Extend-Selection-To-First-Visible-Character-In-Display-Or-Document-Line': ['', 'Extend Selection To First Visible Character In Display Or Document Line'],
                       'Extend-Selection-To-End-Of-Next-Word': ['', 'Extend Selection To End Of Next Word'],
                       'Move-Left-One-Character': ['Left', 'Move Left One Character'],
                       'Redo-Last-Command': ['Ctrl+Y', 'Redo Last Command'],
                       'Move-Left-One-Word-Part': ['Ctrl+/', 'Move Left One Word Part'],
                       'Stuttered-Extend-Selection-Up-One-Page': ['', 'Stuttered Extend Selection Up One Page'],
                       'Delete-Line-To-Right': ['Ctrl+Shift+Del', 'Delete Line To Right'],
                       'Extend-Rectangular-Selection-Right-One-Character': ['Alt+Shift+Right', 'Extend Rectangular Selection Right One Character'],
                       'Transpose-Current-And-Previous-Lines': ['Ctrl+T', 'Transpose Current And Previous Lines'],
                       'Indent-One-Level': ['Tab', 'Indent One Level'],
                       'Extend-Selection-Right-One-Word': ['Ctrl+Shift+Right', 'Extend Selection Right One Word'],
                       'Copy-Selection': ['Ctrl+C', 'Copy Selection'],
                       'Extend-Selection-To-End-Of-Display-Line': ['', 'Extend Selection To End Of Display Line'],
                       'Extend-Selection-To-End-Of-Document-Line': ['Shift+End', 'Extend Selection To End Of Document Line'],
                       'Extend-Rectangular-Selection-Up-One-Page': ['Alt+Shift+PgUp', 'Extend Rectangular Selection Up One Page'],
                       'Extend-Rectangular-Selection-Down-One-Page': ['Alt+Shift+PgDown', 'Extend Rectangular Selection Down One Page'],
                       'Move-To-Start-Of-Document-Line': ['', 'Move To Start Of Document Line'],
                       'Delete-Previous-Character': ['Backspace', 'Delete Previous Character'],
                       'Delete-Previous-Character-If-Not-At-Start-Of-Line': ['', 'Delete Previous Character If Not At Start Of Line'],
                       'Zoom-In': ['Ctrl++', 'Zoom In'],
                       'Move-To-Start-Of-Display-Or-Document-Line': ['', 'Move To Start Of Display Or Document Line'],
                       'Move-To-First-Visible-Character-Of-Display-In-Document-Line': ['', 'Move To First Visible Character Of Display In Document Line'],
                       'Extend-Selection-Up-One-Line': ['Shift+Up', 'Extend Selection Up One Line'],
                       'Copy-Current-Line': ['Ctrl+Shift+T', 'Copy Current Line'],
                       'Move-To-Start-Of-Display-Line': ['Alt+Home', 'Move To Start Of Display Line'],
                       'Move-To-End-Of-Next-Word': ['', 'Move To End Of Next Word'],
                       'Duplicate-The-Current-Line': ['', 'Duplicate The Current Line'],
                       'Move-To-End-Of-Display-Line': ['Alt+End', 'Move To End Of Display Line'],
                       'Extend-Selection-To-End-Of-Document': ['Ctrl+Shift+End', 'Extend Selection To End Of Document'],
                       'Extend-Selection-Up-One-Page': ['Shift+PgUp', 'Extend Selection Up One Page'],
                       'Scroll-To-End-Of-Document': ['', 'Scroll To End Of Document']}
        }
             # extend editor shortcuts with mine
        self.DEFAULT_SHORTCUTS["Editor"].update({
            "Fold-Code": ["", "Fold Code"],
            "Snippets": ["Ctrl+K", "Show Snippets"],
            "Toggle-Indentation-Guide": ["Alt+I", "Toggle Indentation Guide"],
            "Toggle-Breakpoint": ["Alt+B", "Toggle Breakpoint"],
            "Select-to-Matching-Brace": ["", "Select to Matching Brace"],
            "Next-Bookmark": ["", "Next Bookmark"],
            "Previous-Bookmark": ["", "Previous Bookmark"],
            "Comment": ["Ctrl+E", "Comment line/selection"],
            "Uncomment": ["Alt+E", "Uncomment line/selection"],
            "Show-Completion": ["Ctrl+Space", "Show Completions"],
        })

        self.CUSTOM_DEFAULT_SHORTCUTS = {'Ide': {}, 'Editor': {}}

        # load configuration from file
        tempList = []
        file = open("settings.ini", "r")
        for i in file.readlines():
            if i.strip() == '':
                pass
            else:
                tempList.append(tuple(i.strip().split('=')))
        file.close()
        self.settings = dict(tempList)

        self.loadAppData()
        self.loadUseData()

        self.updateInstalledInterpreters()

    def getNameVerFromPath(self, path):
        s = os.path.split(path)[0]
        s = os.path.basename(s)
        s = s[6:]
        l = len(list(s))
        left = s[:l - 1]
        right = s[1:]
        nameVer = "Python " + left + '.' + right
        return nameVer

    def updateInstalledInterpreters(self):
        pyList = self.getPythonExecutables()
        if len(pyList) > 0:
            pyDict = {}
            for i in pyList:
                nameVer = self.getNameVerFromPath(i)
                pyDict[nameVer] = i
            self.SETTINGS["InstalledInterpreters"] = pyDict
        else:
            self.SETTINGS["InstalledInterpreters"] = {}

    def loadAppData(self):
        self.workspaceDir = self.settings["workspace"]
        if not os.path.exists(self.workspaceDir):
            newWorkspace = WorkSpace()
            if newWorkspace.created:
                self.workspaceDir = newWorkspace.path
                self.settings["workspace"] = self.workspaceDir
            else:
                sys.exit()
        self.appPathDict = {
            "snippetsdir": os.path.join(self.workspaceDir, "Snippets"),
            "librarydir": os.path.join(self.workspaceDir, "Library"),
            "projectsdir": os.path.join(self.workspaceDir, "Projects"),
            "venvdir": os.path.join(self.workspaceDir, "Venv"),
            "settingsdir": os.path.join(self.workspaceDir, "Settings"),
            "stylesdir": os.path.join(self.workspaceDir, "Settings", "ColorSchemes"),
            "usedata": os.path.join(self.workspaceDir, "Settings", "usedata.xml"),
            "keymap": os.path.join(self.workspaceDir, "Settings", "keymap.xml")
        }

    def loadUseData(self):
        dom_document = QtXml.QDomDocument()
        file = open(self.appPathDict["usedata"], "r")
        dom_document.setContent(file.read())
        file.close()

        elements = dom_document.documentElement()
        node = elements.firstChild()

        settingsList = []
        while node.isNull() is False:
            property = node.toElement()
            sub_node = property.firstChild()
            while sub_node.isNull() is False:
                sub_prop = sub_node.toElement()
                if node.nodeName() == "openedprojects":
                    path = sub_prop.text()
                    if os.path.exists(path):
                        self.OPENED_PROJECTS.append(path)
                elif node.nodeName() == "settings":
                    settingsList.append((tuple(sub_prop.text().split('=', 1))))
                sub_node = sub_node.nextSibling()
            node = node.nextSibling()

        self.SETTINGS.update(dict(settingsList))
        self.loadKeymap()

    def saveUseData(self):
        dom_document = QtXml.QDomDocument("usedata")

        usedata = dom_document.createElement("usedata")
        dom_document.appendChild(usedata)

        root = dom_document.createElement("openedprojects")
        usedata.appendChild(root)

        for i in self.OPENED_PROJECTS:
            tag = dom_document.createElement("project")
            root.appendChild(tag)

            t = dom_document.createTextNode(i)
            tag.appendChild(t)

        root = dom_document.createElement("settings")
        usedata.appendChild(root)

        s = 0
        for key, value in self.SETTINGS.items():
            if key == "InstalledInterpreters":
                continue
            tag = dom_document.createElement("key")
            root.appendChild(tag)

            t = dom_document.createTextNode(key + '=' + value)
            tag.appendChild(t)
            s += 1

        usedata = dom_document.createElement("usedata")
        dom_document.appendChild(usedata)

        file = open(self.appPathDict["usedata"], "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

        self.settings["running"] = 'False'
        self.saveSettings()

    def loadKeymap(self):
        if self.settings["firstRun"] == "True":
            self.CUSTOM_DEFAULT_SHORTCUTS = self.DEFAULT_SHORTCUTS
            return
        dom_document = QtXml.QDomDocument()
        file = open(self.appPathDict["keymap"], "r")
        x = dom_document.setContent(file.read())
        file.close()

        elements = dom_document.documentElement()
        node = elements.firstChild()
        while node.isNull() is False:
            property = node.toElement()
            sub_node = property.firstChild()
            group = node.nodeName()
            while sub_node.isNull() is False:
                sub_prop = sub_node.toElement()
                tag = sub_prop.toElement()
                name = tag.tagName()
                shortcut = tag.attribute("shortcut")
                shortcut = QtGui.QKeySequence(shortcut).toString()
                function = tag.attribute("function")
                self.CUSTOM_DEFAULT_SHORTCUTS[
                    group][name] = [shortcut, function]

                sub_node = sub_node.nextSibling()

            node = node.nextSibling()

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
        file = open("settings.ini", "w")
        for key, value in self.settings.items():
            file.write('\n' + key + '=' + value)
        file.close()

    def readFile(self, fileName):
        file = open(fileName, 'rb')
        bb = file.read()
        file.close()
        encoding = determineEncoding(bb)

        file = open(fileName, 'r')
        text = file.read()
        file.close()

        lineEnding = determineLineEnding(text)

        return text, encoding, lineEnding

    def getPythonExecutables(self):
        pythonExecutables = PythonExecutables()
        interpreters = pythonExecutables.findPythonExecutables()
        return interpreters
