param(
  [string]$VenvPath = '.venv-api',
  [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
$venvPython = Join-Path $VenvPath 'Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
  Write-Host "Venv not found. Running setup..."
  & powershell -ExecutionPolicy Bypass -File scripts/backend-setup.ps1 -VenvPath $VenvPath
}

# Stop any stale backend uvicorn processes before starting a fresh dev server.
try {
  $backendProcs = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object {
    $_.CommandLine -like '*backend.app.main:app*'
  }
  foreach ($proc in $backendProcs) {
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
  }
} catch {
  Write-Host "Warning: failed to inspect/stop existing backend processes. Continuing..."
}

& $venvPython -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port $Port
