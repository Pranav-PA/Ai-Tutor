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

function Is-PortListening([int]$Port) {
  # Method 1: Use netstat (most reliable on Windows)
  $output = netstat -ano 2>$null | Select-String ":$Port\s+.*LISTENING"
  if ($output) { return $true }
  
  # Method 2: Try Get-NetTCPConnection
  try {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($conn) { return $true }
  } catch {}
  
  return $false
}

function Stop-PortListeners([int]$Port) {
  if (Is-PortListening $Port) {
    Write-Warn "Port $Port is in use. Attempting to free it..."
    
    # Use netstat to kill the process
    $output = netstat -ano 2>$null | Select-String ":$Port\s+.*LISTENING"
    if ($output) {
      foreach ($line in $output) {
        if ($line -match '(\d+)\s*$') {
          $pid = [int]$Matches[1]
          try {
            taskkill /pid $pid /f 2>$null | Out-Null
            Start-Sleep -Milliseconds 500
          } catch {}
        }
      }
    }
  }
  
  Start-Sleep -Milliseconds 500
  
  if (Is-PortListening $Port) {
    throw "Port $Port is still in use. Close the application and retry."
  }
}

function Wait-ForPort([int]$Port, [string]$Name, [int]$TimeoutSeconds = 20) {
  $startTime = Get-Date
  
  while ((Get-Date) -lt $startTime.AddSeconds($TimeoutSeconds)) {
    if (Is-PortListening $Port) {
      Write-Host "  ✓ $Name ready on port $Port" -ForegroundColor Green
      return
    }
    Start-Sleep -Milliseconds 500
  }
  
  throw "$Name failed to start on port $Port (timeout after $TimeoutSeconds seconds)"
}

try {
  Write-Step '[1/5] Checking prerequisites...'

  # Check Python
  $pythonExe = $null
  try {
    $pythonVer = & py -3 --version 2>&1
    $pythonExe = 'py -3'
    Write-Host "  Python: $pythonVer"
  } catch {
    try {
      $pythonVer = & python --version 2>&1
      $pythonExe = 'python'
      Write-Host "  Python: $pythonVer"
    } catch {
      throw 'Python 3.10+ not found. Install Python (add to PATH) and retry.'
    }
  }

  if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js not found. Install Node 18+ and add to PATH, then retry.'
  }
  Write-Host "  Node:   $(node --version)"

  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw 'npm not found. Add npm to PATH and retry.'
  }

  # .env setup
  if (-not (Test-Path "$RootDir/.env") -and (Test-Path "$RootDir/.env.example")) {
    Copy-Item "$RootDir/.env.example" "$RootDir/.env"
    Write-Warn '  Created .env from .env.example — edit it to add your API key(s)'
  }

  Write-Step '[2/5] Setting up Python environment...'

  $venvPath = Join-Path $RootDir "venv"
  $venvPython = Join-Path $venvPath "Scripts\python.exe"
  
  if (-not (Test-Path $venvPath)) {
    Invoke-Expression "$pythonExe -m venv `"$venvPath`""
    Write-Host '  Created virtual environment'
  }

  if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python not found at: $venvPython"
  }

  Write-Host '  Installing Python dependencies...'
  & $venvPython -m pip install --upgrade pip --quiet
  & $venvPython -m pip install -r (Join-Path $RootDir "requirements.txt") --quiet
  Write-Host '  Python dependencies installed'

  Write-Step '[3/5] Installing frontend dependencies...'

  $frontendDir = Join-Path $RootDir "frontend"
  $nodeModulesPath = Join-Path $frontendDir "node_modules"
  
  Set-Location $frontendDir
  if (-not (Test-Path $nodeModulesPath)) {
    npm ci --silent
    Write-Host '  node_modules installed'
  } else {
    Write-Host '  node_modules already exists (skipping)'
  }
  Set-Location $RootDir

  Write-Step '[4/5] Ensuring data directories...'
  @("uploads","vectors","generated","progress","cache","courses") | ForEach-Object {
    New-Item -ItemType Directory -Force -Path "$RootDir/app-data/$_" | Out-Null
  }
  Write-Host '  Data directories ready'

  Write-Host '      Freeing required ports...' -ForegroundColor Green
  Stop-PortListeners $BackendPort
  Stop-PortListeners $FrontendPort

  Write-Step '[5/5] Starting services...'

  Write-Host "  Starting Backend on port $BackendPort..."
  $BackendProc = Start-Process -FilePath $venvPython `
    -ArgumentList '-m','uvicorn','backend.main:app','--host','0.0.0.0','--port',"$BackendPort" `
    -WorkingDirectory $RootDir `
    -PassThru `
    -NoNewWindow
  
  if ($BackendProc.HasExited) {
    throw 'Backend failed to start (process exited immediately). Check requirements.txt and backend/main.py'
  }
  
  Wait-ForPort $BackendPort 'Backend'
  Write-Host "  Backend  -> http://localhost:$BackendPort" -ForegroundColor Green
  Write-Host "  Health   -> http://localhost:$BackendPort/api/health" -ForegroundColor Green

  Write-Host "  Starting Frontend on port $FrontendPort..."
  $FrontendProc = Start-Process -FilePath 'npm' `
    -ArgumentList 'run','dev' `
    -WorkingDirectory $frontendDir `
    -PassThru `
    -NoNewWindow
  
  if ($FrontendProc.HasExited) {
    throw 'Frontend failed to start (process exited immediately). Check frontend/package.json and npm setup'
  }
  
  Wait-ForPort $FrontendPort 'Frontend'
  Write-Host "  Frontend -> http://localhost:$FrontendPort" -ForegroundColor Green

  Write-Host "`n============================================================" -ForegroundColor Green
  Write-Host '  Both services running. Press Ctrl+C to stop.' -ForegroundColor Green
  Write-Host "============================================================`n" -ForegroundColor Green

  # Keep running until user interrupts
  while ($true) {
    if ($BackendProc.HasExited) { 
      Write-Err 'Backend process exited unexpectedly.'
      exit 1
    }
    if ($FrontendProc.HasExited) { 
      Write-Err 'Frontend process exited unexpectedly.'
      exit 1
    }
    Start-Sleep -Seconds 2
  }
}
catch {
  Write-Err "`nError: $($_.Exception.Message)"
  Write-Err "$($_.InvocationInfo.PositionMessage)"
  exit 1
}
finally {
  Write-Warn "`nShutting down..."
  
  if ($FrontendProc -and -not $FrontendProc.HasExited) {
    try { 
      Stop-Process -Id $FrontendProc.Id -Force -ErrorAction SilentlyContinue
      $FrontendProc.WaitForExit(1000)
    } catch {}
  }
  
  if ($BackendProc -and -not $BackendProc.HasExited) {
    try { 
      Stop-Process -Id $BackendProc.Id -Force -ErrorAction SilentlyContinue
      $BackendProc.WaitForExit(1000)
    } catch {}
  }
  
  Write-Host 'Done.' -ForegroundColor Green
}
