@echo off
REM =============================================================================
REM AI Semester Companion - Desktop App Build Script (Windows)
REM =============================================================================
REM Usage:
REM   build.bat              - Build for Windows
REM   build.bat --skip-backend  - Skip backend build
REM   build.bat --skip-frontend - Skip frontend build
REM =============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "DESKTOP_DIR=%SCRIPT_DIR%"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"
set "SKIP_BACKEND="
set "SKIP_FRONTEND="

REM Parse arguments
:parse_args
if "%1"=="" goto start_build
if "%1"=="--skip-backend" set "SKIP_BACKEND=true"
if "%1"=="--skip-frontend" set "SKIP_FRONTEND=true"
shift
goto parse_args

:start_build
echo ======================================================
echo    AI Semester Companion - Desktop Build (Windows)
echo ======================================================
echo.

REM ==========================
REM Step 1: Build Backend
REM ==========================
if defined SKIP_BACKEND goto skip_backend_step

echo [1/3] Building Python Backend...

cd /d "%BACKEND_DIR%"

REM Create virtual environment if not exists
if not exist "build_venv" (
    echo   Creating build virtual environment...
    python -m venv build_venv
)

call build_venv\Scripts\activate.bat

echo   Installing dependencies...
pip install --quiet -r "%PROJECT_ROOT%\requirements.txt"
pip install --quiet pyinstaller

echo   Running PyInstaller...
pyinstaller --noconfirm backend.spec

echo   Copying backend bundle...
if exist "%DESKTOP_DIR%\backend-dist" rmdir /s /q "%DESKTOP_DIR%\backend-dist"
xcopy /s /e /i /q "%BACKEND_DIR%\dist\ai-companion-backend" "%DESKTOP_DIR%\backend-dist"

call deactivate

echo   [OK] Backend built successfully
echo.

:skip_backend_step

REM ==========================
REM Step 2: Build Frontend
REM ==========================
if defined SKIP_FRONTEND goto skip_frontend_step

echo [2/3] Building Frontend (Static Export)...

cd /d "%FRONTEND_DIR%"

echo   Installing npm dependencies...
call npm ci --silent 2>nul || call npm install --silent

echo   Building Next.js static export...
set BUILD_MODE=desktop
call npm run build

echo   Copying frontend build...
if exist "%DESKTOP_DIR%\frontend-dist" rmdir /s /q "%DESKTOP_DIR%\frontend-dist"
xcopy /s /e /i /q "%FRONTEND_DIR%\out" "%DESKTOP_DIR%\frontend-dist"

echo   [OK] Frontend built successfully
echo.

:skip_frontend_step

REM ==========================
REM Step 3: Build Electron App
REM ==========================
echo [3/3] Building Electron Desktop App...

cd /d "%DESKTOP_DIR%"

echo   Installing Electron dependencies...
call npm ci --silent 2>nul || call npm install --silent

echo   Packaging for Windows...
call npm run dist:win

echo.
echo ======================================================
echo    Build Complete!
echo ======================================================
echo.
echo   Output: %DESKTOP_DIR%\release\
echo.
dir /b "%DESKTOP_DIR%\release\*.exe" 2>nul

pause
