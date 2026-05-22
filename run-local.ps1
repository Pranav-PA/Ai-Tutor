$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$BackendPort = 18080
$FrontendPort = 38173
$BackendProc = $null
$FrontendProc = $null

function Write-Step($msg) { Write-Host "`n$msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host $msg -ForegroundColor Red }

function Get-ListeningPids([int]$Port) {
  $pids = @()
  try {
    $connections = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
      $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    }
  } catch {}

  if (-not $pids -or $pids.Count -eq 0) {
    $netstatLines = netstat -ano | Select-String ":$Port"
    foreach ($line in $netstatLines) {
      $text = ($line.ToString() -replace '\s+', ' ').Trim()
      if ($text -match 'LISTENING\s+(\d+)$') {
        $pids += [int]$Matches[1]
      }
    }
    $pids = $pids | Select-Object -Unique
  }

  return $pids
}

function Stop-PortListeners([int]$Port) {
  $pids = Get-ListeningPids $Port
  if ($pids -and $pids.Count -gt 0) {
    Write-Warn "Port $Port busy -> stopping process(es): $($pids -join ', ')"
    foreach ($pid in $pids) {
      try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
    }
    Start-Sleep -Seconds 1
  }

  $stillBusy = Get-ListeningPids $Port
  if ($stillBusy -and $stillBusy.Count -gt 0) {
    throw "Port $Port is still in use. Stop the process manually and retry."
  }
}

function Wait-ForPort([int]$Port, [string]$Name) {
  for ($i = 0; $i -lt 30; $i++) {
    $pids = Get-ListeningPids $Port
    if ($pids -and $pids.Count -gt 0) { return }
    Start-Sleep -Milliseconds 500
  }
  throw "$Name failed to bind on port $Port"
}

try {
  Write-Step '[1/5] Checking prerequisites...'

  $pythonCmd = $null
  if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = 'py -3'
  } elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = 'python'
  } else {
    throw 'Python 3.10+ not found. Install Python and retry.'
  }

  if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js not found. Install Node 18+ and retry.'
  }

  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw 'npm not found. Install npm and retry.'
  }

  Write-Host "  Node:   $(node --version)"

  if (-not (Test-Path "$RootDir/.env") -and (Test-Path "$RootDir/.env.example")) {
    Copy-Item "$RootDir/.env.example" "$RootDir/.env"
    Write-Warn '  Created .env from .env.example — edit it to add your API key(s)'
  }

  Write-Step '[2/5] Setting up Python environment...'

  if (-not (Test-Path "$RootDir/venv")) {
    Invoke-Expression "$pythonCmd -m venv `"$RootDir/venv`""
    Write-Host '  Created virtual environment'
  }

  $venvPython = "$RootDir/venv/Scripts/python.exe"
  & $venvPython -m pip install --upgrade pip | Out-Host
  & $venvPython -m pip install -r "$RootDir/requirements.txt" | Out-Host
  Write-Host '  Python dependencies installed'

  Write-Step '[3/5] Installing frontend dependencies...'

  Set-Location "$RootDir/frontend"
  if (-not (Test-Path "$RootDir/frontend/node_modules")) {
    npm ci
    Write-Host '  node_modules installed'
  } else {
    Write-Host '  node_modules already exists (skipping)'
  }
  Set-Location $RootDir

  Write-Step '[4/5] Ensuring data directories...'
  New-Item -ItemType Directory -Force -Path "$RootDir/app-data/uploads","$RootDir/app-data/vectors","$RootDir/app-data/generated","$RootDir/app-data/progress","$RootDir/app-data/cache","$RootDir/app-data/courses" | Out-Null

  Write-Host '      Freeing required ports...' -ForegroundColor Green
  Stop-PortListeners $BackendPort
  Stop-PortListeners $FrontendPort

  Write-Step '[5/5] Starting services...'

  $BackendProc = Start-Process -FilePath $venvPython -ArgumentList '-m','uvicorn','backend.main:app','--host','0.0.0.0','--port',"$BackendPort" -WorkingDirectory $RootDir -PassThru
  Wait-ForPort $BackendPort 'Backend'
  Write-Host "  Backend  -> http://localhost:$BackendPort" -ForegroundColor Green
  Write-Host "  Health   -> http://localhost:$BackendPort/api/health" -ForegroundColor Green

  $FrontendProc = Start-Process -FilePath 'npm' -ArgumentList 'run','dev' -WorkingDirectory "$RootDir/frontend" -PassThru
  Wait-ForPort $FrontendPort 'Frontend'
  Write-Host "  Frontend -> http://localhost:$FrontendPort" -ForegroundColor Green

  Write-Host "`n============================================================"
  Write-Host '  Both services running. Press Ctrl+C to stop.'
  Write-Host "============================================================`n"

  while ($true) {
    if ($BackendProc.HasExited) { throw 'Backend process exited unexpectedly.' }
    if ($FrontendProc.HasExited) { throw 'Frontend process exited unexpectedly.' }
    Start-Sleep -Seconds 1
  }
}
catch {
  Write-Err "`n$($_.Exception.Message)"
  exit 1
}
finally {
  Write-Warn "`nShutting down..."
  if ($FrontendProc -and -not $FrontendProc.HasExited) {
    try { Stop-Process -Id $FrontendProc.Id -Force } catch {}
  }
  if ($BackendProc -and -not $BackendProc.HasExited) {
    try { Stop-Process -Id $BackendProc.Id -Force } catch {}
  }
  Write-Host 'Done.' -ForegroundColor Green
}
