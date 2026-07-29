@echo off
chcp 65001 >nul
title Editor de Cracha de Supervisor
cd /d "%~dp0"

set PYTHON=C:\SistemaCracha\.venv\Scripts\python.exe

if not exist "%PYTHON%" (
    echo ERRO: Python do projeto nao encontrado em:
    echo %PYTHON%
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0editor_supervisor.py"
