"""Domain Interfaces - Contratos abstractos"""

from .embedding_service import IEmbeddingService
from .vector_store import IVectorStore
from .chat_service import IChatService

__all__ = ["IEmbeddingService", "IVectorStore", "IChatService"]
