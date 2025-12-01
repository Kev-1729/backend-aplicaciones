"""
Entidad Feedback - Retroalimentación del usuario
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class Feedback:
    """
    Representa la retroalimentación del usuario sobre una respuesta del RAG.

    Atributos principales:
        is_correct: Métrica de exactitud (True=correcta, False=incorrecta, None=sin evaluar)
        query: Pregunta original del usuario
        answer: Respuesta generada por el RAG
    """
    query: str
    answer: str
    session_id: Optional[str] = None
    message_id: Optional[str] = None

    # Métrica principal: Exactitud
    is_correct: Optional[bool] = None

    # Métricas secundarias (opcionales)
    rating: Optional[int] = None  # 1-5 estrellas
    comment: Optional[str] = None

    # Metadata técnica
    sources: Optional[List[str]] = None
    chunks_count: Optional[int] = None
    similarity_threshold: Optional[float] = None

    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None

    # Metadata adicional
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validación post-inicialización"""
        if not self.query or not self.query.strip():
            raise ValueError("La query no puede estar vacía")

        if not self.answer or not self.answer.strip():
            raise ValueError("La respuesta no puede estar vacía")

        if self.rating is not None:
            if not isinstance(self.rating, int) or not (1 <= self.rating <= 5):
                raise ValueError("El rating debe ser un entero entre 1 y 5")

        if self.created_at is None:
            self.created_at = datetime.now()

        if self.updated_at is None:
            self.updated_at = datetime.now()

    def mark_as_correct(self) -> None:
        """Marca la respuesta como correcta"""
        self.is_correct = True
        self.updated_at = datetime.now()

    def mark_as_incorrect(self) -> None:
        """Marca la respuesta como incorrecta"""
        self.is_correct = False
        self.updated_at = datetime.now()

    def set_rating(self, rating: int) -> None:
        """
        Establece una calificación por estrellas

        Args:
            rating: Calificación entre 1 y 5

        Raises:
            ValueError: Si el rating no está en el rango 1-5
        """
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            raise ValueError("El rating debe ser un entero entre 1 y 5")

        self.rating = rating
        self.updated_at = datetime.now()

    def add_comment(self, comment: str) -> None:
        """
        Agrega un comentario del usuario

        Args:
            comment: Comentario textual
        """
        if comment and comment.strip():
            self.comment = comment.strip()
            self.updated_at = datetime.now()

    def is_evaluated(self) -> bool:
        """Verifica si la respuesta ha sido evaluada (correcta/incorrecta)"""
        return self.is_correct is not None

    def is_positive(self) -> bool:
        """Verifica si la retroalimentación es positiva"""
        return self.is_correct is True

    def is_negative(self) -> bool:
        """Verifica si la retroalimentación es negativa"""
        return self.is_correct is False

    def has_rating(self) -> bool:
        """Verifica si tiene calificación por estrellas"""
        return self.rating is not None

    def has_comment(self) -> bool:
        """Verifica si tiene comentario"""
        return self.comment is not None and len(self.comment.strip()) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el feedback a diccionario"""
        return {
            'query': self.query,
            'answer': self.answer,
            'session_id': self.session_id,
            'message_id': self.message_id,
            'is_correct': self.is_correct,
            'rating': self.rating,
            'comment': self.comment,
            'sources': self.sources,
            'chunks_count': self.chunks_count,
            'similarity_threshold': self.similarity_threshold,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'metadata': self.metadata or {}
        }


@dataclass
class ExactitudMetrics:
    """
    Métricas de exactitud del sistema RAG.

    Implementa la fórmula:
    Exactitud = (Nº de análisis correctos / Nº total de análisis realizados) * 100
    """
    total_evaluaciones: int
    respuestas_correctas: int
    respuestas_incorrectas: int
    sin_evaluar: int
    exactitud_porcentaje: float
    rating_promedio: Optional[float] = None

    def __post_init__(self):
        """Validación de métricas"""
        if self.total_evaluaciones < 0:
            raise ValueError("total_evaluaciones no puede ser negativo")

        if self.respuestas_correctas < 0 or self.respuestas_incorrectas < 0:
            raise ValueError("Las cantidades no pueden ser negativas")

        if not (0 <= self.exactitud_porcentaje <= 100):
            raise ValueError("La exactitud debe estar entre 0 y 100")

    def get_exactitud_label(self) -> str:
        """Retorna una etiqueta descriptiva de la exactitud"""
        if self.exactitud_porcentaje >= 90:
            return "Excelente"
        elif self.exactitud_porcentaje >= 75:
            return "Buena"
        elif self.exactitud_porcentaje >= 60:
            return "Regular"
        else:
            return "Necesita mejora"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte las métricas a diccionario"""
        return {
            'total_evaluaciones': self.total_evaluaciones,
            'respuestas_correctas': self.respuestas_correctas,
            'respuestas_incorrectas': self.respuestas_incorrectas,
            'sin_evaluar': self.sin_evaluar,
            'exactitud_porcentaje': round(self.exactitud_porcentaje, 2),
            'rating_promedio': round(self.rating_promedio, 2) if self.rating_promedio else None,
            'exactitud_label': self.get_exactitud_label()
        }
