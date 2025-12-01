"""
Interfaz para el repositorio de feedback
"""
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.feedback import Feedback, ExactitudMetrics


class IFeedbackRepository(ABC):
    """
    Contrato abstracto para almacenar y recuperar feedback del usuario.

    Maneja la métrica de exactitud del sistema RAG.
    """

    @abstractmethod
    async def save_feedback(self, feedback: Feedback) -> Feedback:
        """
        Guarda el feedback del usuario

        Args:
            feedback: Entidad Feedback a guardar

        Returns:
            Feedback guardado con ID generado

        Raises:
            VectorStoreError: Si hay error al guardar
        """
        pass

    @abstractmethod
    async def update_feedback(
        self,
        message_id: str,
        is_correct: Optional[bool] = None,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ) -> bool:
        """
        Actualiza un feedback existente

        Args:
            message_id: ID del mensaje a actualizar
            is_correct: Nueva evaluación de exactitud
            rating: Nueva calificación
            comment: Nuevo comentario

        Returns:
            True si se actualizó, False si no existe

        Raises:
            VectorStoreError: Si hay error al actualizar
        """
        pass

    @abstractmethod
    async def get_exactitud_metrics(self, days: int = 30) -> ExactitudMetrics:
        """
        Obtiene las métricas de exactitud del sistema

        Calcula: Exactitud = (Correctas / Total Evaluadas) × 100

        Args:
            days: Número de días a considerar (default: 30)

        Returns:
            ExactitudMetrics con las estadísticas calculadas

        Raises:
            VectorStoreError: Si hay error al calcular
        """
        pass

    @abstractmethod
    async def get_feedback_by_message(self, message_id: str) -> Optional[Feedback]:
        """
        Obtiene el feedback de un mensaje específico

        Args:
            message_id: ID del mensaje

        Returns:
            Feedback si existe, None si no

        Raises:
            VectorStoreError: Si hay error al buscar
        """
        pass
