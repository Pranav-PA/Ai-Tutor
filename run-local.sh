#!/bin/bash
###############################################################################
# AI Semester Companion — Run without Docker
# Requirements: Python 3.10+, Node 18+, npm
# Usage: ./run-local.sh
###############################################################################
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

cleanup() {
  echo -e "\n${YELLOW}Shutting down...${NC}"
  [[ -n "$BACKEND_PID" ]] && kill "$BACKEND_PID" 2>/dev/null
  [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null
  wait 2>/dev/null
  echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT INT TERM

# ─── Preflight checks ────────────────────────────────────────────────────────
echo -e "${GREEN}[1/5] Checking prerequisites...${NC}"

if ! command -v python3 &>/dev/null; then
  echo -e "${RED}python3 not found. Install Python 3.10+${NC}" && exit 1
fi
if ! command -v node &>/dev/null; then
  echo -e "${RED}node not found. Install Node 18+${NC}" && exit 1
fi
if ! command -v npm &>/dev/null; then
  echo -e "${RED}npm not found. Install npm${NC}" && exit 1
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  Python: $PYTHON_VER"
echo "  Node:   $(node --version)"

# ─── .env check ──────────────────────────────────────────────────────────────
if [ ! -f "$ROOT_DIR/.env" ]; then
  if [ -f "$ROOT_DIR/.env.example" ]; then
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    echo -e "${YELLOW}  Created .env from .env.example — edit it to add your API key(s)${NC}"
  fi
fi

# ─── Python venv + dependencies ──────────────────────────────────────────────
echo -e "${GREEN}[2/5] Setting up Python environment...${NC}"

if [ ! -d "$ROOT_DIR/venv" ]; then
  python3 -m venv "$ROOT_DIR/venv"
  echo "  Created virtual environment"
fi

source "$ROOT_DIR/venv/bin/activate"
pip install -q --upgrade pip
pip install -q -r "$ROOT_DIR/requirements.txt"
echo "  Python dependencies installed"

# ─── Frontend dependencies ────────────────────────────────────────────────────
echo -e "${GREEN}[3/5] Installing frontend dependencies...${NC}"

cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm ci --silent || npm install --silent
  echo "  node_modules installed"
else
  echo "  node_modules already exists (skipping)"
fi
cd "$ROOT_DIR"

# ─── Create data directories ─────────────────────────────────────────────────
echo -e "${GREEN}[4/5] Ensuring data directories...${NC}"
mkdir -p app-data/{uploads,vectors,generated,progress,cache,courses}

# ─── Start services ──────────────────────────────────────────────────────────
echo -e "${GREEN}[5/5] Starting services...${NC}"
echo ""

# Backend
source "$ROOT_DIR/venv/bin/activate"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 18080 &
BACKEND_PID=$!
echo -e "  ${GREEN}Backend${NC}  → http://localhost:18080"
echo -e "  ${GREEN}Health${NC}   → http://localhost:18080/api/health"

# Frontend (dev mode — no build step needed)
cd "$ROOT_DIR/frontend"
npx next dev -p 38173 &
FRONTEND_PID=$!
cd "$ROOT_DIR"
echo -e "  ${GREEN}Frontend${NC} → http://localhost:38173"

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Both services running. Press Ctrl+C to stop.${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""

# Wait for either to exit
wait
