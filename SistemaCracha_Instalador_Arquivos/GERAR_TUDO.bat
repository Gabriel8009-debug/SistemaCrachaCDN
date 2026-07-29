@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title Build completo - Sistema de Crachás CDN

call "GERAR_EXE_DEFINITIVO.bat"
if errorlevel 1 exit /b 1

call "GERAR_INSTALADOR.bat"
exit /b %errorlevel%
