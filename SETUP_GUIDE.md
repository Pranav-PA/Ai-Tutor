# AI Semester Companion - Setup & Deployment Guide

This document provides comprehensive setup instructions for deploying the AI Semester Companion application.

## 📋 Quick Reference

| Command | Purpose |
|---------|---------|
| `./setup-and-run.sh` | ⭐ **First time?** Complete setup + start services |
| `./setup-and-run.sh --setup-only` | Install dependencies only (don't start services) |
| `./run.sh` | Run services after initial setup |
| `./run.sh --no-build` | Start without rebuilding frontend |

---

## 🚀 Option 1: Automated Setup (Recommended)

### For New Users

```bash
# Clone the repository
git clone https://github.com/yourusername/Ai-Semister-Companion.git
cd Ai-Semister-Companion

# Make scripts executable
chmod +x setup-and-run.sh run.sh

# Run everything with one command
./setup-and-run.sh
```

**What happens automatically:**
1. Checks for Python 3.11+ and Node.js 18+
2. Creates Python virtual environment
3. Installs all Python packages (70+ dependencies)
4. Installs all npm packages (600+ dependencies)
5. Builds Next.js frontend
6. Starts backend on http://localhost:18080
7. Starts frontend on http://localhost:38173

**Expected output:**
```
╔════════════════════════════════════════════════════════════╗
║  AI Semester Companion - Setup & Run Script               ║
╚════════════════════════════════════════════════════════════╝

✓ Backend: http://localhost:18080
✓ Frontend: http://localhost:38173
✓ API Documentation: http://localhost:18080/docs
```

### For Subsequent Runs

After the initial setup, use:

```bash
./run.sh
```

This will:
- Activate virtual environment
- Start backend on port 18080
- Start frontend on port 38173
- Show logs and URLs

---

## 🔧 Option 2: Manual Setup

### Step 1: Prerequisites

Verify you have the required tools:

```bash
# Check Python version (3.11+)
python3 --version

# Check Node.js version (18+)
node --version

# Check npm version
npm --version
```

If any are missing:
- **Python**: Download from https://www.python.org/
- **Node.js**: Download from https://nodejs.org/

### Step 2: Clone & Setup Backend

```bash
# Clone repository
git clone https://github.com/yourusername/Ai-Semister-Companion.git
cd Ai-Semister-Companion

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate        # Linux/Mac
# or
venv\Scripts\activate           # Windows

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Setup Frontend

```bash
cd frontend

# Install npm dependencies
npm install --legacy-peer-deps

# Build frontend (recommended)
npm run build

cd ..
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
# Linux/Mac:
nano .env

# Windows:
notepad .env

# Add your API keys:
# OPENAI_API_KEY=sk-your-key-here
# GEMINI_API_KEY=AIza-your-key-here
# DEFAULT_PROVIDER=openai
```

### Step 5: Run Services

**Option A: Run Both Together (Terminal 1)**
```bash
cd /path/to/Ai-Semister-Companion
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m backend.main
```

**Option B: Run Separately**

Terminal 1 (Backend):
```bash
source venv/bin/activate
python -m backend.main
# Output: INFO:uvicorn.server: Uvicorn running on http://0.0.0.0:18080
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
# Output: ▲ Next.js 15.5.18
#         Local: http://localhost:38173
```

---

## 🌐 Accessing the Application

Once both services are running:

- **Frontend (UI)**: http://localhost:38173
- **Backend API**: http://localhost:18080/api
- **API Documentation**: http://localhost:18080/docs (Swagger UI)
- **API Schema**: http://localhost:18080/openapi.json

---

## 🗂️ Project Structure

```
Ai-Semister-Companion/
├── setup-and-run.sh         # ⭐ One-command setup script
├── run.sh                   # Run services script
├── requirements.txt         # Python dependencies (70+ packages)
├── .env.example             # Environment template
├── .env                     # Your configuration (create from .env.example)
│
├── backend/                 # FastAPI application
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration management
│   ├── agents/             # AI agents (Teaching, Quiz, Revision, etc.)
│   ├── rag/                # RAG system (ChromaDB, embeddings)
│   ├── database/           # SQLAlchemy models
│   ├── routes/             # API endpoints
│   ├── services/           # AI provider services
│   └── parsers/            # Document processing
│
├── frontend/               # Next.js application
│   ├── package.json        # npm dependencies (600+ packages)
│   ├── next.config.js      # Next.js configuration
│   ├── app/                # Next.js App Router (routes)
│   ├── components/         # React components
│   ├── services/           # API client
│   ├── store/              # Zustand state management
│   └── public/             # Static assets
│
└── app-data/               # Local data storage
    ├── app.db              # SQLite database (auto-created)
    ├── uploads/            # Uploaded documents
    └── chroma-data/        # Vector embeddings

```

---

## 🔐 Environment Variables

Create `.env` in the project root:

```env
# AI Provider Choice (pick at least one)
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=AIza-your-google-ai-key-here

# Default AI Provider (openai or gemini)
DEFAULT_PROVIDER=openai

# Model Selection (optional, defaults shown below)
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-1.5-pro

# Server Configuration
HOST=0.0.0.0
PORT=18080  # Backend port
```

### Getting API Keys

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy and paste into `.env`

**Google Gemini:**
1. Go to https://ai.google.dev/
2. Click "Get API key"
3. Create a new API key
4. Copy and paste into `.env`

---

## 🐛 Troubleshooting

### "Port already in use" Error

**Symptom:** `Address already in use` when starting services

**Solution:**
```bash
# Find and kill process on port 18080 (backend)
lsof -ti :18080 | xargs kill -9

# Find and kill process on port 38173 (frontend)
lsof -ti :38173 | xargs kill -9

# On Windows:
netstat -ano | findstr :18080
taskkill /PID <PID> /F
```

### "Python version 3.x required" Error

**Symptom:** `Setup requires Python 3.11+`

**Solution:**
```bash
# Specify Python path
python3.13 -m venv venv
source venv/bin/activate
```

### "No module named backend" Error

**Symptom:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
```bash
# Verify virtual environment is activated
which python  # Should show path in venv/

# Reinstall packages
pip install -r requirements.txt
```

### "npm ERR! peer dep missing" Warning

**Symptom:** Warnings during `npm install`

**Solution:**
```bash
cd frontend
npm install --legacy-peer-deps
```

### Frontend shows "Failed to connect to API"

**Symptom:** Frontend loads but API calls fail

**Solutions:**
1. Ensure backend is running: `curl http://localhost:18080/api/health`
2. Check CORS settings in `backend/config.py` include your frontend URL
3. Verify `.env` has correct `PORT=18080`

### "import chromadb" fails

**Symptom:** `ImportError` when starting backend

**Solution:**
```bash
pip install --upgrade chromadb
pip install -r requirements.txt
```

---

## 📊 Performance Tips

### 1. Use Python 3.13
The project is optimized for Python 3.13+ (has prebuilt wheels for dependencies):
```bash
python3.13 -m venv venv
```

### 2. Skip Frontend Build on Dev
For faster iteration during development:
```bash
./setup-and-run.sh --no-build  # Runs dev server instead of build
```

### 3. Backend Auto-Reload
Backend automatically reloads on code changes (development mode).

### 4. Frontend HMR
Frontend has Hot Module Replacement—changes visible instantly.

---

## 🚢 Deployment

### Production Build

```bash
# Build frontend for production
cd frontend
npm run build
npm start  # Runs production server

# Backend (use production ASGI server)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

### Docker (Optional)

To containerize the application:

```bash
# Create Dockerfile (example)
docker build -t ai-semester-companion .
docker run -p 18080:18080 -p 38173:38173 ai-semester-companion
```

---

## 📈 Monitoring & Logs

### Backend Logs
```bash
# Live logs (if using run.sh)
tail -f /tmp/backend.log

# All output goes to stdout in real-time
```

### Frontend Logs
Frontend output shows in the terminal:
```
▲ Next.js 15.5.18
- Ready in 4.5s
- Watching for changes...
```

### Health Endpoints

```bash
# Backend health
curl http://localhost:18080/api/health

# Frontend health (check loading any page)
curl http://localhost:38173
```

---

## 🎯 Getting Help

### Common Issues Checklist
- [ ] Python 3.11+ installed?
- [ ] Node.js 18+ installed?
- [ ] `.env` file created with API keys?
- [ ] Virtual environment activated?
- [ ] All dependencies installed? (`pip install -r requirements.txt`)
- [ ] No other services on ports 18080, 38173?

### Debug Mode
Enable verbose logging:
```bash
# Backend
LOGLEVEL=DEBUG python -m backend.main

# Frontend
DEBUG=* npm run dev
```

---

## 📝 Summary

```bash
# First-time setup (one command!)
./setup-and-run.sh

# Subsequent runs
./run.sh

# Access the application
# 🎨 Frontend: http://localhost:38173
# 🔌 API: http://localhost:18080/docs
```

That's it! Happy learning! 🎓🤖

---

**Questions?** Check the main [README.md](./README.md) or create an issue.
