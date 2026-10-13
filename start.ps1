param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython (Join-Path $PSScriptRoot 'app.py') --port $Port
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 (Join-Path $PSScriptRoot 'app.py') --port $Port
} else {
    python (Join-Path $PSScriptRoot 'app.py') --port $Port
}
