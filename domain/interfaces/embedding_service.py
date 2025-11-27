"""
Interface: Embedding Service

Contrato abstracto para servicios de generación de embeddings.
Las implementaciones concretas estarán en infrastructure/
"""
from abc import ABC, abstractmethod
from typing import List


class IEmbeddingService(ABC):
    """
    Interfaz para servicios de embeddings

    Define el contrato que deben cumplir todas las implementaciones
    (Gemini, OpenAI, Cohere, etc.)
    """

    @abstractmethod
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Genera embedding para una consulta de búsqueda

        Args:
            query: Texto de la consulta del usuario

        Returns:
            List[float]: Vector embedding (768 dimensiones para Gemini)

        Raises:
            EmbeddingGenerationError: Si falla la generación
        """
        pass

    @abstractmethod
    async def generate_document_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un documento/chunk

        Args:
            text: Texto del documento a embeddear

        Returns:
            List[float]: Vector embedding (768 dimensiones para Gemini)

        Raises:
            EmbeddingGenerationError: Si falla la generación
        """
        pass

    @abstractmethod
    async def generate_batch_embeddings(
        self,
        texts: List[str],
        delay_ms: int = 100
    ) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos (con rate limiting)

        Args:
            texts: Lista de textos a embeddear
            delay_ms: Delay entre requests (para evitar rate limits)

        Returns:
            List[List[float]]: Lista de vectores embedding

        Raises:
            EmbeddingGenerationError: Si falla la generación
        """
        pass
