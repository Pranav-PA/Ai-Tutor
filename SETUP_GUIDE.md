# AI Semester Companion — Docker Setup

Single-image Docker build. Backend (FastAPI) + Frontend (Next.js) in one container. No Postgres, no Redis — uses SQLite + ChromaDB.

---

## Prerequisites

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
