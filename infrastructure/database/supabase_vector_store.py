"""
Supabase Vector Store - Implementación de almacenamiento vectorial
"""
from typing import List, Dict
import logging
from supabase import Client
from domain.interfaces.vector_store import IVectorStore

logger = logging.getLogger(__name__)


class SupabaseVectorStore(IVectorStore):
    """
    Implementación de IVectorStore usando Supabase + pgvector

    Usa la función RPC search_similar_chunks() para búsqueda vectorial
    """

    def __init__(self, client: Client):
        """
        Initialize Supabase vector store

        Args:
            client: Supabase client instance
        """
        self._client = client
        logger.info("SupabaseVectorStore initialized")

    async def search_similar_chunks(
        self,
        embedding: List[float],
        threshold: float,
        limit: int
    ) -> List[Dict]:
        """
        Busca chunks similares usando búsqueda vectorial

        Args:
            embedding: Vector de búsqueda (768 dimensiones)
            threshold: Umbral mínimo de similitud (0-1)
            limit: Número máximo de resultados

        Returns:
            List[Dict]: Lista de chunks con metadata
        """
        try:
            logger.info(
                f"Searching similar chunks (threshold={threshold}, limit={limit})"
            )

            # Llamar a la función RPC de Supabase
            result = self._client.rpc(
                'search_similar_chunks',
                {
                    'query_embedding': embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()

            chunks = result.data if result.data else []
            logger.info(f"Found {len(chunks)} similar chunks")

            return chunks

        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}", exc_info=True)
            raise

    async def get_document_count(self) -> int:
        """
        Obtiene el total de documentos almacenados

        Returns:
            int: Número total de documentos
        """
        try:
            result = self._client.table('documents')\
                .select('*', count='exact')\
                .execute()

            count = result.count if result.count is not None else 0
            logger.info(f"Total documents: {count}")

            return count

        except Exception as e:
            logger.error(f"Error getting document count: {e}", exc_info=True)
            raise

    async def get_chunk_count(self) -> int:
        """
        Obtiene el total de chunks almacenados

        Returns:
            int: Número total de chunks
        """
        try:
            result = self._client.table('document_chunks')\
                .select('*', count='exact')\
                .execute()

            count = result.count if result.count is not None else 0
            logger.info(f"Total chunks: {count}")

            return count

        except Exception as e:
            logger.error(f"Error getting chunk count: {e}", exc_info=True)
            raise

    async def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del almacenamiento

        Returns:
            Dict: Estadísticas agregadas
        """
        try:
            logger.info("Retrieving database statistics...")

            # Get all documents
            documents_result = self._client.table('documents')\
                .select('*', count='exact')\
                .execute()

            documents = documents_result.data if documents_result.data else []
            total_documents = documents_result.count or 0

            # Get all chunks
            chunks_result = self._client.table('document_chunks')\
                .select('*', count='exact')\
                .execute()

            total_chunks = chunks_result.count or 0

            # Calculate aggregates
            total_pages = sum(doc.get('total_pages', 0) for doc in documents)

            # Group by category
            categories = {}
            for doc in documents:
                category = doc.get('category', 'Sin categoría')
                categories[category] = categories.get(category, 0) + 1

            # Group by document type
            document_types = {}
            for doc in documents:
                doc_type = doc.get('document_type', 'Sin tipo')
                document_types[doc_type] = document_types.get(doc_type, 0) + 1

            stats = {
                'total_documents': total_documents,
                'total_chunks': total_chunks,
                'total_pages': total_pages,
                'categories': categories,
                'document_types': document_types
            }

            logger.info(f"Statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting statistics: {e}", exc_info=True)
            raise
