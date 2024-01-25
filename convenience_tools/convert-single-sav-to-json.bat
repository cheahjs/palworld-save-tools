@ECHO OFF
SETLOCAL enabledelayedexpansion

:FindPythonCommand
for %%A in (python3 python py) do (
    where /Q %%A
    if !errorlevel! EQU 0 (
        set "PYTHON_BIN=%%A"
        echo Found Python at !PYTHON_BIN!
        %PYTHON_BIN% --version
        goto :Found
    )
)

echo Python not found. Please install Python 3.
pause
exit /B 1

:Found
@REM Switch to script directory
cd /D "%~dp0"

@REM Check if convert-single-sav-to-json.py exists
IF NOT EXIST "convert-single-sav-to-json.py" (
    ECHO convert-single-sav-to-json.py is missing.
    PAUSE
    EXIT /B 1
)

@REM Check if first argument exists
IF NOT EXIST "%~1" (
    ECHO You must specify a .sav file to convert.
    PAUSE
    EXIT /B 1
)

@REM Check if uesave.exe exists
IF NOT EXIST "uesave/uesave.exe" (
    ECHO uesave.exe is missing. Please download it from https://github.com/trumank/uesave-rs/releases/download/v0.3.0/uesave-x86_64-pc-windows-msvc.zip and extract uesave.exe into a folder called uesave.
    MKDIR uesave
    PAUSE
    EXIT /B 1
)

ECHO This will convert the save file "%~1" to JSON format.
@REM Ask user if they want to continue
CHOICE /C YN /M "Continue?"
IF %ERRORLEVEL% NEQ 1 (
    EXIT /B 1
)

%PYTHON_BIN% convert-single-sav-to-json.py "uesave/uesave.exe" "%~1"
PAUSE
