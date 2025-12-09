"""
Unit tests for DocumentChunk entity
"""
import pytest
from typing import List
from domain.entities.chunk import DocumentChunk


class TestDocumentChunk:
    """Tests para la entidad DocumentChunk"""

    def test_create_chunk(self, sample_chunk):
        """Test: Crear chunk correctamente"""
        assert sample_chunk.id == "chunk-001"
        assert sample_chunk.document_id == "doc-123"
        assert "Requisitos" in sample_chunk.text
        assert sample_chunk.page_number == 1
        assert sample_chunk.chunk_index == 0
        assert len(sample_chunk.embedding) == 768

    def test_embedding_dimension_property(self, sample_chunk):
        """Test: Propiedad embedding_dimension retorna longitud correcta"""
        assert sample_chunk.embedding_dimension == 768

    def test_validate_embedding_dimension_success(self, sample_chunk):
        """Test: Validar embedding con dimensión correcta (768)"""
        assert sample_chunk.validate_embedding_dimension(768) is True

    def test_validate_embedding_dimension_failure(self):
        """Test: Validar embedding con dimensión incorrecta"""
        chunk = DocumentChunk(
            id="chunk-002",
            document_id="doc-123",
            text="Test text",
            page_number=1,
            chunk_index=0,
            embedding=[0.1] * 512  # Dimensión incorrecta
        )
        assert chunk.validate_embedding_dimension(768) is False
        assert chunk.embedding_dimension == 512

    @pytest.mark.parametrize("embedding_size,expected_dim,should_pass", [
        (768, 768, True),
        (512, 768, False),
        (1024, 768, False),
        (768, 512, False),
        (1536, 1536, True),
    ])
    def test_validate_embedding_dimension_parametrized(
        self,
        embedding_size,
        expected_dim,
        should_pass
    ):
        """Test parametrizado: Validar diferentes dimensiones de embeddings"""
        chunk = DocumentChunk(
            id="chunk-test",
            document_id="doc-test",
            text="Test",
            page_number=1,
            chunk_index=0,
            embedding=[0.1] * embedding_size
        )
        assert chunk.validate_embedding_dimension(expected_dim) == should_pass

    def test_has_valid_text_true(self, sample_chunk):
        """Test: Chunk con texto válido retorna True"""
        assert sample_chunk.has_valid_text() is True

    def test_has_valid_text_false_empty(self):
        """Test: Chunk con texto vacío retorna False"""
        chunk = DocumentChunk(
            id="chunk-empty",
            document_id="doc-123",
            text="",
            page_number=1,
            chunk_index=0,
            embedding=[0.1] * 768
        )
        assert chunk.has_valid_text() is False

    def test_has_valid_text_false_whitespace(self):
        """Test: Chunk con solo espacios retorna False"""
        chunk = DocumentChunk(
            id="chunk-whitespace",
            document_id="doc-123",
            text="   \n\t  ",
            page_number=1,
            chunk_index=0,
            embedding=[0.1] * 768
        )
        assert chunk.has_valid_text() is False

    @pytest.mark.parametrize("text,expected", [
        ("Valid text", True),
        ("Requisitos: DNI, RUC", True),
        ("A", True),
        ("", False),
        ("   ", False),
        ("\n\t", False),
        ("  \n  ", False),
    ])
    def test_has_valid_text_parametrized(self, text, expected):
        """Test parametrizado: Verificar validación de texto"""
        chunk = DocumentChunk(
            id="chunk-test",
            document_id="doc-test",
            text=text,
            page_number=1,
            chunk_index=0,
            embedding=[0.1] * 768
        )
        assert chunk.has_valid_text() == expected

    def test_chunk_with_metadata(self):
        """Test: Chunk con metadata opcional"""
        metadata = {
            "document_type": "guia",
            "category": "comercio",
            "language": "es"
        }
        chunk = DocumentChunk(
            id="chunk-meta",
            document_id="doc-123",
            text="Test text",
            page_number=1,
            chunk_index=0,
            embedding=[0.1] * 768,
            metadata=metadata
        )
        assert chunk.metadata == metadata
        assert chunk.metadata["document_type"] == "guia"

    def test_chunk_without_metadata(self, sample_chunk):
        """Test: Chunk sin metadata (None por defecto)"""
        chunk = DocumentChunk(
            id="chunk-no-meta",
            document_id="doc-123",
            text="Test text",
            page_number=1,
            chunk_index=0,
            embedding=[0.1] * 768
        )
        assert chunk.metadata is None

    def test_chunk_index_ordering(self):
        """Test: Múltiples chunks con índices ordenados"""
        chunks = [
            DocumentChunk(
                id=f"chunk-{i}",
                document_id="doc-123",
                text=f"Chunk {i}",
                page_number=1,
                chunk_index=i,
                embedding=[0.1] * 768
            )
            for i in range(5)
        ]

        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
