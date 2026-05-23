<# 
.SYNOPSIS
    AI Semester Companion - Windows Desktop Build Script
.DESCRIPTION
    Builds the complete desktop application for Windows (.exe installer)
#>

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$DesktopOnly
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$DesktopDir = Split-Path -Parent $ScriptDir  # desktop/ directory
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

function Write-Step($msg) { Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Write-Ok($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

function Test-Prerequisites {
    Write-Step "Checking prerequisites..."
    
    # Python
    try {
        $pyVersion = python --version 2>&1
        Write-Step "Python: $pyVersion"
    } catch {
        Write-Err "Python 3.9+ is required. Download from https://python.org"
        exit 1
    }
    
    # Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Step "Node.js: $nodeVersion"
    } catch {
        Write-Err "Node.js 18+ is required. Download from https://nodejs.org"
        exit 1
    }
    
    Write-Ok "All prerequisites met"
}

function Build-Backend {
    Write-Step "Building Python backend..."
    
    Set-Location $BackendDir
    
    # Create virtual environment
    if (-not (Test-Path "build-venv")) {
        python -m venv build-venv
    }
    
    # Activate and install
    & "build-venv\Scripts\Activate.ps1"
    
    Write-Step "Installing Python dependencies..."
    pip install --upgrade pip setuptools wheel | Out-Null
    pip install -r "$ProjectRoot\requirements.txt" | Out-Null
    pip install pyinstaller | Out-Null
    
    # Run PyInstaller
    Write-Step "Running PyInstaller..."
    pyinstaller --noconfirm backend.spec
    
    # Copy output
    $outputDir = Join-Path $DesktopDir "backend-dist"
    if (Test-Path $outputDir) { Remove-Item $outputDir -Recurse -Force }
    Copy-Item -Path "dist\ai-companion-backend" -Destination $outputDir -Recurse
    
    deactivate
    Write-Ok "Backend built successfully"
}

function Build-Frontend {
    Write-Step "Building frontend..."
    
    Set-Location $FrontendDir
    
    Write-Step "Installing frontend dependencies..."
    npm ci | Out-Null
    
    Write-Step "Building static export..."
    $env:BUILD_MODE = "desktop"
    npm run build
    
    # Copy output
    $outputDir = Join-Path $DesktopDir "frontend-dist"
    if (Test-Path $outputDir) { Remove-Item $outputDir -Recurse -Force }
    
    $outDir = Join-Path $FrontendDir "out"
    if (Test-Path $outDir) {
        Copy-Item -Path $outDir -Destination $outputDir -Recurse
    } else {
        Write-Warn "Static export 'out' dir not found, frontend will be served from backend"
        New-Item -ItemType Directory -Path $outputDir | Out-Null
    }
    
    Write-Ok "Frontend built successfully"
}

function Build-Desktop {
    Write-Step "Building Electron desktop app..."
    
    Set-Location $DesktopDir
    
    Write-Step "Installing Electron dependencies..."
    npm ci | Out-Null
    
    Write-Step "Packaging application..."
    npx electron-builder --win
    
    Write-Ok "Desktop app built successfully!"
    Write-Step "Output: $DesktopDir\release\"
    Get-ChildItem "$DesktopDir\release\" -ErrorAction SilentlyContinue
}

# Main
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  AI Semester Companion - Windows Build" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Test-Prerequisites

if ($BackendOnly) {
    Build-Backend
} elseif ($FrontendOnly) {
    Build-Frontend
} elseif ($DesktopOnly) {
    Build-Desktop
} else {
    Build-Backend
    Write-Host ""
    Build-Frontend
    Write-Host ""
    Build-Desktop
    Write-Host ""
    Write-Ok "========================================"
    Write-Ok "  Build complete!"
    Write-Ok "  Check: $DesktopDir\release\"
    Write-Ok "========================================"
}
