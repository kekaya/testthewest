@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%xlsb_compare.py

if "%~2"=="" (
    echo.
    echo Drag exactly TWO XLSB files onto this BAT file.
    echo.
    pause
    exit /b 1
)

cd %SCRIPT_DIR%

py "%PYTHON_SCRIPT%" "%~f1" "%~f2"

pause