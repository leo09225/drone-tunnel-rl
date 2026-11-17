@echo off
setlocal

set "ROOT=%~dp0.."
set "PYTHON=%ROOT%\.venv\Scripts\python.exe"
set "APP=%ROOT%\multi_agent\app.py"
set "SOLARA_HOME=%ROOT%\.solara_local"

if not exist "%PYTHON%" (
    echo Virtual environment Python not found: "%PYTHON%"
    exit /b 1
)

"%PYTHON%" -m solara run "%APP%"
