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

rem Hardcoded full path to Excel config file
set "excel_file=%script_dir%.venv\Scripts\TestConfig.xlsx"
set "sheet_name=Tests"

rem Call helper Python to read Excel and get enabled script names
for /f "usebackq delims=" %%s in (`"%venv_python%" "%script_dir%get_enabled_scripts.py" "%excel_file%" "%sheet_name%"`) do (
    echo Running %%s...
    "%venv_python%" "%script_dir%%%s"
    if errorlevel 1 (
        echo Error running %%s >&2
        exit /b 1
    )
)

echo All selected scripts executed.
endlocal
