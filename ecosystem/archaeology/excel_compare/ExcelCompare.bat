@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%excel_compare.py

echo ARG1=%~f1

echo ARG2=%~f2

cd %SCRIPT_DIR%
py "%~dp0excel_compare.py" "%~f1" "%~f2"

start logs

pause