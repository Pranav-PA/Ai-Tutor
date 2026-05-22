# AI Semester Companion 🎓🤖

> Your Personal AI-Powered Tutor for Every Semester

A full-stack AI tutoring application that acts as a personalized semester companion. Upload your notes, get personalized teaching, smart quizzes, revision plans, and exam preparation — all powered by AI that learns YOUR material.

![AI Semester Companion](https://img.shields.io/badge/AI-Semester_Companion-6366f1?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)

---

## ✨ Features

### 🧠 Multi-Agent AI System
- **Teaching Agent** — Explains concepts with step-by-step lessons
- **Quiz Agent** — Generates MCQs, short answers, numerical problems
- **Revision Agent** — Creates cheat sheets, formula sheets, quick notes
- **Memory Agent** — Tracks weak/strong topics, adapts difficulty
- **Analytics Agent** — Provides study insights and readiness scores
- **Question Paper Agent** — Generates model papers based on patterns

### 📚 Smart Document Processing
- Upload PDFs, DOCX, PPTX, TXT, images
- OCR support for handwritten notes
- Automatic chunking and vector embedding
- RAG-powered answers from YOUR notes

### 🎯 Adaptive Learning
- Identifies weak topics automatically
- Increases practice in struggling areas
- Spaced repetition flashcards (SM-2 algorithm)
- Confidence tracking per topic

### 📊 Analytics Dashboard
- Syllabus completion tracking
- Quiz accuracy trends
- AI Exam Readiness Score
- Study hour tracking & revision streaks

### 🎨 Premium UI
- Modern glassmorphism design
- Dark/Light/AMOLED themes
- Smooth Framer Motion animations
- Responsive (mobile/tablet/desktop)
- Command palette (Cmd+K)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                 Frontend                      │
│          (Next.js + TypeScript)              │
│     TailwindCSS + shadcn/ui + Framer        │
└─────────────────┬───────────────────────────┘
                  │ API Calls
┌─────────────────▼───────────────────────────┐
│              Backend (FastAPI)                │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Teaching │  │   Quiz   │  │ Revision │  │
│  │  Agent   │  │  Agent   │  │  Agent   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │         RAG System (ChromaDB)         │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────┐  ┌──────────┐                 │
│  │ SQLite   │  │  OpenAI  │                 │
│  │   DB     │  │ / Gemini │                 │
│  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ (with npm)
- **Python** 3.11+ (or 3.13 recommended)
- **OpenAI** or **Google Gemini** API key (or both)

### Quick Start (Recommended) ⚡

The easiest way to set up and run the entire application:

```bash
# Clone the repository
git clone https://github.com/yourusername/Ai-Semister-Companion.git
cd Ai-Semister-Companion

# Make scripts executable
chmod +x setup-and-run.sh run.sh

# One command to setup and run everything!
./setup-and-run.sh
```

The script will:
- ✅ Check all prerequisites
- ✅ Create Python virtual environment (if needed)
- ✅ Install all Python dependencies
- ✅ Install all npm packages
- ✅ Build the Next.js frontend
- ✅ Start both backend and frontend automatically

**Backend** runs at: http://localhost:18080  
**Frontend** runs at: http://localhost:38173  
**API Docs** available at: http://localhost:18080/docs

---

### Manual Setup (Alternative)

If you prefer manual control or need to troubleshoot:

#### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/Ai-Semister-Companion.git
cd Ai-Semister-Companion

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run build  # Optional: Pre-build for production
```

#### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Windows: notepad .env
# Mac/Linux: nano .env
```

#### 4. Run the Application

**Option A: Run Both Services (using run script)**
```bash
cd /path/to/Ai-Semister-Companion
./run.sh
```

**Option B: Run Separately in Different Terminals**

Terminal 1 (Backend):
```bash
cd Ai-Semister-Companion
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m backend.main
```
Backend: http://localhost:18080

Terminal 2 (Frontend):
```bash
cd Ai-Semister-Companion/frontend
npm run dev
```
Frontend: http://localhost:38173

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# AI Provider (choose one or both)
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=AIza-your-key-here

# Default provider (openai or gemini)
DEFAULT_PROVIDER=openai

# Models (optional)
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-1.5-pro

# Server
HOST=0.0.0.0
PORT=18080
```

You can also configure API keys from the Settings page in the UI.

---

## � Setup Scripts Reference

### `setup-and-run.sh` — Complete Setup & Start
Automates everything: prerequisites check, dependency installation, and service startup.

```bash
# Full setup and run both services
./setup-and-run.sh

# Setup only (install dependencies, don't start services)
./setup-and-run.sh --setup-only

# Skip Next.js build, use dev server only
./setup-and-run.sh --no-build
```

### `run.sh` — Start Services (After Setup)
Quick script to start both backend and frontend after dependencies are installed.

```bash
./run.sh
```

**What these scripts do:**
- ✅ Verify Python and Node.js are installed
- ✅ Activate Python virtual environment
- ✅ Install all dependencies from requirements.txt
- ✅ Install all npm packages
- ✅ Build frontend (if not using `--no-build`)
- ✅ Start backend on port 18080
- ✅ Start frontend on port 38173
- ✅ Display service URLs and log locations

---

## 🔧 Troubleshooting

### Port Already in Use
If you get "Address already in use" error:
```bash
# Kill processes on port 18080 (backend)
lsof -ti :18080 | xargs kill -9

# Kill processes on port 38173 (frontend)
lsof -ti :38173 | xargs kill -9

# On Windows, use:
# netstat -ano | findstr :18080
# taskkill /PID <PID> /F
```

### Python Version Issues
The application requires Python 3.11+. Check your version:
```bash
python3 --version
```

If you have multiple Python versions, specify explicitly:
```bash
python3.13 -m venv venv
```

### Virtual Environment Not Activating
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify activation (should show (venv) in terminal)
which python  # Should show path in venv/
```

### npm install Failures
Clear npm cache and reinstall:
```bash
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Backend Import Errors
Verify backend can be imported:
```bash
source venv/bin/activate
python3 -c "from backend.main import app; print('✓ Backend imports successfully')"
```

### Frontend Build Failures
Clear Next.js cache and rebuild:
```bash
cd frontend
rm -rf .next
npm run build
```

### API Connection Issues
Verify both services are running:
```bash
# Check backend
curl http://localhost:18080/api/health

# Check frontend
curl http://localhost:38173
```

---



```
Ai-Semister-Companion/
├── backend/
│   ├── agents/          # Multi-agent system (orchestrator, prompts)
│   ├── rag/             # Vector store & RAG system
│   ├── parsers/         # Document parsing (PDF, DOCX, PPTX, OCR)
│   ├── database/        # SQLAlchemy models & connection
│   ├── routes/          # API endpoints
│   ├── services/        # AI provider service
│   ├── models/          # Pydantic schemas
│   ├── config.py        # Configuration
│   └── main.py          # FastAPI application
├── frontend/
│   └── src/
│       ├── app/         # Next.js App Router pages
│       ├── components/  # React components
│       ├── services/    # API client
│       ├── store/       # Zustand state management
│       ├── types/       # TypeScript types
│       └── styles/      # Global styles
├── app-data/            # Local data storage
│   ├── uploads/         # Uploaded files
│   ├── vectors/         # ChromaDB vectors
│   └── ...
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

---

## 🎯 Usage Guide

1. **Create a Course** — Add your course name, semester, exam date
2. **Upload Materials** — Drag & drop PDFs, notes, slides
3. **Learn** — Ask the AI to teach you any topic
4. **Chat** — Have conversations about your course material
5. **Quiz** — Generate and take adaptive quizzes
6. **Revision** — Generate cheat sheets and flashcards
7. **Track Progress** — View analytics and readiness scores

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, TailwindCSS |
| UI Components | Radix UI, Framer Motion, Lucide Icons |
| State | Zustand, React Query |
| Backend | FastAPI, Python 3.11+ |
| Database | SQLite + SQLAlchemy |
| Vector DB | ChromaDB |
| AI | OpenAI GPT-4o / Google Gemini 1.5 Pro |
| Document Processing | pdfplumber, python-docx, python-pptx, Tesseract OCR |

---

## 📜 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/courses` | Create course |
| GET | `/api/courses` | List courses |
| GET | `/api/courses/{id}` | Get course |
| DELETE | `/api/courses/{id}` | Delete course |
| POST | `/api/documents/upload` | Upload document |
| GET | `/api/documents/{courseId}` | List documents |
| POST | `/api/chat/stream` | Chat (streaming) |
| POST | `/api/chat` | Chat (non-streaming) |
| POST | `/api/quiz/generate` | Generate quiz |
| POST | `/api/quiz/submit` | Submit quiz |
| POST | `/api/revision/generate` | Generate revision |
| POST | `/api/revision/flashcards/generate` | Generate flashcards |
| GET | `/api/analytics/{courseId}` | Get analytics |
| GET | `/api/settings` | Get settings |
| PUT | `/api/settings` | Update settings |

---

## 🔒 Security

- All data stored locally — no cloud dependency
- API keys stored in environment variables or local settings
- File upload size limits (50MB)
- Extension whitelist for uploads
- Input sanitization

---

## 🚧 Future Roadmap

- [ ] Ollama local model support
- [ ] Collaborative study rooms
- [ ] Mobile app (React Native)
- [ ] Cloud sync (optional)
- [ ] LMS integration
- [ ] Voice input/output
- [ ] Export to PDF/Markdown

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

Built with ❤️ for students everywhere.
