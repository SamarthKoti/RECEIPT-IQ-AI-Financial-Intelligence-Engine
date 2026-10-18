$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$python = Join-Path $projectRoot '.venv/Scripts/python.exe'
$frontend = Join-Path $projectRoot 'frontend'
$logDirectory = Join-Path $projectRoot 'data/run'

if (-not (Test-Path -LiteralPath $python)) { throw 'Python environment missing. Follow README.md installation instructions first.' }
if (-not (Test-Path -LiteralPath (Join-Path $frontend 'node_modules/vite/bin/vite.js'))) { throw 'Frontend dependencies missing. Run npm ci in frontend first.' }
$node = (Get-Command node -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null

function Test-LocalEndpoint([string]$Url) {
    try { return (Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 }
    catch { return $false }
}

if (-not (Test-LocalEndpoint 'http://127.0.0.1:8000/api/health')) {
    Push-Location $projectRoot
    try {
        & $python -m alembic -c backend/alembic.ini upgrade head
        if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
    } finally { Pop-Location }
    Start-Process -FilePath $python -ArgumentList '-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000' -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory 'backend.stdout.log') -RedirectStandardError (Join-Path $logDirectory 'backend.stderr.log') | Out-Null
}

if (-not (Test-LocalEndpoint 'http://127.0.0.1:5173')) {
    Start-Process -FilePath $node -ArgumentList 'node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5173 --strictPort' -WorkingDirectory $frontend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory 'frontend.stdout.log') -RedirectStandardError (Join-Path $logDirectory 'frontend.stderr.log') | Out-Null
}

$ready = $false
for ($attempt = 0; $attempt -lt 15; $attempt++) {
    if ((Test-LocalEndpoint 'http://127.0.0.1:5173/api/health') -and (Test-LocalEndpoint 'http://127.0.0.1:5173')) { $ready = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $ready) { throw "Startup did not finish. Inspect logs in $logDirectory and check whether ports 5173/8000 are occupied." }
Write-Host 'Receipt IQ is ready: http://127.0.0.1:5173'
Write-Host "Background server logs: $logDirectory"
