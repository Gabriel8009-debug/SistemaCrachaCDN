@echo off
chcp 65001 >nul
title Gerar EXE - Sistema de Crachás CDN
cd /d "%~dp0"

echo.
echo ==================================================
echo   SISTEMA DE CRACHAS CDN - GERADOR DO EXECUTAVEL
echo ==================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado em:
    echo %CD%\.venv
    echo.
    echo Execute este arquivo dentro da pasta C:\SistemaCracha
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

echo Atualizando ferramentas de empacotamento...
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade pyinstaller

echo.
echo Limpando compilacoes anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Gerando o executavel...
python -m PyInstaller --clean --noconfirm "SistemaCrachaCDN.spec"

if errorlevel 1 (
    echo.
    echo ERRO: O executavel nao foi gerado.
    echo Copie toda a mensagem exibida acima.
    pause
    exit /b 1
)

echo.
echo Copiando pastas externas de operacao...

if not exist "dist\SistemaCrachaCDN\credentials" mkdir "dist\SistemaCrachaCDN\credentials"
if not exist "dist\SistemaCrachaCDN\output" mkdir "dist\SistemaCrachaCDN\output"
if not exist "dist\SistemaCrachaCDN\fotos_temp" mkdir "dist\SistemaCrachaCDN\fotos_temp"
if not exist "dist\SistemaCrachaCDN\logs" mkdir "dist\SistemaCrachaCDN\logs"

if exist "credentials\*" xcopy "credentials\*" "dist\SistemaCrachaCDN\credentials\" /E /I /Y >nul

echo.
echo ==================================================
echo   EXECUTAVEL GERADO COM SUCESSO
echo ==================================================
echo.
echo Pasta final:
echo %CD%\dist\SistemaCrachaCDN
echo.
echo Aplicativo:
echo %CD%\dist\SistemaCrachaCDN\SistemaCrachaCDN.exe
echo.
echo IMPORTANTE:
echo Use a pasta SistemaCrachaCDN inteira.
echo Nao mova somente o arquivo .exe.
echo.
pause
