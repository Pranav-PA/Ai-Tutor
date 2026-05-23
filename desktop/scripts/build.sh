#!/bin/bash
# =============================================================================
# AI Semester Companion - Full Desktop Build Script
# Builds the application for the current platform (Linux/macOS)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DESKTOP_DIR="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Linux*)  PLATFORM="linux";;
        Darwin*) PLATFORM="mac";;
        *)       PLATFORM="unknown";;
    esac
    log_info "Detected platform: $PLATFORM"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Python 3.9+
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3.9+ is required but not found"
        exit 1
    fi
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    log_info "Python version: $PYTHON_VERSION"
    
    # Node.js 18+
    if ! command -v node &> /dev/null; then
        log_error "Node.js 18+ is required but not found"
        exit 1
    fi
    NODE_VERSION=$(node --version)
    log_info "Node.js version: $NODE_VERSION"
    
    # npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not found"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Build the Python backend with PyInstaller
build_backend() {
    log_info "Building Python backend..."
    
    cd "$BACKEND_DIR"
    
    # Create/activate virtual environment
    if [ ! -d "build-venv" ]; then
        python3 -m venv build-venv
    fi
    source build-venv/bin/activate
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    pip install -r "$PROJECT_ROOT/requirements.txt" > /dev/null 2>&1
    pip install pyinstaller > /dev/null 2>&1
    
    # Run PyInstaller
    log_info "Running PyInstaller..."
    pyinstaller --noconfirm backend.spec
    
    # Copy output to desktop dir
    rm -rf "$DESKTOP_DIR/backend-dist"
    cp -r "$BACKEND_DIR/dist/ai-companion-backend" "$DESKTOP_DIR/backend-dist"
    
    deactivate
    log_success "Backend built successfully"
}

# Build the Next.js frontend as static export
build_frontend() {
    log_info "Building frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    log_info "Installing frontend dependencies..."
    npm ci > /dev/null 2>&1
    
    # Build with static export mode
    log_info "Building static export..."
    BUILD_MODE=desktop npm run build
    
    # Copy the exported output
    rm -rf "$DESKTOP_DIR/frontend-dist"
    
    # Next.js static export goes to 'out' directory
    if [ -d "$FRONTEND_DIR/out" ]; then
        cp -r "$FRONTEND_DIR/out" "$DESKTOP_DIR/frontend-dist"
    else
        # Fallback: copy .next/static and create basic structure
        mkdir -p "$DESKTOP_DIR/frontend-dist"
        cp -r "$FRONTEND_DIR/.next/static" "$DESKTOP_DIR/frontend-dist/_next/static" 2>/dev/null || true
        log_warn "Static export not found, frontend will be served from backend"
    fi
    
    log_success "Frontend built successfully"
}

# Build the Electron desktop app
build_desktop() {
    log_info "Building Electron desktop app..."
    
    cd "$DESKTOP_DIR"
    
    # Install dependencies
    log_info "Installing Electron dependencies..."
    npm ci > /dev/null 2>&1
    
    # Build for current platform
    log_info "Packaging application..."
    case "$PLATFORM" in
        linux)
            npx electron-builder --linux AppImage deb
            ;;
        mac)
            npx electron-builder --mac dmg
            ;;
        *)
            log_error "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac
    
    log_success "Desktop app built successfully!"
    log_info "Output: $DESKTOP_DIR/release/"
    ls -la "$DESKTOP_DIR/release/" 2>/dev/null || true
}

# Main build pipeline
main() {
    echo "=============================================="
    echo "  AI Semester Companion - Desktop Build"
    echo "=============================================="
    echo ""
    
    detect_platform
    check_prerequisites
    
    echo ""
    log_info "Starting build pipeline..."
    echo ""
    
    # Step 1: Build backend
    build_backend
    echo ""
    
    # Step 2: Build frontend
    build_frontend
    echo ""
    
    # Step 3: Build desktop app
    build_desktop
    echo ""
    
    log_success "========================================"
    log_success "  Build complete!"
    log_success "  Check: $DESKTOP_DIR/release/"
    log_success "========================================"
}

# Parse arguments
case "${1:-}" in
    --backend-only)
        detect_platform
        build_backend
        ;;
    --frontend-only)
        detect_platform
        build_frontend
        ;;
    --desktop-only)
        detect_platform
        build_desktop
        ;;
    *)
        main
        ;;
esac
