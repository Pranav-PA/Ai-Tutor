# AI Semester Companion — Setup Guide

Three deployment options: **Docker** (easiest), **Linux/macOS local**, or **Windows local**.

---

## Prerequisites

### All Methods
- Git
- An OpenAI or Gemini API key

### Docker Option
- Docker & Docker Compose

### Local Options (Linux/macOS/Windows)
- Python 3.10+ (Windows recommended: 3.11 or 3.12)
- Node 18+ with npm

---

## Option 1: Docker (Recommended for Quick Start)

**Works on:** Linux, macOS, Windows (with Docker Desktop)

```bash
# Clone
git clone https://github.com/Pranav-PA/Ai-Tutor.git
cd Ai-Tutor

# Setup .env
cp .env.example .env
# Edit .env and add OPENAI_API_KEY or GEMINI_API_KEY

# Run
docker compose up --build -d

# Access:
#   Frontend: http://localhost:38173
#   Backend:  http://localhost:18080
#   Health:   http://localhost:18080/api/health

# Stop
docker compose down
```

---

## Option 2: Local (Linux / macOS)

**Works on:** Linux, macOS (Intel or Apple Silicon)

```bash
# Clone
git clone https://github.com/Pranav-PA/Ai-Tutor.git
cd Ai-Tutor

# Setup .env
cp .env.example .env
# Edit .env and add OPENAI_API_KEY or GEMINI_API_KEY

# Run (auto-installs dependencies)
chmod +x run-local.sh
./run-local.sh

# Access:
#   Frontend: http://localhost:38173
#   Backend:  http://localhost:18080
#   Health:   http://localhost:18080/api/health

# Stop: Press Ctrl+C
```

---

## Option 3: Local (Windows)

**Works on:** Windows 10/11 (PowerShell or CMD)

### Prerequisites Check
Before running, ensure:
1. **Python 3.10-3.12** is installed and in PATH (**3.11 recommended**)
   - Test: `py -3 --version` or `python --version`
   - If not in PATH: Add your Python install directory to PATH (for example, Python311)
2. **Node 18+** is installed and in PATH
   - Test: `node --version`
3. **npm** is installed and in PATH
   - Test: `npm --version`

### Steps

```powershell
# Clone
git clone https://github.com/Pranav-PA/Ai-Tutor.git
cd Ai-Tutor

# Setup .env
Copy-Item .env.example .env
# Edit .env -> add OPENAI_API_KEY or GEMINI_API_KEY

# Run (PowerShell)
.\run-local.ps1

# or run from CMD (double-click friendly)
run-local.bat

# Access:
#   Frontend: http://localhost:38173
#   Backend:  http://localhost:18080
#   Health:   http://localhost:18080/api/health

# Stop: Press Ctrl+C
```

---

## What Gets Installed

### Local Methods
- Python dependencies in `venv/` virtual environment
- Node.js packages in `frontend/node_modules/`
- SQLite database in `app-data/ai_tutor.db`
- ChromaDB vector store in `app-data/vectors/`

### Docker
- Everything in a single container image
- Data persisted in `./app-data/` volume

---

## Environment Variables

Add these to `.env`:

```
# Required: At least one
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Optional
DEFAULT_PROVIDER=openai
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-1.5-pro
```

---

## Ports

| Service | Port |
|---------|------|
| Frontend (Next.js) | 38173 |
| Backend (FastAPI) | 18080 |

If ports are already in use, the local scripts will auto-kill old processes. Docker runs in isolation.

---

## Troubleshooting

### Python not found (Windows)
```
ERROR: Python 3.10+ not found
```
**Fix:** Install Python from python.org, check "Add Python to PATH" during install, restart PowerShell.

### Node not found
```
ERROR: Node.js not found
```
**Fix:** Install Node 18+ from nodejs.org, ensure npm is also installed, restart PowerShell/terminal.

### Port already in use
```
Port XXXX busy
```
**Linux/macOS:** Script auto-kills old process. If fails, manually: `lsof -ti:XXXX | xargs kill -9`
**Windows:** Script auto-kills old process. If fails, use Task Manager to close node/python.

### Backend fails to start
Check that `requirements.txt` has all needed packages and backend directory exists.

### Frontend fails to start
Ensure `frontend/node_modules` exists and `npm run dev` works manually in the frontend directory.

---

## Data Persistence

Local methods store all data in `./app-data/`:
- `ai_tutor.db` — SQLite database
- `vectors/` — ChromaDB store
- `uploads/` — User uploads
- `progress/` — Learning progress

Files are preserved between restarts.

---

## Tips

1. **First run is slow** — venv creation, npm install, and dependencies take 2–5 minutes.
2. **Keep .env secure** — Never commit it to Git.
3. **Use `npm run dev`** — Frontend runs in hot-reload mode by default.
4. **Check logs live** — Both services print logs directly to terminal.
5. **Kill stuck processes** — `taskkill /im python.exe /f` (Windows) or `pkill -f uvicorn` (Linux/macOS).

---

## Questions?

Check backend logs if health endpoint fails:
```bash
curl http://localhost:18080/api/health
```

Check frontend in browser DevTools for UI errors.docker compose logs -f app | grep frontend
```

---

## Troubleshooting

```bash
# Check container status
docker compose ps

# Shell into the container
docker compose exec app bash

# Check health
curl http://localhost:18080/api/health
```
