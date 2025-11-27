"""
Custom Exceptions for RAG System
"""


class RAGException(Exception):
    """Base exception for RAG system"""
    def __init__(self, message: str = "An error occurred in the RAG system"):
        self.message = message
        super().__init__(self.message)


class EmbeddingGenerationError(RAGException):
    """Exception raised when embedding generation fails"""
    def __init__(self, message: str = "Failed to generate embeddings"):
        super().__init__(message)


class VectorSearchError(RAGException):
    """Exception raised when vector search fails"""
    def __init__(self, message: str = "Failed to search vector store"):
        super().__init__(message)


class ChatGenerationError(RAGException):
    """Exception raised when chat/LLM generation fails"""
    def __init__(self, message: str = "Failed to generate chat response"):
        super().__init__(message)


class VectorStoreError(RAGException):
    """Exception raised when vector store operations fail"""
    def __init__(self, message: str = "Vector store operation failed"):
        super().__init__(message)
