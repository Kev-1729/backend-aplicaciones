"""
Global Exception Handlers for FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

from core.exceptions import (
    RAGException,
    EmbeddingGenerationError,
    VectorSearchError,
    ChatGenerationError
)

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    """
    Setup global exception handlers for the FastAPI app

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RAGException)
    async def rag_exception_handler(request: Request, exc: RAGException):
        """Handle RAG-specific exceptions"""
        logger.error(f"RAG Exception: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": exc.message,
                "type": exc.__class__.__name__
            }
        )

    @app.exception_handler(EmbeddingGenerationError)
    async def embedding_error_handler(request: Request, exc: EmbeddingGenerationError):
        """Handle embedding generation errors"""
        logger.error(f"Embedding Error: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Failed to generate embeddings. Please try again.",
                "type": "EmbeddingGenerationError"
            }
        )

    @app.exception_handler(VectorSearchError)
    async def vector_search_error_handler(request: Request, exc: VectorSearchError):
        """Handle vector search errors"""
        logger.error(f"Vector Search Error: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Failed to search knowledge base. Please try again.",
                "type": "VectorSearchError"
            }
        )

    @app.exception_handler(ChatGenerationError)
    async def chat_error_handler(request: Request, exc: ChatGenerationError):
        """Handle chat generation errors"""
        logger.error(f"Chat Error: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Failed to generate response. Please try again.",
                "type": "ChatGenerationError"
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred. Please try again later.",
                "type": "InternalServerError"
            }
        )

    logger.info("Exception handlers configured")
