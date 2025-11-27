"""
Get Statistics Use Case - Obtiene estadísticas del sistema
"""
import logging
from application.dtos.stats_dto import StatsOutput
from domain.interfaces.vector_store import IVectorStore

logger = logging.getLogger(__name__)


class GetStatisticsUseCase:
    """
    Caso de uso: Obtener estadísticas del sistema RAG

    Recupera métricas agregadas del vector store.
    """

    def __init__(self, vector_store: IVectorStore):
        self._vector_store = vector_store

    async def execute(self) -> StatsOutput:
        """
        Ejecuta la consulta de estadísticas

        Returns:
            StatsOutput: Estadísticas del sistema
        """
        logger.info("Retrieving system statistics...")

        try:
            # Obtener estadísticas del vector store
            stats_data = await self._vector_store.get_statistics()

            # Convertir a DTO
            stats = StatsOutput(
                total_documents=stats_data.get('total_documents', 0),
                total_chunks=stats_data.get('total_chunks', 0),
                total_pages=stats_data.get('total_pages', 0),
                categories=stats_data.get('categories', {}),
                document_types=stats_data.get('document_types', {})
            )

            logger.info(
                f"Statistics retrieved: {stats.total_documents} documents, "
                f"{stats.total_chunks} chunks"
            )

            return stats

        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}", exc_info=True)
            raise
