# PowerShell Runner: Memulai Auto-Refresh Scraper Setiap 5 Menit
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $scriptDir ".venv\Scripts\python.exe"
$schedulerScript = Join-Path $scriptDir "scheduler.py"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  MEMULAI CRON JOB AUTO-REFRESH SCRAPER LOWONGAN S1 BIOLOGI" -ForegroundColor Green
Write-Host "  Interval: Otomatis Setiap 5 Menit" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan

if (Test-Path $pythonExe) {
    & $pythonExe $schedulerScript --interval 5 --max-results 10 --open-dashboard @args
} else {
    Write-Error "Virtual environment .venv tidak ditemukan di $scriptDir"
}
