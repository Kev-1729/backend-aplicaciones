"""
Interface: Vector Store

Contrato abstracto para almacenamiento y búsqueda vectorial.
Las implementaciones concretas estarán en infrastructure/
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class IVectorStore(ABC):
    """
    Interfaz para almacenamiento vectorial

    Define el contrato que deben cumplir todas las implementaciones
    (Supabase, Pinecone, Weaviate, etc.)
    """

    @abstractmethod
    async def search_similar_chunks(
        self,
        embedding: List[float],
        threshold: float,
        limit: int
    ) -> List[Dict]:
        """
        Busca chunks similares usando búsqueda vectorial

        Args:
            embedding: Vector de búsqueda
            threshold: Umbral mínimo de similitud (0-1)
            limit: Número máximo de resultados

        Returns:
            List[Dict]: Lista de chunks con metadata
                Cada dict contiene:
                - text: Texto del chunk
                - document_name: Nombre del documento
                - document_id: ID del documento
                - page_number: Número de página
                - similarity: Score de similitud

        Raises:
            VectorSearchError: Si falla la búsqueda
        """
        pass

    @abstractmethod
    async def get_document_count(self) -> int:
        """
        Obtiene el total de documentos almacenados

        Returns:
            int: Número total de documentos

        Raises:
            VectorStoreError: Si falla la consulta
        """
        pass

    @abstractmethod
    async def get_chunk_count(self) -> int:
        """
        Obtiene el total de chunks almacenados

        Returns:
            int: Número total de chunks

        Raises:
            VectorStoreError: Si falla la consulta
        """
        pass

    @abstractmethod
    async def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del almacenamiento

        Returns:
            Dict: Estadísticas con estructura:
                - total_documents: int
                - total_chunks: int
                - total_pages: int
                - categories: Dict[str, int]
                - document_types: Dict[str, int]

        Raises:
            VectorStoreError: Si falla la consulta
        """
        pass
