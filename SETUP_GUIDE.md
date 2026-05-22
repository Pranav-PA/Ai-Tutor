# AI Semester Companion — Setup & Deploy

Two ways to run: **Docker** (one command) or **Local** (no Docker needed).

---

## Option A: Run Locally (no Docker)

### Prerequisites

- Python 3.10+
- Node 18+ & npm
- An OpenAI or Gemini API key

### Steps

```bash
# 1. Clone
git clone https://github.com/Pranav-PA/Ai-Tutor.git
cd Ai-Tutor

# 2. Add your API key
cp .env.example .env
# Edit .env → add OPENAI_API_KEY or GEMINI_API_KEY

# 3. Run everything
chmod +x run-local.sh
./run-local.sh
```

### Windows (PowerShell / CMD)

```powershell
# 1. Clone
git clone https://github.com/Pranav-PA/Ai-Tutor.git
cd Ai-Tutor

# 2. Add your API key
Copy-Item .env.example .env
# Edit .env -> add OPENAI_API_KEY or GEMINI_API_KEY

# 3. Run everything (PowerShell)
.\run-local.ps1

# or from CMD (double-click friendly)
run-local.bat
```

This will:
- Create a Python venv and install deps
- Install frontend npm packages
- Start backend on **http://localhost:18080**
- Start frontend on **http://localhost:38173**

Press `Ctrl+C` to stop both.

---

## Option B: Docker (one container)

### Prerequisites

- Docker & Docker Compose installed on the target machine
- An OpenAI or Gemini API key

---

## Quick Start (on any laptop)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/Ai-Semister-Companion.git
cd Ai-Semister-Companion

# 2. Create your .env file from the example
cp .env.example .env
# Edit .env and add your API key(s)

# 3. Build and run
docker compose up --build -d

# That's it. Access:
#   Frontend → http://localhost:38173
#   Backend  → http://localhost:18080
#   Health   → http://localhost:18080/api/health
```

---

## Stop / Restart

```bash
# Stop
docker compose down

# Restart (no rebuild)
docker compose up -d

# Rebuild after code changes
docker compose up --build -d
```

---

## Data Persistence

All app data (SQLite DB, vector store, uploads) is stored in `./app-data/` and mounted as a Docker volume. Your data survives container rebuilds.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | — | OpenAI API key |
| `GEMINI_API_KEY` | Yes* | — | Google Gemini API key |
| `DEFAULT_PROVIDER` | No | `openai` | Which AI provider to use |
| `OPENAI_MODEL` | No | `gpt-4o` | OpenAI model name |
| `GEMINI_MODEL` | No | `gemini-1.5-pro` | Gemini model name |

*At least one API key is required.

---

## Ports

| Service | Port |
|---------|------|
| Frontend (Next.js) | `38173` |
| Backend (FastAPI) | `18080` |

---

## Logs

```bash
# Follow all logs
docker compose logs -f

# Backend only
docker compose logs -f app | grep backend

# Frontend only
docker compose logs -f app | grep frontend
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
