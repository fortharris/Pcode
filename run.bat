@echo off
cd /d "%~dp0"
if not exist ".pcode-venv\Scripts\python.exe" (
  echo Create the venv first. From the parent folder run:
  echo   python -m venv Pcode\.pcode-venv
  echo   Pcode\.pcode-venv\Scripts\pip install -r Pcode\requirements.txt
  exit /b 1
)
".pcode-venv\Scripts\python.exe" Pcode.py %*
