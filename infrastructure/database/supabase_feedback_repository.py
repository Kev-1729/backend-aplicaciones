"""
Implementación de IFeedbackRepository usando Supabase
"""
import logging
from typing import Optional
from datetime import datetime
from supabase import Client

from domain.interfaces.feedback_repository import IFeedbackRepository
from domain.entities.feedback import Feedback, ExactitudMetrics
from core.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class SupabaseFeedbackRepository(IFeedbackRepository):
    """
    Implementación de IFeedbackRepository usando Supabase PostgreSQL.

    Gestiona el almacenamiento y cálculo de la métrica de exactitud.
    Fórmula: Exactitud = (Correctas / Total Evaluadas) × 100
    """

    def __init__(self, client: Client):
        """
        Args:
            client: Cliente de Supabase configurado
        """
        self.client = client

    async def save_feedback(self, feedback: Feedback) -> Feedback:
        """Guarda el feedback del usuario"""
        try:
            logger.info(f"Saving feedback for message: {feedback.message_id}")

            data = {
                "session_id": feedback.session_id,
                "message_id": feedback.message_id,
                "query": feedback.query,
                "answer": feedback.answer,
                "is_correct": feedback.is_correct,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "sources": feedback.sources or [],
                "chunks_count": feedback.chunks_count,
                "similarity_threshold": feedback.similarity_threshold,
                "metadata": feedback.metadata or {}
            }

            response = self.client.table("rag_feedback").insert(data).execute()

            if not response.data:
                raise VectorStoreError("No se pudo guardar el feedback")

            saved_data = response.data[0]
            logger.info(f"Feedback saved successfully: {saved_data['id']}")

            # Retornar feedback con datos actualizados
            feedback.created_at = datetime.fromisoformat(saved_data["created_at"])
            feedback.updated_at = datetime.fromisoformat(saved_data["updated_at"])

            return feedback

        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            raise VectorStoreError(f"Error al guardar feedback: {str(e)}")

    async def update_feedback(
        self,
        message_id: str,
        is_correct: Optional[bool] = None,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ) -> bool:
        """Actualiza un feedback existente"""
        try:
            logger.info(f"Updating feedback for message: {message_id}")

            # Construir objeto de actualización solo con campos proporcionados
            update_data = {}
            if is_correct is not None:
                update_data["is_correct"] = is_correct
            if rating is not None:
                update_data["rating"] = rating
            if comment is not None:
                update_data["comment"] = comment

            if not update_data:
                logger.warning("No data to update")
                return False

            response = self.client.table("rag_feedback")\
                .update(update_data)\
                .eq("message_id", message_id)\
                .execute()

            updated = len(response.data) > 0
            if updated:
                logger.info(f"Feedback updated for message {message_id}")
            else:
                logger.warning(f"No feedback found for message {message_id}")

            return updated

        except Exception as e:
            logger.error(f"Error updating feedback: {str(e)}")
            raise VectorStoreError(f"Error al actualizar feedback: {str(e)}")

    async def get_exactitud_metrics(self, days: int = 30) -> ExactitudMetrics:
        """
        Obtiene las métricas de exactitud del sistema

        Calcula: Exactitud = (Correctas / Total Evaluadas) × 100
        """
        try:
            logger.info(f"Calculating exactitud metrics for last {days} days")

            # Llamar a la función SQL que calcula las métricas
            response = self.client.rpc("calculate_exactitud", {
                "p_days": days
            }).execute()

            if not response.data or len(response.data) == 0:
                logger.warning("No feedback data available")
                # Retornar métricas vacías
                return ExactitudMetrics(
                    total_evaluaciones=0,
                    respuestas_correctas=0,
                    respuestas_incorrectas=0,
                    sin_evaluar=0,
                    exactitud_porcentaje=0.0,
                    rating_promedio=None
                )

            data = response.data[0]

            metrics = ExactitudMetrics(
                total_evaluaciones=data["total_evaluaciones"],
                respuestas_correctas=data["respuestas_correctas"],
                respuestas_incorrectas=data["respuestas_incorrectas"],
                sin_evaluar=data["sin_evaluar"],
                exactitud_porcentaje=float(data["exactitud_porcentaje"]),
                rating_promedio=float(data["rating_promedio"]) if data["rating_promedio"] else None
            )

            logger.info(
                f"Exactitud calculated: {metrics.exactitud_porcentaje}% "
                f"({metrics.respuestas_correctas}/{metrics.respuestas_correctas + metrics.respuestas_incorrectas})"
            )

            return metrics

        except Exception as e:
            logger.error(f"Error calculating exactitud: {str(e)}")
            raise VectorStoreError(f"Error al calcular exactitud: {str(e)}")

    async def get_feedback_by_message(self, message_id: str) -> Optional[Feedback]:
        """Obtiene el feedback de un mensaje específico"""
        try:
            logger.info(f"Fetching feedback for message: {message_id}")

            response = self.client.table("rag_feedback")\
                .select("*")\
                .eq("message_id", message_id)\
                .execute()

            if not response.data or len(response.data) == 0:
                logger.info(f"No feedback found for message {message_id}")
                return None

            data = response.data[0]

            feedback = Feedback(
                query=data["query"],
                answer=data["answer"],
                session_id=data.get("session_id"),
                message_id=data.get("message_id"),
                is_correct=data.get("is_correct"),
                rating=data.get("rating"),
                comment=data.get("comment"),
                sources=data.get("sources"),
                chunks_count=data.get("chunks_count"),
                similarity_threshold=data.get("similarity_threshold"),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                metadata=data.get("metadata")
            )

            logger.info(f"Feedback found for message {message_id}")
            return feedback

        except Exception as e:
            logger.error(f"Error fetching feedback: {str(e)}")
            raise VectorStoreError(f"Error al obtener feedback: {str(e)}")
