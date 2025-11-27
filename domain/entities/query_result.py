"""
QueryResult Entity - Representa el resultado de una búsqueda RAG
"""
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class SimilarChunk:
    """Chunk encontrado en búsqueda de similitud"""
    text: str
    document_name: str
    document_id: str
    page_number: int
    similarity_score: float
    metadata: Optional[Dict] = None


@dataclass
class QueryResult:
    """
    Entidad de dominio: Resultado de Query RAG

    Representa el resultado de una consulta al sistema RAG.
    """
    query: str
    answer: str
    sources: List[str]
    similar_chunks: List[SimilarChunk]
    document_name: Optional[str] = None
    download_url: Optional[str] = None

    def has_sources(self) -> bool:
        """
        Verifica si se encontraron fuentes

        Returns:
            bool: True si hay al menos una fuente
        """
        return len(self.sources) > 0

    def get_unique_documents(self) -> List[str]:
        """
        Obtiene lista de documentos únicos citados

        Returns:
            List[str]: Nombres únicos de documentos
        """
        return list(set(self.sources))

    def get_average_similarity(self) -> float:
        """
        Calcula similitud promedio de chunks encontrados

        Returns:
            float: Promedio de similarity scores (0-1)
        """
        if not self.similar_chunks:
            return 0.0

        total_similarity = sum(chunk.similarity_score for chunk in self.similar_chunks)
        return total_similarity / len(self.similar_chunks)
