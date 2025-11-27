"""
Gemini Embedding Service - Implementación con Google Gemini
"""
import google.generativeai as genai
from typing import List
import asyncio
import logging
from domain.interfaces.embedding_service import IEmbeddingService
from infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


class GeminiEmbeddingService(IEmbeddingService):
    """
    Implementación de IEmbeddingService usando Google Gemini

    Genera embeddings de 768 dimensiones usando text-embedding-004
    """

    def __init__(self):
        """Initialize Gemini AI client"""
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_EMBEDDING_MODEL
        logger.info(f"GeminiEmbeddingService initialized with model: {self.model_name}")

    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Genera embedding para una consulta de búsqueda

        Args:
            query: Texto de la consulta del usuario

        Returns:
            List[float]: Vector embedding (768 dimensiones)
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model=f"models/{self.model_name}",
                    content=query,
                    task_type="retrieval_query"
                )
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    async def generate_document_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un documento/chunk

        Args:
            text: Texto del documento a embeddear

        Returns:
            List[float]: Vector embedding (768 dimensiones)
        """
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model=f"models/{self.model_name}",
                    content=text,
                    task_type="retrieval_document"
                )
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating document embedding: {e}")
            raise

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
        """
        embeddings = []

        for i, text in enumerate(texts):
            try:
                embedding = await self.generate_document_embedding(text)
                embeddings.append(embedding)

                # Log progress
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated embeddings: {i + 1}/{len(texts)}")

                # Rate limiting
                if i < len(texts) - 1:
                    await asyncio.sleep(delay_ms / 1000)

            except Exception as e:
                logger.error(f"Error embedding text {i}: {e}")
                raise

        logger.info(f"Successfully generated {len(embeddings)} embeddings")
        return embeddings
