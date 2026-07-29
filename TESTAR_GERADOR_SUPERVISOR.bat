@echo off
chcp 65001 >nul
title Teste do Gerador de Supervisor
cd /d "%~dp0"

set PYTHON=C:\SistemaCracha\.venv\Scripts\python.exe

if not exist "%PYTHON%" (
    echo ERRO: Python do projeto nao encontrado.
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0testar_geracao_supervisor.py"
pause
