@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py --open-dashboard %*
) else (
    echo [ERROR] Virtual environment .venv tidak ditemukan.
    echo Silakan buat venv terlebih dahulu: python -m venv .venv
)
pause
