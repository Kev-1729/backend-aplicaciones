"""
Query DTOs - Data Transfer Objects para consultas RAG
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class QueryInput:
    """
    DTO de entrada para consultas RAG con soporte de sesiones

    Representa la solicitud del usuario desde la capa de presentación.
    """
    query: str
    session_id: Optional[str] = None  # ID de sesión para memoria conversacional

    def is_valid(self) -> bool:
        """Valida que la query no esté vacía"""
        return bool(self.query and self.query.strip())


@dataclass
class QueryOutput:
    """
    DTO de salida para consultas RAG

    Representa la respuesta que se envía a la capa de presentación.
    """
    answer: str
    sources: List[str]
    document_name: Optional[str] = None
    download_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización JSON"""
        return {
            "answer": self.answer,
            "sources": self.sources,
            "document_name": self.document_name,
            "download_url": self.download_url
        }
