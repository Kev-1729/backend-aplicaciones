"""Domain Interfaces - Contratos abstractos"""

from .embedding_service import IEmbeddingService
from .vector_store import IVectorStore
from .chat_service import IChatService
from .chat_session_store import IChatSessionStore
from .feedback_repository import IFeedbackRepository

__all__ = [
    "IEmbeddingService",
    "IVectorStore",
    "IChatService",
    "IChatSessionStore",
    "IFeedbackRepository"
]
