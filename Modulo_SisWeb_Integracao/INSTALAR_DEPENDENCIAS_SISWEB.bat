@echo off
cd /d C:\SistemaCracha
call .venv\Scripts\activate.bat 2>nul
python -m pip install -r requirements_sisweb.txt
pause
