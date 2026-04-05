param(
  [string]$VenvPath = '.venv-api'
)

$ErrorActionPreference = 'Stop'
$venvPython = Join-Path $VenvPath 'Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
  Write-Host "Venv not found. Running setup..."
  & powershell -ExecutionPolicy Bypass -File scripts/backend-setup.ps1 -VenvPath $VenvPath
}

& $venvPython backend/smoke_test.py
