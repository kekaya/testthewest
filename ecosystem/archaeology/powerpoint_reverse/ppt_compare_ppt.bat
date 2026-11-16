@echo off
setlocal
chcp 65001 >nul

REM Ruft das Python-Skript auf und übergibt alle per Drag-and-Drop gezogenen Dateien
py "%~dp0compare_ppt.py" %*

echo.
echo Fertig! Das HTML-Protokoll wurde erstellt.
pause