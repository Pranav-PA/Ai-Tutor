#!/bin/bash

################################################################################
# AI Semester Companion - Complete Setup and Run Script
# 
# This script automates the entire setup process for the AI Semester Companion
# application, including dependency installation and service startup.
#
# Usage: ./setup-and-run.sh [--setup-only] [--no-build]
#   --setup-only   : Only install dependencies, don't start services
#   --no-build     : Skip Next.js build, only run dev server
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SETUP_ONLY=false
NO_BUILD=false
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --setup-only)
      SETUP_ONLY=true
      shift
      ;;
    --no-build)
      NO_BUILD=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--setup-only] [--no-build]"
      exit 1
      ;;
  esac
done

################################################################################
# Helper Functions
################################################################################

print_banner() {
  echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║  AI Semester Companion - Setup & Run Script               ║${NC}"
  echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
  echo ""
}

print_step() {
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}▶ $1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

check_command() {
  if ! command -v "$1" &> /dev/null; then
    print_error "$1 is not installed"
    return 1
  fi
  print_success "$1 found"
  return 0
}

wait_for_port() {
  local port=$1
  local timeout=$2
  local elapsed=0
  
  echo "Waiting for port $port to be ready (timeout: ${timeout}s)..."
  
  while [ $elapsed -lt $timeout ]; do
    if nc -z localhost $port 2>/dev/null; then
      echo "✓ Port $port is ready"
      return 0
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done
  
  print_warning "Port $port not responding after ${timeout}s"
  return 1
}

################################################################################
# Prerequisites Check
################################################################################

print_banner

print_step "Checking Prerequisites"

echo "Checking for required tools..."
PREREQ_MET=true

check_command "python3" || PREREQ_MET=false
check_command "pip" || PREREQ_MET=false
check_command "node" || PREREQ_MET=false
check_command "npm" || PREREQ_MET=false

if [ "$PREREQ_MET" = false ]; then
  print_error "Missing required prerequisites"
  echo ""
  echo "Please install:"
  echo "  • Python 3.7+ (with pip)"
  echo "  • Node.js LTS (with npm)"
  echo ""
  exit 1
fi

print_success "All prerequisites met"
echo ""

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  print_warning ".env file not found, creating from .env.example"
  if [ -f "$SCRIPT_DIR/.env.example" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    print_success ".env file created from .env.example"
    echo "⚠️  Please update .env with your API keys (OPENAI_API_KEY, GEMINI_API_KEY)"
  else
    print_error ".env.example not found"
    exit 1
  fi
else
  print_success ".env file exists"
fi

echo ""

################################################################################
# Backend Setup
################################################################################

print_step "Setting Up Backend"

cd "$SCRIPT_DIR"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
print_success "Python version: $PYTHON_VERSION"

# Create/activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
  print_success "Virtual environment created"
else
  print_success "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
if pip install -r requirements.txt; then
  print_success "Python dependencies installed"
else
  print_error "Failed to install Python dependencies"
  exit 1
fi

# Verify backend imports
echo "Verifying backend setup..."
if python3 -c "from backend.main import app; print('Backend import successful')" 2>&1 | grep -q "successful"; then
  print_success "Backend imports verified"
else
  print_error "Backend import failed"
  exit 1
fi

echo ""

################################################################################
# Frontend Setup
################################################################################

print_step "Setting Up Frontend"

cd "$SCRIPT_DIR/frontend"

# Install npm dependencies
echo "Installing npm dependencies..."
if npm install --legacy-peer-deps --quiet; then
  print_success "npm dependencies installed"
else
  print_error "Failed to install npm dependencies"
  exit 1
fi

# Build frontend (unless --no-build flag is set)
if [ "$NO_BUILD" = false ]; then
  echo "Building Next.js application..."
  if npm run build; then
    print_success "Frontend build successful"
  else
    print_warning "Frontend build failed (will use dev server instead)"
  fi
else
  print_warning "Skipping Next.js build (--no-build flag set)"
fi

echo ""

################################################################################
# Setup Complete - Either End or Start Services
################################################################################

if [ "$SETUP_ONLY" = true ]; then
  print_step "Setup Complete"
  echo ""
  echo "Setup completed successfully! To start the application, run:"
  echo ""
  echo "  cd \"$SCRIPT_DIR\""
  echo "  source venv/bin/activate"
  echo "  ./run.sh"
  echo ""
  exit 0
fi

################################################################################
# Start Services
################################################################################

print_step "Starting Services"
echo ""

cd "$SCRIPT_DIR"

# Kill any existing processes on our ports (cleanup)
echo "Cleaning up existing processes on ports 18080 and 38173..."
lsof -ti :18080 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti :38173 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend in background
echo "Starting backend on http://localhost:18080..."
source venv/bin/activate
python3 -m backend.main > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
print_success "Backend PID: $BACKEND_PID"

# Wait for backend to be ready
sleep 2
if ! wait_for_port 18080 10; then
  print_error "Backend failed to start. Check /tmp/backend.log"
  cat /tmp/backend.log
  exit 1
fi

# Test backend health
echo "Testing backend health..."
if curl -s http://localhost:18080/api/health | grep -q "healthy\|ok\|health"; then
  print_success "Backend health check passed"
else
  print_warning "Backend health check returned unexpected response"
fi

echo ""

# Start frontend
echo "Starting frontend on http://localhost:38173..."
cd "$SCRIPT_DIR/frontend"

if npm run dev &
then
  FRONTEND_PID=$!
  print_success "Frontend started (PID: $FRONTEND_PID)"
else
  print_error "Failed to start frontend"
  kill $BACKEND_PID 2>/dev/null || true
  exit 1
fi

echo ""

################################################################################
# Success Summary
################################################################################

print_step "🎉 Application Started Successfully!"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:18080"
echo -e "${GREEN}Frontend: http://localhost:38173${NC}"
echo ""
echo "API Documentation: http://localhost:18080/docs"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo "  Backend: tail -f /tmp/backend.log"
echo "  Frontend: above output"
echo ""
echo "To stop the services:"
echo "  • Press Ctrl+C to stop frontend"
echo "  • Run: kill $BACKEND_PID (in another terminal)"
echo ""

# Keep the script running to show output
wait

################################################################################
# Cleanup on Exit
################################################################################

trap 'print_warning "Shutting down services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' EXIT
