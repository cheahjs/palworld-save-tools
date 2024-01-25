@ECHO OFF

@REM Check if python is installed, error if not
python3 --version 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    py --version 2>NUL
    IF %ERRORLEVEL% NEQ 0 (
        python --version 2>NUL
        IF %ERRORLEVEL% NEQ 0 (
            ECHO Python is not installed. Please install python and try again.
            PAUSE
            EXIT /B 1
        ) ELSE (
            SET PYTHON_BIN=python
        )
    ) ELSE (
        SET PYTHON_BIN=py
    )
) ELSE (
    SET PYTHON_BIN=python3
)

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
    ECHO uesave.exe is missing. Please download it from https://github.com/trumank/uesave-rs/releases/download/v0.3.0/uesave-x86_64-pc-windows-msvc.zip and extract uesave.exe into a folder called uesave.
    MKDIR uesave
    PAUSE
    EXIT /B 1
)

ECHO This will convert the save file "%~1" in JSON format in back to .sav format.
ECHO This will overwrite your existing .sav file!
@REM Ask user if they want to continue
CHOICE /C YN /M "Continue?"
IF %ERRORLEVEL% NEQ 1 (
    EXIT /B 1
)

%PYTHON_BIN% convert-single-json-to-sav.py "uesave/uesave.exe" "%~1"
PAUSE
