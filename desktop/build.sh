#!/bin/bash
# =============================================================================
# AI Semester Companion - Desktop App Build Script
# =============================================================================
# This script builds the complete desktop application for the target platform.
# It handles: Python backend bundling, Next.js frontend export, and Electron packaging.
#
# Usage:
#   ./build.sh              # Build for current platform
#   ./build.sh --platform win    # Build for Windows
#   ./build.sh --platform mac    # Build for macOS
#   ./build.sh --platform linux  # Build for Linux
#   ./build.sh --all             # Build for all platforms
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DESKTOP_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default platform
PLATFORM="current"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --all)
            PLATFORM="all"
            shift
            ;;
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown argument: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AI Semester Companion - Desktop Build             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ==========================
# Step 1: Build Backend
# ==========================
build_backend() {
    echo -e "${YELLOW}[1/3] Building Python Backend...${NC}"
    
    cd "$BACKEND_DIR"
    
    # Create/activate virtual environment if not exists
    if [ ! -d "build_venv" ]; then
        echo "  Creating build virtual environment..."
        python3 -m venv build_venv
    fi
    
    source build_venv/bin/activate
    
    # Install dependencies
    echo "  Installing dependencies..."
    pip install --quiet -r "$PROJECT_ROOT/requirements.txt"
    pip install --quiet pyinstaller
    
    # Run PyInstaller
    echo "  Running PyInstaller..."
    pyinstaller --noconfirm backend.spec
    
    # Copy output to desktop directory
    echo "  Copying backend bundle..."
    rm -rf "$DESKTOP_DIR/backend-dist"
    cp -r "$BACKEND_DIR/dist/ai-companion-backend" "$DESKTOP_DIR/backend-dist"
    
    deactivate
    
    echo -e "${GREEN}  ✓ Backend built successfully${NC}"
}

# ==========================
# Step 2: Build Frontend
# ==========================
build_frontend() {
    echo -e "${YELLOW}[2/3] Building Frontend (Standalone)...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    echo "  Installing npm dependencies..."
    npm ci --silent 2>/dev/null || npm install --silent
    
    # Build with standalone mode
    echo "  Building Next.js standalone server..."
    BUILD_MODE=desktop npm run build
    
    # Copy standalone output to desktop directory
    echo "  Copying frontend build..."
    rm -rf "$DESKTOP_DIR/frontend-dist"
    mkdir -p "$DESKTOP_DIR/frontend-dist"
    
    # Copy the standalone server
    cp -r "$FRONTEND_DIR/.next/standalone/." "$DESKTOP_DIR/frontend-dist/"
    # Copy static assets
    cp -r "$FRONTEND_DIR/.next/static" "$DESKTOP_DIR/frontend-dist/.next/static"
    # Copy public folder
    if [ -d "$FRONTEND_DIR/public" ]; then
        cp -r "$FRONTEND_DIR/public" "$DESKTOP_DIR/frontend-dist/public"
    fi
    
    echo -e "${GREEN}  ✓ Frontend built successfully${NC}"
}

# ==========================
# Step 3: Build Electron App
# ==========================
build_electron() {
    echo -e "${YELLOW}[3/3] Building Electron Desktop App...${NC}"
    
    cd "$DESKTOP_DIR"
    
    # Install dependencies
    echo "  Installing Electron dependencies..."
    npm ci --silent 2>/dev/null || npm install --silent
    
    # Build for target platform
    case "$PLATFORM" in
        win|windows)
            echo "  Packaging for Windows..."
            npm run dist:win
            ;;
        mac|macos|darwin)
            echo "  Packaging for macOS..."
            npm run dist:mac
            ;;
        linux)
            echo "  Packaging for Linux..."
            npm run dist:linux
            ;;
        all)
            echo "  Packaging for all platforms..."
            npm run dist:all
            ;;
        current|*)
            echo "  Packaging for current platform..."
            npm run dist
            ;;
    esac
    
    echo -e "${GREEN}  ✓ Electron app packaged successfully${NC}"
}

# ==========================
# Execute Build Steps
# ==========================

if [ "$SKIP_BACKEND" != "true" ]; then
    build_backend
fi

if [ "$SKIP_FRONTEND" != "true" ]; then
    build_frontend
fi

build_electron

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Build Complete!                                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Output: ${BLUE}$DESKTOP_DIR/release/${NC}"
echo ""
ls -la "$DESKTOP_DIR/release/" 2>/dev/null || echo "  (check release directory for output files)"
