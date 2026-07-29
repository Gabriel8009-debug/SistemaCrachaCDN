@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Instalador - Sistema de Crachas CDN

echo ==================================================
echo   INSTALADOR PROFISSIONAL - SISTEMA DE CRACHAS CDN
echo ==================================================
echo.

if not exist "dist\SistemaCrachaCDN\SistemaCrachaCDN.exe" (
    echo O executavel ainda nao foi gerado.
    echo Iniciando o build definitivo primeiro...
    echo.
    call "GERAR_EXE_DEFINITIVO.bat"
    if errorlevel 1 goto :erro
)

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    echo ERRO: Inno Setup 6 nao encontrado.
    echo Instale o Inno Setup 6 e execute novamente.
    pause
    exit /b 1
)

if exist "dist_instalador" rmdir /s /q "dist_instalador"
mkdir "dist_instalador"

"%ISCC%" "installer\SistemaCrachaCDN.iss"
if errorlevel 1 goto :erro

echo.
echo INSTALADOR GERADO COM SUCESSO:
echo %CD%\dist_instalador\Setup_SistemaCrachaCDN.exe
explorer "%CD%\dist_instalador"
pause
exit /b 0

:erro
echo.
echo A geracao foi interrompida. Revise a mensagem acima.
pause
exit /b 1
