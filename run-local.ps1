$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$BackendPort = 18080
$FrontendPort = 38173

function Write-Step {
    param([string]$msg)
    Write-Host ""
    Write-Host $msg -ForegroundColor Green
}

function Write-Err {
    param([string]$msg)
    Write-Host $msg -ForegroundColor Red
}

function Write-Warn {
    param([string]$msg)
    Write-Host $msg -ForegroundColor Yellow
}

try {
    Write-Step "[1/5] Checking prerequisites..."
    
    $pythonCmd = ""
    
    try {
        $output = py -3 --version 2>&1
        $pythonCmd = "py -3"
        Write-Host "  Python: $output"
    } catch {
        try {
            $output = python --version 2>&1
            $pythonCmd = "python"
            Write-Host "  Python: $output"
        } catch {
            throw "Python 3.10+ not found. Install Python and ensure it is in PATH."
        }
    }
    
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        throw "Node.js not found. Install Node 18+ and add to PATH."
    }
    Write-Host "  Node:   $(node --version)"
    
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm not found. Add to PATH."
    }
    
    if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
        Copy-Item ".env.example" ".env"
        Write-Warn "  Created .env - edit to add API keys"
    }
    
    Write-Step "[2/5] Setting up Python environment..."
    
    if (-not (Test-Path "venv")) {
        Write-Host "  Creating virtual environment..."
        $cmd = "$pythonCmd -m venv venv"
        Invoke-Expression $cmd | Out-Null
    }
    
    $venvPython = "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment failed. Check Python installation."
    }
    
    Write-Host "  Installing dependencies..."
    & $venvPython -m pip install --upgrade pip -q
    & $venvPython -m pip install -r requirements.txt -q
    Write-Host "  Dependencies installed"
    
    Write-Step "[3/5] Installing frontend dependencies..."
    
    Set-Location frontend
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Installing npm packages..."
        npm ci --silent
    } else {
        Write-Host "  node_modules exists"
    }
    Set-Location ..
    
    Write-Step "[4/5] Ensuring data directories..."
    
    @("uploads", "vectors", "generated", "progress", "cache", "courses") | ForEach-Object {
        New-Item -ItemType Directory -Force -Path "app-data\$_" | Out-Null
    }
    Write-Host "  Directories ready"
    
    Write-Host "  Checking ports..." -ForegroundColor Green
    
    $connected = netstat -ano 2>$null | Select-String ":$BackendPort\s+.*LISTENING"
    if ($connected) {
        Write-Warn "    Port $BackendPort busy, stopping old process..."
        foreach ($line in $connected) {
            if ($line -match '(\d+)\s*$') {
                taskkill /pid $Matches[1] /f 2>$null | Out-Null
            }
        }
        Start-Sleep -Seconds 1
    }
    
    $connected = netstat -ano 2>$null | Select-String ":$FrontendPort\s+.*LISTENING"
    if ($connected) {
        Write-Warn "    Port $FrontendPort busy, stopping old process..."
        foreach ($line in $connected) {
            if ($line -match '(\d+)\s*$') {
                taskkill /pid $Matches[1] /f 2>$null | Out-Null
            }
        }
        Start-Sleep -Seconds 1
    }
    
    Write-Step "[5/5] Starting services..."
    
    Write-Host "  Starting Backend..."
    $backendProc = Start-Process -FilePath $venvPython -ArgumentList @("-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "$BackendPort") -WorkingDirectory $RootDir -PassThru -NoNewWindow
    
    Start-Sleep -Seconds 3
    if ($backendProc.HasExited) {
        throw "Backend failed to start"
    }
    
    $listening = $false
    for ($i = 0; $i -lt 30; $i++) {
        $result = netstat -ano 2>$null | Select-String ":$BackendPort\s+.*LISTENING"
        if ($result) {
            $listening = $true
            break
        }
        Start-Sleep -Milliseconds 500
    }
    
    if (-not $listening) {
        throw "Backend not listening on port $BackendPort"
    }
    
    Write-Host "  Backend started on http://localhost:$BackendPort" -ForegroundColor Green
    
    Write-Host "  Starting Frontend..."
    $env:SHELL = "cmd.exe"
    Set-Location frontend
    $frontendProc = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -PassThru -NoNewWindow
    Set-Location ..
    
    Start-Sleep -Seconds 3
    if ($frontendProc.HasExited) {
        throw "Frontend failed to start"
    }
    
    $listening = $false
    for ($i = 0; $i -lt 30; $i++) {
        $result = netstat -ano 2>$null | Select-String ":$FrontendPort\s+.*LISTENING"
        if ($result) {
            $listening = $true
            break
        }
        Start-Sleep -Milliseconds 500
    }
    
    if (-not $listening) {
        throw "Frontend not listening on port $FrontendPort"
    }
    
    Write-Host "  Frontend started on http://localhost:$FrontendPort" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  Both services running." -ForegroundColor Green
    Write-Host "  Backend  -> http://localhost:$BackendPort/api/health" -ForegroundColor Green
    Write-Host "  Frontend -> http://localhost:$FrontendPort" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Press Ctrl+C to stop" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    
    while ($true) {
        if ($backendProc.HasExited) {
            Write-Err "Backend exited"
            exit 1
        }
        if ($frontendProc.HasExited) {
            Write-Err "Frontend exited"
            exit 1
        }
        Start-Sleep -Seconds 2
    }
}
catch {
    Write-Err ""
    Write-Err "ERROR: $($_.Exception.Message)"
    Write-Err ""
    exit 1
}
finally {
    Write-Warn ""
    Write-Warn "Shutting down..."
    
    if ($backendProc -and -not $backendProc.HasExited) {
        $backendProc.Kill() 2>$null
    }
    
    if ($frontendProc -and -not $frontendProc.HasExited) {
        $frontendProc.Kill() 2>$null
    }
    
    Write-Host "Done." -ForegroundColor Green
}
