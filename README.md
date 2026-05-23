# AI Semester Companion

An AI-powered personalized study companion that helps you learn course material through intelligent chat, quizzes, flashcards, revision notes, and study planning.

## Features

- **Document Upload** – Upload PDFs, DOCX, PPTX, TXT files; auto-indexed into a vector store for retrieval
- **AI Chat** – Context-aware teaching, doubt-clearing, and concept explanation using your uploaded materials
- **Quiz Generation** – AI generates MCQ/short-answer quizzes based on your course content
- **Revision Notes** – Auto-generated summaries and revision material
- **Flashcards** – Spaced-repetition flashcard system
- **Study Planner** – Personalized study schedule generator
- **Analytics** – Track progress and study patterns

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, ChromaDB |
| Frontend | Next.js 15, React 18, Tailwind CSS, Radix UI |
| AI | OpenAI GPT-4o / Google Gemini |
| Vector DB | ChromaDB (local, file-based) |

---

## Quick Start (5 minutes)

### Prerequisites

- **Python 3.10+** (`python3 --version`)
- **Node.js 18+** (`node --version`)
- **npm** (`npm --version`)
- An **OpenAI API key** or **Google Gemini API key**

### 1. Clone the repo

```bash
git clone https://github.com/Pranav-PA/Ai-Tutor.git
cd Ai-Tutor
```

### 2. Setup Python backend

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# (use any text editor)
nano .env
```

Set at minimum:
```
OPENAI_API_KEY=sk-your-key-here
DEFAULT_PROVIDER=openai
```

Or for Gemini:
```
GEMINI_API_KEY=your-gemini-key
DEFAULT_PROVIDER=gemini
```

### 4. Setup Frontend

```bash
cd frontend
npm install
cd ..
```

### 5. Run the application

You need **two terminals** (or use `&` on Linux):

**Terminal 1 – Backend:**
```bash
source venv/bin/activate   # or venv\Scripts\activate on Windows
python -m uvicorn backend.main:app --host 127.0.0.1 --port 18080 --reload
```

**Terminal 2 – Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Open the app

Open your browser and go to: **http://localhost:38173**

---

## Usage Guide

1. **Create a course** – Click "New Course" and give it a name (e.g., "Machine Learning")
2. **Upload materials** – Go into the course, click "Upload" and drop your PDF/DOCX files
3. **Chat with AI** – Ask questions about your material; the AI uses your uploaded docs as context
4. **Generate quizzes** – Go to the Quiz tab, select topic/difficulty, and test yourself
5. **Review flashcards** – Spaced repetition cards are auto-generated from your content
6. **Plan study sessions** – Set exam dates and hours per day to get a personalized schedule

---

## Project Structure

```
├── requirements.txt        # Python dependencies (install with pip)
├── .env.example            # Template for environment variables
├── .env                    # Your local config (not committed)
├── app-data/               # Runtime data (uploads, vector DB, etc.)
├── backend/
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # Configuration (reads .env)
│   ├── routes/             # API endpoints
│   ├── services/           # AI provider logic
│   ├── database/           # SQLAlchemy models & connection
│   ├── rag/                # Vector store (ChromaDB)
│   ├── parsers/            # Document parsing (PDF, DOCX, etc.)
│   ├── agents/             # AI agent orchestration
│   └── models/             # Pydantic schemas
├── frontend/
│   ├── package.json        # Node.js dependencies
│   ├── next.config.js      # Next.js config (proxies /api to backend)
│   └── src/
│       ├── app/            # Pages (Next.js App Router)
│       ├── components/     # Reusable UI components
│       ├── services/       # API client functions
│       └── store/          # State management (Zustand)
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET/POST | `/api/courses` | List / Create courses |
| POST | `/api/documents/upload` | Upload a document |
| POST | `/api/chat` | Send a chat message |
| POST | `/api/chat/stream` | Stream a chat response (SSE) |
| POST | `/api/quiz/generate` | Generate a quiz |
| POST | `/api/revision/generate` | Generate revision notes |
| POST | `/api/planner/generate` | Generate study plan |
| GET | `/api/analytics/{course_id}` | Get course analytics |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Make sure venv is activated: `source venv/bin/activate` |
| Frontend can't reach backend | Ensure backend is running on port 18080 |
| Upload fails | Check `app-data/uploads/` directory exists (auto-created on startup) |
| OpenAI errors | Verify your API key in `.env` and that you have credits |
| Port already in use | Kill the process: `lsof -ti:18080 | xargs kill` |

---

## Development Notes

- Backend runs on `http://127.0.0.1:18080`
- Frontend runs on `http://localhost:38173`
- Next.js proxies all `/api/*` requests to the backend automatically
- The vector database (ChromaDB) persists to `app-data/vectors/`
- Uploaded files are stored in `app-data/uploads/`
- SQLite database is auto-created at startup

## License

MIT
