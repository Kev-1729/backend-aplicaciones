"""
DocumentChunk Entity - Representa un fragmento de documento con embedding
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DocumentChunk:
    """
    Entidad de dominio: Chunk de Documento

    Representa un fragmento de texto de un documento con su vector embedding.
    """
    id: str
    document_id: str
    text: str
    page_number: int
    chunk_index: int
    embedding: List[float]
    metadata: Optional[dict] = None

    @property
    def embedding_dimension(self) -> int:
        """
        Dimensión del vector embedding

        Returns:
            int: Número de dimensiones (debería ser 768 para Gemini)
        """
        return len(self.embedding)

    def validate_embedding_dimension(self, expected_dim: int = 768) -> bool:
        """
        Valida que el embedding tenga la dimensión esperada

        Args:
            expected_dim: Dimensión esperada (default 768 para Gemini)

        Returns:
            bool: True si la dimensión coincide
        """
        return self.embedding_dimension == expected_dim

    def has_valid_text(self) -> bool:
        """
        Valida que el texto del chunk no esté vacío

        Returns:
            bool: True si el texto tiene contenido
        """
        return bool(self.text and self.text.strip())
