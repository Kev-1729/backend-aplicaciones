"""
FastAPI Application Factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routes import rag_router, session_router, feedback_router
from .schemas import HealthResponse
from infrastructure.config.settings import get_settings
from presentation.middleware.error_handler import setup_exception_handlers

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="RAG system for municipal procedures",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(rag_router)
    app.include_router(session_router)
    app.include_router(feedback_router)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            version=settings.VERSION,
            app_name=settings.APP_NAME
        )

    logger.info(f"{settings.APP_NAME} v{settings.VERSION} initialized")

    return app
