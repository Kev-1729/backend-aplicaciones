"""
Core Module - Shared utilities

Cross-cutting concerns:
- Exceptions: Custom exception classes
- Logging: Logging configuration
"""

from .exceptions import (
    RAGException,
    EmbeddingGenerationError,
    VectorSearchError,
    ChatGenerationError
)

__all__ = [
    "RAGException",
    "EmbeddingGenerationError",
    "VectorSearchError",
    "ChatGenerationError"
]
