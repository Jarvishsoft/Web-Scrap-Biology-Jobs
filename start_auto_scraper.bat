@echo off
cd /d "%~dp0"
title Auto-Refresh Scraper Biologi Jabek (Tiap 5 Menit)
echo ================================================================
echo   MEMULAI CRON JOB AUTO-REFRESH SCRAPER LOWONGAN S1 BIOLOGI
echo   Interval: Otomatis Setiap 5 Menit
echo   Dashboard: http://localhost:8000/dashboard.html
echo ================================================================
echo.
echo [INFO] Server dashboard akan berjalan di http://localhost:8000
echo [INFO] Buka URL tersebut di browser untuk tombol Refresh berfungsi.
echo [INFO] Jangan tutup jendela ini selama scraping berjalan.
echo.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scheduler.py --interval 5 --max-results 10 --open-dashboard %*
) else if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" scheduler.py --interval 5 --max-results 10 --open-dashboard %*
) else (
    python scheduler.py --interval 5 --max-results 10 --open-dashboard %*
)
pause
