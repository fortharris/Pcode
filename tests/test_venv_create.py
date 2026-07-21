"""Create a real project-style venv (stdlib venv + ensurepip)."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Extensions.python_paths import (  # noqa: E402
    venv_exists,
    venv_python,
    venv_site_packages,
)


def test_stdlib_venv_create_with_pip(tmp_path):
    # Plain create (ensurepip) — avoid --upgrade-deps network/slowness in CI.
    venvdir = str(tmp_path / "Venv")
    completed = subprocess.run(
        [sys.executable, "-m", "venv", venvdir],
        check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert venv_exists(venvdir)
    assert os.path.isfile(os.path.join(venvdir, "pyvenv.cfg"))
    site = venv_site_packages(venvdir)
    assert os.path.isdir(site)
    pip_check = subprocess.run(
        [venv_python(venvdir), "-c", "import pip"],
        check=False, capture_output=True, text=True)
    assert pip_check.returncode == 0, pip_check.stderr or pip_check.stdout
