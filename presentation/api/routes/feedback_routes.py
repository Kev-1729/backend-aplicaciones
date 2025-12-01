"""
Feedback API Routes - Endpoints para retroalimentación y métricas de exactitud
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from presentation.api.schemas import (
    SubmitFeedbackRequest,
    FeedbackResponse,
    ExactitudMetricsResponse
)
from infrastructure.database.supabase_feedback_repository import SupabaseFeedbackRepository
from domain.entities.feedback import Feedback
from core.exceptions import VectorStoreError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/feedback", tags=["feedback"])


# Importar dependency injection
from presentation.api.dependencies import get_feedback_repository


@router.post(
    "/",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback for a RAG response"
)
async def submit_feedback(
    request: SubmitFeedbackRequest,
    feedback_repo: Annotated[SupabaseFeedbackRepository, Depends(get_feedback_repository)]
):
    """
    Envía retroalimentación sobre una respuesta del RAG.

    **Métrica de Exactitud:**
    - `is_correct=true`: La respuesta fue correcta
    - `is_correct=false`: La respuesta fue incorrecta
    - `is_correct=null`: Sin evaluar

    **Fórmula:** Exactitud = (Correctas / Total Evaluadas) × 100

    **Campos opcionales:**
    - `rating`: Calificación 1-5 estrellas
    - `comment`: Comentario del usuario
    """
    try:
        logger.info(f"Received feedback for message: {request.message_id}")

        # Crear entidad Feedback
        feedback = Feedback(
            query=request.query,
            answer=request.answer,
            session_id=request.session_id,
            message_id=request.message_id,
            is_correct=request.is_correct,
            rating=request.rating,
            comment=request.comment,
            sources=request.sources
        )

        # Guardar en base de datos
        saved_feedback = await feedback_repo.save_feedback(feedback)

        logger.info(f"Feedback saved for message {request.message_id}")

        return FeedbackResponse(
            success=True,
            message="Feedback guardado exitosamente",
            message_id=request.message_id
        )

    except VectorStoreError as e:
        logger.error(f"Error saving feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/metrics",
    response_model=ExactitudMetricsResponse,
    summary="Get exactitud metrics"
)
async def get_exactitud_metrics(
    days: int = 30,
    feedback_repo: Annotated[SupabaseFeedbackRepository, Depends(get_feedback_repository)] = None
):
    """
    Obtiene las métricas de exactitud del sistema RAG.

    **Fórmula de Exactitud:**
    ```
    Exactitud = (Nº de análisis correctos / Nº total de análisis realizados) × 100
    ```

    **Parámetros:**
    - `days`: Número de días a considerar (default: 30)

    **Retorna:**
    - Total de evaluaciones
    - Respuestas correctas e incorrectas
    - Porcentaje de exactitud
    - Rating promedio (opcional)
    - Label de exactitud (Excelente/Buena/Regular/Necesita mejora)
    """
    try:
        logger.info(f"Calculating exactitud metrics for last {days} days")

        # Obtener métricas
        metrics = await feedback_repo.get_exactitud_metrics(days=days)

        logger.info(
            f"Exactitud: {metrics.exactitud_porcentaje}% "
            f"({metrics.respuestas_correctas}/{metrics.total_evaluaciones})"
        )

        return ExactitudMetricsResponse(
            total_evaluaciones=metrics.total_evaluaciones,
            respuestas_correctas=metrics.respuestas_correctas,
            respuestas_incorrectas=metrics.respuestas_incorrectas,
            sin_evaluar=metrics.sin_evaluar,
            exactitud_porcentaje=metrics.exactitud_porcentaje,
            rating_promedio=metrics.rating_promedio,
            exactitud_label=metrics.get_exactitud_label()
        )

    except VectorStoreError as e:
        logger.error(f"Error calculating metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch(
    "/{message_id}",
    response_model=FeedbackResponse,
    summary="Update existing feedback"
)
async def update_feedback(
    message_id: str,
    is_correct: bool = None,
    rating: int = None,
    comment: str = None,
    feedback_repo: Annotated[SupabaseFeedbackRepository, Depends(get_feedback_repository)] = None
):
    """
    Actualiza el feedback de un mensaje existente.

    Permite cambiar:
    - `is_correct`: Correcta/Incorrecta
    - `rating`: Calificación 1-5
    - `comment`: Comentario
    """
    try:
        logger.info(f"Updating feedback for message: {message_id}")

        updated = await feedback_repo.update_feedback(
            message_id=message_id,
            is_correct=is_correct,
            rating=rating,
            comment=comment
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback not found for message {message_id}"
            )

        return FeedbackResponse(
            success=True,
            message="Feedback actualizado exitosamente",
            message_id=message_id
        )

    except VectorStoreError as e:
        logger.error(f"Error updating feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
