# PowerShell Runner: Otomatis menggunakan Python dari virtual environment .venv
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $scriptDir ".venv\Scripts\python.exe"
$mainScript = Join-Path $scriptDir "main.py"

if (Test-Path $pythonExe) {
    & $pythonExe $mainScript --open-dashboard @args
} else {
    Write-Error "Virtual environment .venv tidak ditemukan di $scriptDir"
}
