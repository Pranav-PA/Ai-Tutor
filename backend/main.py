"""AI Semester Companion - FastAPI Backend."""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import CORS_ORIGINS, HOST, PORT, UPLOADS_DIR
from backend.database.connection import init_db

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="AI Semester Companion",
    description="AI-powered tutoring application for personalized learning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
if os.path.exists(str(UPLOADS_DIR)):
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Import and include routers
from backend.routes.courses import router as courses_router
from backend.routes.documents import router as documents_router
from backend.routes.chat import router as chat_router
from backend.routes.quiz import router as quiz_router
from backend.routes.revision import router as revision_router
from backend.routes.analytics import router as analytics_router
from backend.routes.settings import router as settings_router
from backend.routes.planner import router as planner_router

app.include_router(courses_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(revision_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(planner_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI Semester Companion API", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


# Serve frontend static files in desktop/production mode
if os.getenv("DESKTOP_MODE") == "true":
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend-dist")
    if os.path.exists(frontend_dir):
        app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
