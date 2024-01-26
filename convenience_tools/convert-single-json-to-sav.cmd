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
:: Print Python version for debugging
ECHO Python version:
%PYTHON_BIN% --version

:: Check that the minor version of python is at least 9.
FOR /F "tokens=1,2 delims=." %%G IN ('%PYTHON_BIN% --version') DO (
   SET PYTHON_VERSION_MINOR=%%H
)

IF %PYTHON_VERSION_MINOR% LSS 9 (
  ECHO Python 3.9 or higher is required.
  EXIT /B 1
)

:: Switch to script directory
cd /D "%~dp0"

:: Check if convert-single-json-to-sav.py exists
IF NOT EXIST "convert-single-json-to-sav.py" (
    ECHO convert-single-json-to-sav.py is missing.
    PAUSE
    EXIT /B 1
)

:: Check if first argument exists
IF NOT EXIST "%~1" (
    ECHO You must specify a .sav file to convert.
    PAUSE
    EXIT /B 1
)

:: Check if uesave.exe exists
IF NOT EXIST "uesave/uesave.exe" (
    ECHO uesave.exe is missing. Did you download the palworld-save-tools.zip from releases?
    MKDIR uesave
    PAUSE
    EXIT /B 1
)

ECHO This will convert the save file "%~1" in JSON format in back to .sav format.
ECHO This will overwrite your existing .sav file!
ECHO Please make a backup of your .sav file before continuing!
:: Ask user if they want to continue
CHOICE /C YN /M "Continue?"
IF %ERRORLEVEL% NEQ 1 (
    ECHO Exiting because aborted.
    EXIT /B 1
)

%PYTHON_BIN% convert-single-json-to-sav.py "uesave/uesave.exe" "%~1"
PAUSE
