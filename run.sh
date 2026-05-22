#!/bin/bash

################################################################################
# AI Semester Companion - Run Services Script
# 
# This script starts both backend and frontend services.
# Run this after initial setup.sh has been executed.
#
# Usage: ./run.sh
################################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

################################################################################
# Helper Functions
################################################################################

print_banner() {
  echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║  AI Semester Companion - Run Services                    ║${NC}"
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
# Check Prerequisites
################################################################################

print_banner

print_step "Checking Prerequisites"

# Check virtual environment
if [ ! -d "$SCRIPT_DIR/venv" ]; then
  print_error "Virtual environment not found. Please run setup-and-run.sh first."
  exit 1
fi

print_success "Virtual environment found"

# Check Environment file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  print_error ".env file not found. Please run setup-and-run.sh first."
  exit 1
fi

print_success ".env file exists"
echo ""

################################################################################
# Start Backend
################################################################################

print_step "Starting Backend Service"

cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes on port 18080
echo "Cleaning up port 18080..."
lsof -ti :18080 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend
echo "Starting backend on http://localhost:18080..."
python3 -m backend.main > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
export BACKEND_PID
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

################################################################################
# Start Frontend
################################################################################

print_step "Starting Frontend Service"

cd "$SCRIPT_DIR/frontend"

# Kill any existing processes on port 38173
echo "Cleaning up port 38173..."
lsof -ti :38173 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Start frontend
echo "Starting frontend on http://localhost:38173..."
if npm run dev &
then
  FRONTEND_PID=$!
  export FRONTEND_PID
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

print_step "🎉 Services Started Successfully!"
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

# Keep the script running to show frontend output
wait

################################################################################
# Cleanup on Exit
################################################################################

trap 'print_warning "Shutting down services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' EXIT
