# 🎓 AI Learning Engine

**AI-powered adaptive learning platform** that replaces unstructured studying with guided, intelligent learning.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Folder Structure](#folder-structure)
- [Database Schema](#database-schema)
- [Agent System](#agent-system)
- [API Documentation](#api-documentation)
- [Frontend Pages](#frontend-pages)
- [Sample Workflow](#sample-workflow)
- [Setup & Run (Local)](#setup--run-local)
- [Setup & Run (Docker)](#setup--run-docker)
- [GitLab CI/CD Deployment](#gitlab-cicd-deployment)
- [Environment Variables](#environment-variables)
- [Performance Optimization](#performance-optimization)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Next.js)                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │Dashboard │ │Learning  │ │  Quiz    │ │    Analytics         │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ REST API (JSON)
┌────────────────────────────────┼────────────────────────────────────┐
│                         BACKEND (FastAPI)                            │
│                                │                                     │
│  ┌─────────────────────────────┼─────────────────────────────────┐  │
│  │              API LAYER (Routes)                                │  │
│  │  /auth  /ingestion  /learning  /quiz  /adaptive               │  │
│  └─────────────────────────────┬─────────────────────────────────┘  │
│                                │                                     │
│  ┌─────────────────────────────┼─────────────────────────────────┐  │
│  │           AgentScope Runtime (Orchestrator)                    │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │  HiCLaw - Hierarchical Control Logic                     │ │  │
│  │  │  • Decision rules with priority levels                   │ │  │
│  │  │  • State machine for learning lifecycle                  │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │  │
│  │  │Ingest  │→│Know.   │→│Weight. │→│Roadmap │→│Teach   │    │  │
│  │  │Agent   │ │Extract │ │Analysis│ │Agent   │ │Agent   │    │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └───┬────┘    │  │
│  │                                                    │          │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐                │          │  │
│  │  │Adaptive│←│Eval.   │←│Quiz    │←───────────────┘          │  │
│  │  │Agent   │ │Agent   │ │Agent   │                            │  │
│  │  └────┬───┘ └────────┘ └────────┘   ┌────────┐              │  │
│  │       │                               │Doubt   │              │  │
│  │       └──────── Loop Back ───────────→│Agent   │              │  │
│  └───────────────────────────────────────┴────────┴──────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │              SERVICE LAYER                                     │  │
│  │  LLMService │ VectorStore │ FileProcessor                     │  │
│  └──────┬──────────────┬─────────────────────────────────────────┘  │
└─────────┼──────────────┼────────────────────────────────────────────┘
          │              │
┌─────────┼──────────────┼────────────────────────────────────────────┐
│         │              │            DATA LAYER                        │
│  ┌──────┴───┐   ┌─────┴────┐   ┌───────────┐                       │
│  │PostgreSQL│   │FAISS/Vec │   │  Redis    │                       │
│  │Users     │   │Embeddings│   │  Cache    │                       │
│  │Courses   │   │Documents │   │  LLM Resp │                       │
│  │Progress  │   │Notes     │   │  Sessions │                       │
│  │Quizzes   │   │PYQs      │   │           │                       │
│  └──────────┘   └──────────┘   └───────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User uploads documents** → Ingestion Agent processes files (OCR, text extraction)
2. **Knowledge Extraction Agent** → Builds structured knowledge graph (Units → Topics → Subtopics)
3. **Weightage Analysis Agent** → Parses PYQs, assigns importance scores
4. **Roadmap Agent** → Creates optimized learning path
5. **Teaching Agent** → Generates explanations from uploaded material (RAG)
6. **Quiz Agent** → Generates assessments per topic
7. **Evaluation Agent** → Scores answers, identifies weak areas
8. **Adaptive Agent + HiCLaw** → Decides: revise, continue, or level up

---

## Folder Structure

```
learningagent/
├── .gitlab-ci.yml              # GitLab CI/CD pipeline
├── .gitignore
├── docker-compose.yml          # Production Docker Compose
├── docker-compose.dev.yml      # Development Docker Compose
├── README.md                   # This file
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   └── app/
│       ├── main.py             # FastAPI application factory
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py       # Settings/configuration
│       ├── database/
│       │   ├── __init__.py
│       │   └── session.py      # SQLAlchemy async engine
│       ├── models/
│       │   ├── __init__.py
│       │   └── models.py       # All SQLAlchemy models
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── schemas.py      # Pydantic schemas
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── routes.py       # Auth endpoints
│       │   └── security.py     # JWT, password hashing
│       ├── ingestion/
│       │   ├── __init__.py
│       │   └── routes.py       # File upload & processing
│       ├── learning/
│       │   ├── __init__.py
│       │   └── routes.py       # Topic content & navigation
│       ├── quiz/
│       │   ├── __init__.py
│       │   └── routes.py       # Quiz generation & submission
│       ├── adaptive/
│       │   ├── __init__.py
│       │   └── routes.py       # Doubts, recommendations, analytics
│       ├── agents/
│       │   ├── __init__.py     # Registry & runtime creation
│       │   ├── base.py         # BaseAgent, AgentContext, AgentResult
│       │   ├── runtime.py      # AgentRuntime + HiCLaw
│       │   ├── ingestion_agent.py
│       │   ├── knowledge_agent.py
│       │   ├── weightage_agent.py
│       │   ├── roadmap_agent.py
│       │   ├── teaching_agent.py
│       │   ├── doubt_agent.py
│       │   ├── quiz_agent.py
│       │   ├── evaluation_agent.py
│       │   └── adaptive_agent.py
│       └── services/
│           ├── __init__.py
│           ├── llm_service.py   # OpenAI API with caching
│           ├── vector_store.py  # FAISS vector store
│           └── file_processor.py # File parsing & OCR
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── app/
│       │   ├── globals.css
│       │   ├── layout.tsx       # Root layout
│       │   ├── page.tsx         # Landing page
│       │   ├── auth/
│       │   │   └── page.tsx     # Login/Register
│       │   ├── dashboard/
│       │   │   ├── layout.tsx
│       │   │   └── page.tsx     # Main dashboard
│       │   ├── learning/
│       │   │   ├── layout.tsx
│       │   │   └── page.tsx     # Learning page
│       │   ├── quiz/
│       │   │   ├── layout.tsx
│       │   │   └── page.tsx     # Quiz page
│       │   └── analytics/
│       │       ├── layout.tsx
│       │       └── page.tsx     # Analytics page
│       ├── components/
│       │   └── layout/
│       │       └── Sidebar.tsx  # Navigation sidebar
│       ├── lib/
│       │   └── api.ts           # API client (Axios)
│       └── store/
│           └── index.ts         # Zustand state management
│
└── docs/
```

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Users   │────<│ Courses  │────<│Documents │
└──────────┘     └──────────┘     └──────────┘
     │                │
     │           ┌────┴────┐
     │           │  Units  │
     │           └────┬────┘
     │                │
     │           ┌────┴────┐
     │           │ Topics  │────<┌──────────┐
     │           └────┬────┘     │Subtopics │
     │                │          └──────────┘
     │                │
     │      ┌─────────┼─────────┐
     │      │         │         │
┌────┴──────┴┐   ┌────┴───┐  ┌─┴──────────┐
│UserProgress│   │ Quizzes │  │ChatMessages│
└────────────┘   └────┬───┘  └────────────┘
                      │
                 ┌────┴────┐
                 │Questions│
                 └────┬────┘
                      │
                ┌─────┴─────┐
                │QuizAttempts│
                └───────────┘
```

### Key Tables

| Table | Purpose |
|-------|---------|
| `users` | User authentication & profiles |
| `courses` | Subject/course containers |
| `documents` | Uploaded files (syllabus, notes, PYQs) |
| `units` | Top-level course divisions |
| `topics` | Individual learning topics with content |
| `subtopics` | Granular breakdowns within topics |
| `roadmaps` | Generated learning paths (JSON structure) |
| `user_progress` | Per-topic progress tracking |
| `quizzes` | Generated quiz containers |
| `questions` | Individual quiz questions (MCQ, short, conceptual) |
| `quiz_attempts` | Student quiz submissions & scores |
| `chat_messages` | Doubt resolution conversation history |
| `learning_states` | Adaptive learning state per user/course |

---

## Agent System

### Agent Architecture (AgentScope)

The system uses a custom **AgentScope** framework with three components:

#### 1. BaseAgent (Abstract)
```python
class BaseAgent:
    async def pre_execute(context)   # Pre-execution hook
    async def execute(context)        # Main logic (MUST implement)
    async def post_execute(context)   # Post-execution hook
    async def run(context)            # Full pipeline
```

#### 2. AgentScope Runtime (Orchestrator)
- Registers agents and maps them to learning phases
- Manages state transitions (state machine)
- Passes context between agents
- Supports pipeline and adaptive loop execution

#### 3. HiCLaw (Hierarchical Control Logic)
- Priority-based decision rules (CRITICAL > HIGH > MEDIUM > LOW)
- Evaluates conditions on the learning context
- Determines which action/agent to trigger next

### Agent Pipeline

```
Phase 1: INGESTION ─────→ Phase 2: KNOWLEDGE_EXTRACTION
                                         │
Phase 3: WEIGHTAGE_ANALYSIS ←────────────┘
         │
Phase 4: ROADMAP_GENERATION ←────────────┘
         │
Phase 5: TEACHING ←──────────────────────┘
         │
Phase 6: QUIZ ←──────────────────────────┘
         │
Phase 7: EVALUATION ←────────────────────┘
         │
Phase 8: ADAPTATION ←────────────────────┘
         │
         └──→ (Loop back to TEACHING or REVISION)
```

### HiCLaw Decision Rules

| Priority | Rule | Condition | Action |
|----------|------|-----------|--------|
| CRITICAL | Force Revision | Score < 40% | Revision mode |
| HIGH | Suggest Revision | 40% ≤ Score < 60% | Adaptive revision |
| HIGH | Level Up | Score ≥ 90% + 3 consecutive | Increase difficulty |
| MEDIUM | Continue | Score ≥ 60% | Next topic |
| MEDIUM | Course Complete | All topics done | Completion |

---

## API Documentation

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/auth/me` | Get current user |

### Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ingestion/courses` | Create course |
| GET | `/api/v1/ingestion/courses` | List courses |
| POST | `/api/v1/ingestion/courses/{id}/upload` | Upload documents |
| POST | `/api/v1/ingestion/courses/{id}/process` | Process & generate roadmap |

### Learning
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/learning/courses/{id}/roadmap` | Get roadmap |
| GET | `/api/v1/learning/courses/{id}/units` | Get units & topics |
| GET | `/api/v1/learning/topics/{id}` | Get topic content |
| POST | `/api/v1/learning/topics/{id}/complete` | Mark complete |
| GET | `/api/v1/learning/courses/{id}/progress` | Get progress |
| GET | `/api/v1/learning/courses/{id}/next-topic` | Get next topic |

### Quiz
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/quiz/generate` | Generate quiz |
| GET | `/api/v1/quiz/{id}` | Get quiz |
| POST | `/api/v1/quiz/submit` | Submit answers |
| GET | `/api/v1/quiz/attempts/{course_id}` | Quiz history |

### Adaptive
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/adaptive/doubt` | Ask a doubt |
| GET | `/api/v1/adaptive/recommend/{course_id}` | Get recommendation |
| GET | `/api/v1/adaptive/analytics/{course_id}` | Get analytics |

---

## Frontend Pages

### 1. Landing Page (`/`)
- Product hero with feature highlights
- Login/Register CTA

### 2. Auth Page (`/auth`)
- Login/Register toggle form
- JWT token storage

### 3. Dashboard (`/dashboard`)
- Course cards with upload/process/learn actions
- Quick stats (courses, completed, hours)
- Create course modal
- Upload modal (syllabus, notes, PYQs)

### 4. Learning Page (`/learning?course={id}`)
- Topic content with tabbed view (Content, Key Points, Examples)
- Chat panel for doubts (real-time Q&A)
- Navigation (Previous / Mark Complete / Next)
- Markdown rendering for explanations

### 5. Quiz Page (`/quiz`)
- Quiz generation from current topic
- Interactive MCQ selection
- Text input for short/conceptual
- Progress bar
- Instant results with per-question feedback

### 6. Analytics Page (`/analytics`)
- Score history line chart
- Completion pie chart
- Topic performance bar chart
- Weak/strong areas identification

---

## Sample Workflow

```
1. User REGISTERS → Creates account with JWT auth

2. User CREATES COURSE → "Data Structures" 

3. User UPLOADS:
   • syllabus.pdf (course structure)
   • notes.pdf (study material)
   • pyq_2023.pdf (previous year questions)

4. User clicks PROCESS:
   • Ingestion Agent: Extracts text, OCR if needed, chunks & embeds
   • Knowledge Agent: Extracts Units → Topics → Subtopics
   • Weightage Agent: Analyzes PYQ frequency, assigns importance
   • Roadmap Agent: Creates ordered learning path

5. User clicks LEARN:
   • Teaching Agent retrieves relevant chunks from vector store
   • Generates explanation, key points, examples, memory tricks
   • Content is grounded in uploaded materials only

6. User ASKS DOUBT:
   • "What is the difference between stack and queue?"
   • Doubt Agent retrieves context via vector similarity
   • Generates contextual answer

7. After learning, user takes QUIZ:
   • Quiz Agent generates 5 questions (MCQ + short answer)
   • User answers interactively
   • Evaluation Agent scores answers

8. ADAPTIVE loop:
   • Score: 45% → HiCLaw rule "force_revision" triggers
   • System recommends reviewing weak concepts
   • After revision, quiz again → Score: 78%
   • Continue to next topic

9. REPEAT until all topics completed
```

---

## Setup & Run (Local)

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16
- Redis 7
- Tesseract OCR (`apt install tesseract-ocr`)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your actual values (DATABASE_URL, OPENAI_API_KEY, etc.)

# Create database
createdb learningagent

# Run migrations (or let the app auto-create tables)
# alembic upgrade head

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment
cp .env.local.example .env.local

# Run development server
npm run dev
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## Setup & Run (Docker)

### Quick Start (Recommended)

```bash
# Clone the repository
git clone <your-repo-url> learningagent
cd learningagent

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Start all services
docker-compose up --build -d

# Check status
docker-compose ps
docker-compose logs -f backend
```

### Development Mode

```bash
# Uses hot-reload for both frontend and backend
docker-compose -f docker-compose.dev.yml up --build
```

### Services

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |

---

## GitLab CI/CD Deployment

### Pipeline Stages

```
test → build → deploy
```

### Required CI/CD Variables (GitLab Settings > CI/CD > Variables)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `SSH_PRIVATE_KEY` | SSH key for deploy server |
| `SSH_KNOWN_HOSTS` | Known hosts file content |
| `STAGING_USER` | Deploy username (staging) |
| `STAGING_HOST` | Deploy server IP (staging) |
| `PROD_USER` | Deploy username (production) |
| `PROD_HOST` | Deploy server IP (production) |
| `API_URL` | Backend API URL for frontend |

### Deploy Process

1. **Push to `develop`**: Runs tests → Builds images → Manual deploy to staging
2. **Push to `main`**: Runs tests → Builds images → Manual deploy to production
3. **Production deploy** includes automatic health check and rollback

### Server Setup (One-time)

On your deploy server:

```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sh

# Create app directory
mkdir -p /opt/learning-engine
cd /opt/learning-engine

# Copy docker-compose.yml (or pull from registry)
# Set environment variables
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Pull and start
docker-compose pull
docker-compose up -d
```

---

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/learningagent

# Redis
REDIS_URL=redis://redis:6379/0

# Auth
SECRET_KEY=your-256-bit-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4

# Vector DB
FAISS_INDEX_PATH=./data/faiss_index
EMBEDDING_MODEL=all-MiniLM-L6-v2

# File Storage
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=52428800
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Performance Optimization

| Technique | Implementation |
|-----------|---------------|
| **LLM Response Caching** | Redis cache with 1hr TTL for repeated prompts |
| **Vector Search Efficiency** | FAISS IndexFlatIP with normalized embeddings, top-k retrieval |
| **Streaming Responses** | OpenAI streaming for real-time teaching output |
| **Minimal Agent Calls** | Pipeline execution only processes changed documents |
| **Database Connection Pooling** | SQLAlchemy async pool (size=20, overflow=10) |
| **Chunked Text Processing** | 1000-char chunks with 200-char overlap for embeddings |
| **Frontend Caching** | Zustand state persistence, SWR-like data fetching |
| **Docker Layer Caching** | Multi-stage builds, CI cache with branch keys |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TailwindCSS, Framer Motion, Zustand, Recharts |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Pydantic v2 |
| AI/ML | OpenAI GPT-4, Sentence Transformers, FAISS, LangChain |
| Database | PostgreSQL 16, Redis 7 |
| Auth | JWT (python-jose), bcrypt |
| File Processing | PyPDF2, python-docx, Tesseract OCR |
| DevOps | Docker, Docker Compose, GitLab CI/CD |
| Architecture | Agent-based (AgentScope + HiCLaw) |

---

## License

MIT License - See LICENSE file for details.
