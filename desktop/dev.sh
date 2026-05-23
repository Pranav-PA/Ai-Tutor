#!/bin/bash
# =============================================================================
# AI Semester Companion - Development Runner
# =============================================================================
# Starts all services for desktop development:
#   1. Python backend (port 18080)
#   2. Next.js frontend dev server (port 38173)
#   3. Electron app (connects to above)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting AI Semester Companion (Development Mode)${NC}"
echo ""

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    wait 2>/dev/null
    echo -e "${GREEN}All services stopped.${NC}"
}
trap cleanup EXIT INT TERM

# Start backend
echo -e "${YELLOW}[1/3] Starting Backend (port 18080)...${NC}"
cd "$PROJECT_ROOT"
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

HOST=127.0.0.1 PORT=18080 DESKTOP_MODE=true python -m uvicorn backend.main:app --host 127.0.0.1 --port 18080 --reload &
BACKEND_PID=$!
echo -e "  Backend PID: $BACKEND_PID"

# Wait for backend to start
echo -e "  Waiting for backend..."
for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:18080/ > /dev/null 2>&1; then
        echo -e "  ${GREEN}Backend ready!${NC}"
        break
    fi
    sleep 1
done

# Start frontend
echo -e "${YELLOW}[2/3] Starting Frontend (port 38173)...${NC}"
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
echo -e "  Frontend PID: $FRONTEND_PID"

# Wait a moment for frontend
sleep 3

# Start Electron
echo -e "${YELLOW}[3/3] Starting Electron App...${NC}"
cd "$SCRIPT_DIR"
npm run dev &
ELECTRON_PID=$!

echo ""
echo -e "${GREEN}All services running:${NC}"
echo -e "  Backend:  http://127.0.0.1:18080"
echo -e "  Frontend: http://localhost:38173"
echo -e "  Electron: Running (dev mode)"
echo ""
echo -e "Press Ctrl+C to stop all services."
echo ""

# Wait for any process to exit
wait
