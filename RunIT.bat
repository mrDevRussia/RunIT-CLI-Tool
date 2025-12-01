@echo off
setlocal

REM RunIT CLI Tool Launcher
REM Automatically sets environment and runs main.py

set "RUNIT_HOME=%~dp0"
set "PYTHONPATH=%RUNIT_HOME%;%PYTHONPATH%"
cd /d "%RUNIT_HOME%"

if "%1"=="" (
    python main.py
) else (
    python main.py %*
)

pause