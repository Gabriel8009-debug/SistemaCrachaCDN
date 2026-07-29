@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Build definitivo - Sistema de Crachas CDN

echo ==================================================
echo   BUILD DEFINITIVO - SISTEMA DE CRACHAS CDN
echo ==================================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo ERRO: ambiente virtual .venv nao encontrado.
  echo Crie com: py -m venv .venv
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto :erro

python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :erro
python -m pip install -r requirements_build.txt
if errorlevel 1 goto :erro

python validar_build.py
if errorlevel 1 goto :erro

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller --clean --noconfirm SistemaCrachaCDN.spec
if errorlevel 1 goto :erro

set "DEST=dist\SistemaCrachaCDN"
for %%D in (credentials output fotos_temp logs) do if not exist "%DEST%\%%D" mkdir "%DEST%\%%D"
if exist "credentials\credenciais.json" copy /Y "credentials\credenciais.json" "%DEST%\credentials\credenciais.json" >nul
if exist "LEIA-ME-EXECUTAVEL.txt" copy /Y "LEIA-ME-EXECUTAVEL.txt" "%DEST%\LEIA-ME.txt" >nul

echo.
echo BUILD CONCLUIDO:
echo %CD%\%DEST%\SistemaCrachaCDN.exe
echo.
echo Mantenha toda a pasta SistemaCrachaCDN junta.
pause
exit /b 0

:erro
echo.
echo BUILD INTERROMPIDO. Revise a mensagem acima.
pause
exit /b 1
