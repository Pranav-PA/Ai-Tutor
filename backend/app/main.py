"""AI Learning Engine - Main FastAPI Application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import get_settings
from app.database import init_db

settings = get_settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    structlog.get_logger().info("application_started", app=settings.app_name)
    yield
    # Shutdown
    structlog.get_logger().info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered adaptive learning platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://frontend:3000", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    from app.auth.routes import router as auth_router
    from app.ingestion.routes import router as ingestion_router
    from app.learning.routes import router as learning_router
    from app.quiz.routes import router as quiz_router
    from app.adaptive.routes import router as adaptive_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(ingestion_router, prefix="/api/v1")
    app.include_router(learning_router, prefix="/api/v1")
    app.include_router(quiz_router, prefix="/api/v1")
    app.include_router(adaptive_router, prefix="/api/v1")

    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy", "app": settings.app_name, "version": "1.0.0"}

    return app


app = create_app()
