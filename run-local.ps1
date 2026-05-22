$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$BackendPort = 18080
$FrontendPort = 38173

function Write-Step {
    param([string]$msg)
    Write-Host "" -ForegroundColor Green
    Write-Host $msg -ForegroundColor Green
}

function Write-Warn {
    param([string]$msg)
    Write-Host $msg -ForegroundColor Yellow
}

function Write-Err {
    param([string]$msg)
    Write-Host $msg -ForegroundColor Red
}

function Is-PortListening {
    param([int]$Port)
    $result = netstat -ano 2>$null | Select-String ":$Port\s+.*LISTENING"
    return $null -ne $result
}

function Stop-OldProcesses {
    param([int]$Port)
    
    if (Is-PortListening $Port) {
        Write-Warn "Port $Port is in use. Stopping old process..."
        $lines = netstat -ano 2>$null | Select-String ":$Port\s+.*LISTENING"
        
        foreach ($line in $lines) {
            if ($line -match '(\d+)\s*$') {
                $pid = [int]$Matches[1]
                try {
                    taskkill /pid $pid /f 2>$null | Out-Null
                    Start-Sleep -Milliseconds 500
                } catch { }
            }
        }
    }
    
    Start-Sleep -Milliseconds 500
    
    if (Is-PortListening $Port) {
        throw "Port $Port is still in use. Close other applications and retry."
    }
}

function Wait-ForPort {
    param([int]$Port, [string]$Name)
    
    for ($i = 0; $i -lt 40; $i++) {
        if (Is-PortListening $Port) {
            Write-Host "  Ready on port $Port" -ForegroundColor Green
            return
        }
        Start-Sleep -Milliseconds 500
    }
    
    throw "$Name failed to start on port $Port"
}

try {
    Write-Step "[1/5] Checking prerequisites..."
    
    $pythonExe = $null
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $pythonExe = 'py'
        $ver = & $pythonExe -3 --version 2>&1
        Write-Host "  Python: $ver"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonExe = 'python'
        $ver = & $pythonExe --version 2>&1
        Write-Host "  Python: $ver"
    } else {
        throw "Python not found. Install Python 3.10+ and ensure it is in PATH"
    }
    
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        throw "Node.js not found. Install Node 18+ and ensure it is in PATH"
    }
    Write-Host "  Node:   $(node --version)"
    
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm not found. Ensure it is in PATH"
    }
    
    if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
        Copy-Item ".env.example" ".env"
        Write-Warn "  Created .env from .env.example - edit it to add API keys"
    }
    
    Write-Step "[2/5] Setting up Python environment..."
    
    $venvPath = "venv"
    $venvPython = "$venvPath\Scripts\python.exe"
    
    if (-not (Test-Path $venvPath)) {
        if ($pythonExe -eq 'py') {
            & py -3 -m venv $venvPath
        } else {
            & python -m venv $venvPath
        }
        Write-Host "  Created virtual environment"
    }
    
    Write-Host "  Installing dependencies..."
    & $venvPython -m pip install -q --upgrade pip
    & $venvPython -m pip install -q -r requirements.txt
    Write-Host "  Python dependencies installed"
    
    Write-Step "[3/5] Installing frontend dependencies..."
    
    Push-Location frontend
    if (-not (Test-Path "node_modules")) {
        & npm ci --silent
        Write-Host "  node_modules installed"
    } else {
        Write-Host "  node_modules already exists"
    }
    Pop-Location
    
    Write-Step "[4/5] Ensuring data directories..."
    
    @("uploads", "vectors", "generated", "progress", "cache", "courses") | ForEach-Object {
        New-Item -ItemType Directory -Force -Path "app-data\$_" | Out-Null
    }
    Write-Host "  Data directories ready"
    
    Write-Host "  Freeing required ports..." -ForegroundColor Green
    Stop-OldProcesses $BackendPort
    Stop-OldProcesses $FrontendPort
    
    Write-Step "[5/5] Starting services..."
    
    Write-Host "  Starting Backend on port $BackendPort..."
    $backendArgs = @("-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "$BackendPort")
    $backendProc = Start-Process -FilePath $venvPython -ArgumentList $backendArgs -WorkingDirectory $RootDir -PassThru -NoNewWindow
    
    Start-Sleep -Seconds 2
    if ($backendProc.HasExited) {
        throw "Backend failed to start. Check Python dependencies and backend/main.py"
    }
    
    Wait-ForPort $BackendPort "Backend"
    Write-Host "  Backend  -> http://localhost:$BackendPort" -ForegroundColor Green
    Write-Host "  Health   -> http://localhost:$BackendPort/api/health" -ForegroundColor Green
    
    Write-Host "  Starting Frontend on port $FrontendPort..."
    Push-Location frontend
    $frontendProc = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -PassThru -NoNewWindow
    Pop-Location
    
    Start-Sleep -Seconds 2
    if ($frontendProc.HasExited) {
        throw "Frontend failed to start. Check frontend/package.json"
    }
    
    Wait-ForPort $FrontendPort "Frontend"
    Write-Host "  Frontend -> http://localhost:$FrontendPort" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  Both services running. Press Ctrl+C to stop." -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    
    while ($true) {
        if ($backendProc.HasExited) {
            Write-Err "Backend process exited"
            exit 1
        }
        if ($frontendProc.HasExited) {
            Write-Err "Frontend process exited"
            exit 1
        }
        Start-Sleep -Seconds 2
    }
}
catch {
    Write-Err ""
    Write-Err "Error: $($_.Exception.Message)"
    exit 1
}
finally {
    Write-Warn ""
    Write-Warn "Shutting down..."
    
    if ($backendProc -and -not $backendProc.HasExited) {
        try {
            $backendProc.Kill()
        } catch { }
    }
    
    if ($frontendProc -and -not $frontendProc.HasExited) {
        try {
            $frontendProc.Kill()
        } catch { }
    }
    
    Write-Host "Done." -ForegroundColor Green
}
