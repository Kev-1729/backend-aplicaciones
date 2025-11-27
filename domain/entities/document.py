"""
Document Entity - Representa un documento municipal
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Document:
    """
    Entidad de dominio: Documento Municipal

    Representa un documento procesado en el sistema RAG.
    No tiene dependencias de infraestructura.
    """
    id: str
    filename: str
    document_type: str  # "ley", "ordenanza", "decreto", "reglamento", "formulario", "guia"
    category: str       # "normativa", "comercio", "informacion", "general"
    total_pages: int
    file_hash: str
    created_at: datetime
    processing_status: str = "completed"
    total_chunks: Optional[int] = None

    def is_legal_document(self) -> bool:
        """
        Lógica de negocio: Determina si es un documento legal

        Returns:
            bool: True si es ley, ordenanza, decreto o reglamento
        """
        legal_types = {"ley", "ordenanza", "decreto", "reglamento"}
        return self.document_type in legal_types

    def is_small_document(self) -> bool:
        """
        Lógica de negocio: Determina si es un documento pequeño

        Returns:
            bool: True si tiene 5 páginas o menos
        """
        return self.total_pages <= 5

    def should_chunk_by_articles(self) -> bool:
        """
        Lógica de negocio: Determina si debe chunkearse por artículos

        Returns:
            bool: True si es documento legal (chunk por artículos)
        """
        return self.is_legal_document()

    def should_keep_as_single_chunk(self) -> bool:
        """
        Lógica de negocio: Determina si debe mantenerse como un solo chunk

        Returns:
            bool: True si es documento pequeño de tipo formulario/guía/general
        """
        small_doc_types = {"formulario", "guia", "documento_general"}
        return self.is_small_document() and self.document_type in small_doc_types
