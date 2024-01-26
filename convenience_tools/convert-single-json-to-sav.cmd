@ECHO OFF
SETLOCAL enabledelayedexpansion

:FindPythonCommand
for %%A in (python3 python py) do (
    where /Q %%A
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_BIN=%%A"
        echo Found Python at !PYTHON_BIN!
        goto :Found
    )
)

echo Python not found. Please install Python 3.
pause
exit /B 1

:Found
@REM Print Python version for debugging
ECHO Python version:
%PYTHON_BIN% --version

@REM Switch to script directory
cd /D "%~dp0"

@REM Check if convert-single-json-to-sav.py exists
IF NOT EXIST "convert-single-json-to-sav.py" (
    ECHO convert-single-json-to-sav.py is missing.
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
    ECHO uesave.exe is missing. Did you download the palworld-save-tools.zip from releases?
    MKDIR uesave
    PAUSE
    EXIT /B 1
)

ECHO This will convert the save file "%~1" in JSON format in back to .sav format.
ECHO This will overwrite your existing .sav file!
ECHO Please make a backup of your .sav file before continuing!
@REM Ask user if they want to continue
CHOICE /C YN /M "Continue?"
IF %ERRORLEVEL% NEQ 1 (
    ECHO Exiting because aborted.
    EXIT /B 1
)

%PYTHON_BIN% convert-single-json-to-sav.py "uesave/uesave.exe" "%~1"
PAUSE
