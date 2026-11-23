@echo off
cd /d "%~dp0"
python serve.py || py serve.py
pause
