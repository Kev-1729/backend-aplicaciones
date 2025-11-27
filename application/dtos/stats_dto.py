"""
Stats DTOs - Data Transfer Objects para estadísticas
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class StatsOutput:
    """
    DTO de salida para estadísticas del sistema

    Representa las estadísticas agregadas del sistema RAG.
    """
    total_documents: int
    total_chunks: int
    total_pages: int
    categories: Dict[str, int]
    document_types: Dict[str, int]

    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización JSON"""
        return {
            "total_documents": self.total_documents,
            "total_chunks": self.total_chunks,
            "total_pages": self.total_pages,
            "categories": self.categories,
            "document_types": self.document_types
        }
