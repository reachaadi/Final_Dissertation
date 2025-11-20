@echo off
setlocal enabledelayedexpansion

rem Get the script directory (equivalent to BASH_SOURCE)
set "script_dir=%~dp0"
set "venv_python=%script_dir%.venv\Scripts\python.exe"

rem Check if python executable exists
if not exist "%venv_python%" (
    echo Error: Python not found at %venv_python% >&2
    exit /b 1
)

rem List of scripts to run
set scripts=TestScript.py TestScript2.py TestScript3.py

for %%s in (%scripts%) do (
    echo Running %%s...
    "%venv_python%" "%script_dir%%%s"
    if errorlevel 1 (
        echo Error running %%s >&2
        exit /b 1
    )
)

echo All scripts executed.
endlocal
