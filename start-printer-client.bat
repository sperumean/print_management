@echo off
cd /d "%~dp0"

:loop
python printer-client.py
timeout /t 5 /nobreak
goto loop
