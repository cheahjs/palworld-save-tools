@ECHO OFF
SETLOCAL enabledelayedexpansion

:FindPythonCommand
for %%A in (python3 python py) do (
    ECHO Checking if Python is installed as %%A
    where %%A
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_BIN=%%A"
        echo Found Python at !PYTHON_BIN!
        goto :Found
    )
)

echo Python not found. Please install Python 3.9 or newer.
pause
exit /B 1

:Found
@REM Print Python version for debugging
ECHO Python version:
!PYTHON_BIN! --version

@REM Switch to script directory
cd /D "%~dp0"

@REM Check if convert.py exists
IF NOT EXIST "convert.py" (
    ECHO convert.py is missing.
    PAUSE
    EXIT /B 1
)

!PYTHON_BIN! convert.py "%~1"
PAUSE
