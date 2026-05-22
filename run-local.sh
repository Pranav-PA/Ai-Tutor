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

BACKEND_PORT=18080
FRONTEND_PORT=38173

kill_port_listeners() {
  local port="$1"
  local pids=""

  if command -v fuser &>/dev/null; then
    if fuser -n tcp "$port" >/dev/null 2>&1; then
      echo -e "${YELLOW}  Port $port busy → stopping with fuser${NC}"
      fuser -k -n tcp "$port" >/dev/null 2>&1 || true
      sleep 1
    fi
  fi

  if command -v lsof &>/dev/null; then
    pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
  else
    pids=$(ss -ltnp 2>/dev/null | grep -E ":$port[[:space:]]" | grep -o 'pid=[0-9]*' | cut -d= -f2 | sort -u || true)
  fi

  if [ -n "$pids" ]; then
    echo -e "${YELLOW}  Port $port busy → stopping old process(es): $pids${NC}"
    kill $pids 2>/dev/null || true
    sleep 1
  fi

  local still_busy=""
  if command -v lsof &>/dev/null; then
    still_busy=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
  else
    still_busy=$(ss -ltnp 2>/dev/null | awk -v p=":$port" '$4 ~ p {print $0}')
  fi

  if [ -n "$still_busy" ]; then
    echo -e "${RED}  Port $port is still in use. Stop the conflicting process and retry.${NC}"
    exit 1
  fi
}

wait_for_port() {
  local port="$1"
  local name="$2"
  local retries=20

  for _ in $(seq 1 "$retries"); do
    if ss -ltn 2>/dev/null | grep -qE ":$port[[:space:]]"; then
      return 0
    fi
    sleep 0.5
  done

  echo -e "${RED}${name} failed to bind on port $port.${NC}"
  return 1
}

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

if [ ! -f "$ROOT_DIR/requirements.txt" ]; then
  echo -e "${RED}requirements.txt not found. Run from the project root directory.${NC}"
  exit 1
fi

source "$ROOT_DIR/venv/bin/activate"
echo "  Installing pip upgrade..."
pip install --upgrade pip || { echo -e "${RED}pip upgrade failed${NC}"; exit 1; }
echo "  Installing requirements..."
pip install -r "$ROOT_DIR/requirements.txt" || { echo -e "${RED}requirements install failed${NC}"; exit 1; }
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

echo -e "${GREEN}      Freeing required ports...${NC}"
pkill -f "next.*$FRONTEND_PORT" 2>/dev/null || true
pkill -f "uvicorn.*$BACKEND_PORT" 2>/dev/null || true
kill_port_listeners "$BACKEND_PORT"
kill_port_listeners "$FRONTEND_PORT"

# ─── Start services ──────────────────────────────────────────────────────────
echo -e "${GREEN}[5/5] Starting services...${NC}"
echo ""

# Backend
source "$ROOT_DIR/venv/bin/activate"
python -m uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!
sleep 1
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo -e "${RED}Backend failed to start.${NC}"
  exit 1
fi
wait_for_port "$BACKEND_PORT" "Backend" || exit 1
echo -e "  ${GREEN}Backend${NC}  → http://localhost:${BACKEND_PORT}"
echo -e "  ${GREEN}Health${NC}   → http://localhost:${BACKEND_PORT}/api/health"

# Frontend (dev mode — no build step needed)
cd "$ROOT_DIR/frontend"
npx next dev -p "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$ROOT_DIR"
sleep 1
if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
  echo -e "${RED}Frontend failed to start.${NC}"
  exit 1
fi
wait_for_port "$FRONTEND_PORT" "Frontend" || exit 1
echo -e "  ${GREEN}Frontend${NC} → http://localhost:${FRONTEND_PORT}"

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Both services running. Press Ctrl+C to stop.${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
echo ""

# Wait for either to exit
wait
