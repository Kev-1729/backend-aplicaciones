"""
Unit tests for Document entity
"""
import pytest
from datetime import datetime
from domain.entities.document import Document


class TestDocument:
    """Tests para la entidad Document"""

    def test_create_document(self, sample_document):
        """Test: Crear documento correctamente"""
        assert sample_document.id == "doc-123"
        assert sample_document.filename == "Licencia_Funcionamiento.pdf"
        assert sample_document.document_type == "guia"
        assert sample_document.category == "comercio"
        assert sample_document.total_pages == 10
        assert sample_document.processing_status == "completed"

    def test_is_legal_document_true(self, sample_legal_document):
        """Test: Documento legal retorna True"""
        assert sample_legal_document.is_legal_document() is True
        assert sample_legal_document.document_type == "ordenanza"

    def test_is_legal_document_false(self, sample_document):
        """Test: Documento no legal retorna False"""
        assert sample_document.is_legal_document() is False
        assert sample_document.document_type == "guia"

    @pytest.mark.parametrize("doc_type,expected", [
        ("ley", True),
        ("ordenanza", True),
        ("decreto", True),
        ("reglamento", True),
        ("guia", False),
        ("formulario", False),
    ])
    def test_is_legal_document_parametrized(self, doc_type, expected):
        """Test parametrizado: Verificar diferentes tipos de documentos legales"""
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            document_type=doc_type,
            category="test",
            total_pages=5,
            file_hash="hash123",
            created_at=datetime.now()
        )
        assert doc.is_legal_document() == expected

    def test_is_small_document_true(self, sample_small_document):
        """Test: Documento pequeño (≤5 páginas) retorna True"""
        assert sample_small_document.is_small_document() is True
        assert sample_small_document.total_pages == 3

    def test_is_small_document_false(self, sample_document):
        """Test: Documento grande (>5 páginas) retorna False"""
        assert sample_document.is_small_document() is False
        assert sample_document.total_pages == 10

    @pytest.mark.parametrize("pages,expected", [
        (1, True),
        (3, True),
        (5, True),
        (6, False),
        (10, False),
        (100, False),
    ])
    def test_is_small_document_parametrized(self, pages, expected):
        """Test parametrizado: Verificar límite de páginas para documento pequeño"""
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            document_type="guia",
            category="test",
            total_pages=pages,
            file_hash="hash123",
            created_at=datetime.now()
        )
        assert doc.is_small_document() == expected

    def test_should_chunk_by_articles_true(self, sample_legal_document):
        """Test: Documento legal debe chunkearse por artículos"""
        assert sample_legal_document.should_chunk_by_articles() is True

    def test_should_chunk_by_articles_false(self, sample_document):
        """Test: Documento no legal no debe chunkearse por artículos"""
        assert sample_document.should_chunk_by_articles() is False

    def test_should_keep_as_single_chunk_true(self, sample_small_document):
        """Test: Documento pequeño de tipo formulario debe mantenerse como un chunk"""
        assert sample_small_document.should_keep_as_single_chunk() is True

    def test_should_keep_as_single_chunk_false_large_document(self, sample_document):
        """Test: Documento grande no debe mantenerse como un solo chunk"""
        assert sample_document.should_keep_as_single_chunk() is False

    def test_should_keep_as_single_chunk_false_wrong_type(self):
        """Test: Documento pequeño pero de tipo incorrecto no debe mantenerse como un chunk"""
        doc = Document(
            id="doc-test",
            filename="test.pdf",
            document_type="ley",  # Tipo legal, no formulario/guía
            category="normativa",
            total_pages=3,  # Pequeño
            file_hash="hash",
            created_at=datetime.now()
        )
        assert doc.should_keep_as_single_chunk() is False

    @pytest.mark.parametrize("pages,doc_type,expected", [
        (3, "formulario", True),
        (5, "guia", True),
        (3, "documento_general", True),
        (6, "formulario", False),  # Demasiadas páginas
        (3, "ley", False),  # Tipo incorrecto
        (10, "ordenanza", False),  # Ambos incorrectos
    ])
    def test_should_keep_as_single_chunk_parametrized(self, pages, doc_type, expected):
        """Test parametrizado: Verificar lógica de single chunk"""
        doc = Document(
            id="test-doc",
            filename="test.pdf",
            document_type=doc_type,
            category="test",
            total_pages=pages,
            file_hash="hash123",
            created_at=datetime.now()
        )
        assert doc.should_keep_as_single_chunk() == expected

    def test_document_with_optional_total_chunks(self):
        """Test: Documento con total_chunks opcional"""
        doc = Document(
            id="doc-test",
            filename="test.pdf",
            document_type="guia",
            category="general",
            total_pages=5,
            file_hash="hash",
            created_at=datetime.now()
        )
        assert doc.total_chunks is None

    def test_document_processing_status_default(self):
        """Test: processing_status tiene valor por defecto 'completed'"""
        doc = Document(
            id="doc-test",
            filename="test.pdf",
            document_type="guia",
            category="general",
            total_pages=5,
            file_hash="hash",
            created_at=datetime.now()
        )
        assert doc.processing_status == "completed"
