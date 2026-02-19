# build.ps1
Set-Location -Path $PSScriptRoot

Write-Host "Checking for virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "Building executable with PyInstaller..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m PyInstaller --clean build_broker.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable is at: dist\lightroom-mcp-broker.exe" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
