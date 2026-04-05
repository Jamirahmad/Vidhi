param(
  [string]$VenvPath = '.venv-api'
)

$ErrorActionPreference = 'Stop'

function Resolve-Python {
  if (Get-Command py -ErrorAction SilentlyContinue) { return 'py' }
  if (Get-Command python -ErrorAction SilentlyContinue) { return 'python' }
  $fallback = Join-Path $env:LocalAppData 'Python\pythoncore-3.14-64\python.exe'
  if (Test-Path $fallback) { return $fallback }
  throw 'Python interpreter not found. Install Python 3.11+ and retry.'
}

$pythonCmd = Resolve-Python
$venvPython = Join-Path $VenvPath 'Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
  if ($pythonCmd -eq 'py') {
    & py -m venv $VenvPath
  } else {
    & $pythonCmd -m venv $VenvPath
  }
}

& $venvPython -m pip install --upgrade pip setuptools wheel
& $venvPython -m pip install -r backend/requirements.txt

Write-Host "Backend venv ready at $VenvPath"
