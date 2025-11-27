"""
RAG API Routes - Endpoints para consultas y estadísticas
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import logging

from ..schemas import QueryRequest, QueryResponse, StatisticsResponse
from ..dependencies import get_query_rag_use_case, get_statistics_use_case
from application.use_cases.query_rag import QueryRAGUseCase
from application.use_cases.get_statistics import GetStatisticsUseCase
from application.dtos.query_dto import QueryInput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG"])


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    use_case: Annotated[QueryRAGUseCase, Depends(get_query_rag_use_case)]
):
    """
    Endpoint: Consultar el sistema RAG

    Procesa una consulta del usuario usando RAG:
    1. Genera embedding de la query
    2. Busca chunks similares en vector store
    3. Construye contexto
    4. Genera respuesta con LLM

    Args:
        request: QueryRequest con la consulta del usuario
        use_case: QueryRAGUseCase inyectado

    Returns:
        QueryResponse: Respuesta con answer, sources, etc.
    """
    try:
        # Convertir HTTP schema → Application DTO
        input_dto = QueryInput(query=request.query)

        # Ejecutar caso de uso
        output_dto = await use_case.execute(input_dto)

        # Convertir Application DTO → HTTP schema
        return QueryResponse(
            answer=output_dto.answer,
            sources=output_dto.sources,
            document_name=output_dto.document_name,
            download_url=output_dto.download_url
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/stats", response_model=StatisticsResponse)
async def get_statistics(
    use_case: Annotated[GetStatisticsUseCase, Depends(get_statistics_use_case)]
):
    """
    Endpoint: Obtener estadísticas del sistema

    Retorna métricas agregadas:
    - Total de documentos
    - Total de chunks
    - Total de páginas
    - Distribución por categoría
    - Distribución por tipo de documento

    Args:
        use_case: GetStatisticsUseCase inyectado

    Returns:
        StatisticsResponse: Estadísticas del sistema
    """
    try:
        # Ejecutar caso de uso
        output_dto = await use_case.execute()

        # Convertir Application DTO → HTTP schema
        return StatisticsResponse(
            total_documents=output_dto.total_documents,
            total_chunks=output_dto.total_chunks,
            total_pages=output_dto.total_pages,
            categories=output_dto.categories,
            document_types=output_dto.document_types
        )

    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
