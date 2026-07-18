"""CLI helper: freeze a Desktop Application project with cx_Freeze (no GUI).

Usage (from repo root, with build deps installed)::

    python scripts/freeze_project.py path/to/project

Requires ``pip install -e ".[build]"`` (or ``requirements.txt`` which includes
cx_Freeze). Exit code 0 on success; prints the build directory and artifact.
"""

from __future__ import annotations

import argparse
import os
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description="Freeze a Pcode project")
    parser.add_argument(
        "project",
        help="Path to a Pcode project root (contains project.json or project.xml)",
    )
    parser.add_argument(
        "--interpreter",
        default=sys.executable,
        help="Python interpreter to freeze against (default: current)",
    )
    args = parser.parse_args(argv)

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo)
    if repo not in sys.path:
        sys.path.insert(0, repo)

    project = os.path.abspath(args.project)
    if not os.path.isdir(project):
        print("error: not a directory:", project, file=sys.stderr)
        return 2

    from Extensions.ProjectManifest import read as read_manifest
    from Extensions.ProjectData import load as load_project_data
    from Extensions.BuildProfile import load as load_build_profile
    from Extensions.Projects.ProjectManager.Build import BuildThread

    manifest = read_manifest(project)
    if not manifest:
        print("error: no Pcode project manifest in", project, file=sys.stderr)
        return 2
    _tag, data = manifest

    mainscript_name = data.get("MainScript") or "main.py"
    mainscript = os.path.join(project, "src", mainscript_name)
    if not os.path.isfile(mainscript):
        mainscript = os.path.join(project, mainscript_name)
    if not os.path.isfile(mainscript):
        print("error: main script not found:", mainscript, file=sys.stderr)
        return 2

    sourcedir = os.path.join(project, "src")
    if not os.path.isdir(sourcedir):
        sourcedir = project

    iconsdir = os.path.join(project, "Resources", "Icons")
    os.makedirs(iconsdir, exist_ok=True)

    if sys.platform.startswith("win"):
        builddir = os.path.join(project, "Build", "Windows")
    elif sys.platform == "darwin":
        builddir = os.path.join(project, "Build", "Mac")
    else:
        builddir = os.path.join(project, "Build", "Linux")
    os.makedirs(builddir, exist_ok=True)

    project_path_dict = {
        "root": project,
        "sourcedir": sourcedir,
        "builddir": builddir,
        "mainscript": mainscript,
        "iconsdir": iconsdir,
        "name": data.get("Name") or os.path.basename(project),
        "type": data.get("Type") or "Desktop Application",
        "buildprofile": os.path.join(project, "Build", "profile.json"),
    }

    settings = load_project_data(project).get("settings", {})
    settings["DefaultInterpreter"] = args.interpreter
    settings["UseVirtualEnv"] = "False"

    profile = load_build_profile(os.path.join(project, "Build"))
    thread = BuildThread()
    thread.profile = profile
    thread.projectPathDict = project_path_dict
    thread.projectSettings = settings

    class _UseData:
        SETTINGS = {"InstalledInterpreters": [args.interpreter]}

    thread.useData = _UseData()
    thread.missing = []
    thread.run()

    if getattr(thread, "error", None):
        print("error: freeze failed:", thread.error, file=sys.stderr)
        return 1

    stem = os.path.splitext(os.path.basename(mainscript))[0]
    candidates = [stem + ".exe", stem]
    names = set(os.listdir(builddir)) if os.path.isdir(builddir) else set()
    artifact = next((c for c in candidates if c in names), None)
    print("builddir:", builddir)
    if artifact:
        print("artifact:", os.path.join(builddir, artifact))
        return 0
    print("warning: freeze finished but expected artifact not found:",
          candidates, file=sys.stderr)
    if getattr(thread, "missing", None):
        print("missing modules:", len(thread.missing), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
