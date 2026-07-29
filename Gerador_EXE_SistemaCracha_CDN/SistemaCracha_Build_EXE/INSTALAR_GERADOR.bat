@echo off
chcp 65001 >nul
title Preparar Gerador de EXE
cd /d "%~dp0"

echo Copiando arquivos de compilacao para C:\SistemaCracha...

if not exist "C:\SistemaCracha" (
    echo ERRO: A pasta C:\SistemaCracha nao foi encontrada.
    pause
    exit /b 1
)

copy /Y "SistemaCrachaCDN.spec" "C:\SistemaCracha\SistemaCrachaCDN.spec" >nul
copy /Y "version_info.txt" "C:\SistemaCracha\version_info.txt" >nul
copy /Y "icone_cdn.ico" "C:\SistemaCracha\icone_cdn.ico" >nul
copy /Y "GERAR_EXE.bat" "C:\SistemaCracha\GERAR_EXE.bat" >nul

echo.
echo Arquivos instalados.
echo Agora abra C:\SistemaCracha e execute GERAR_EXE.bat
echo.
pause
