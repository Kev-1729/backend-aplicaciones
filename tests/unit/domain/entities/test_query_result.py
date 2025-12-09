"""
Tests para las entidades QueryResult y SimilarChunk
"""
import pytest
from domain.entities.query_result import QueryResult, SimilarChunk


class TestSimilarChunk:
    """Tests para la entidad SimilarChunk"""

    def test_create_similar_chunk(self):
        """Prueba creación básica de SimilarChunk"""
        chunk = SimilarChunk(
            text="Contenido del chunk",
            document_name="documento.pdf",
            document_id="doc-123",
            page_number=5,
            similarity_score=0.85
        )

        assert chunk.text == "Contenido del chunk"
        assert chunk.document_name == "documento.pdf"
        assert chunk.document_id == "doc-123"
        assert chunk.page_number == 5
        assert chunk.similarity_score == 0.85
        assert chunk.metadata is None

    def test_create_similar_chunk_with_metadata(self):
        """Prueba creación de SimilarChunk con metadata"""
        chunk = SimilarChunk(
            text="Contenido",
            document_name="doc.pdf",
            document_id="123",
            page_number=1,
            similarity_score=0.9,
            metadata={"category": "legal", "year": 2024}
        )

        assert chunk.metadata == {"category": "legal", "year": 2024}


class TestQueryResult:
    """Tests para la entidad QueryResult"""

    def test_create_query_result(self):
        """Prueba creación básica de QueryResult"""
        chunks = [
            SimilarChunk(
                text="Chunk 1",
                document_name="doc1.pdf",
                document_id="1",
                page_number=1,
                similarity_score=0.9
            )
        ]

        result = QueryResult(
            query="¿Cómo solicitar licencia?",
            answer="Debes presentar DNI.",
            sources=["doc1.pdf"],
            similar_chunks=chunks
        )

        assert result.query == "¿Cómo solicitar licencia?"
        assert result.answer == "Debes presentar DNI."
        assert result.sources == ["doc1.pdf"]
        assert len(result.similar_chunks) == 1
        assert result.document_name is None
        assert result.download_url is None

    def test_create_query_result_with_all_fields(self):
        """Prueba creación de QueryResult con todos los campos"""
        chunks = [
            SimilarChunk(
                text="Chunk 1",
                document_name="doc1.pdf",
                document_id="1",
                page_number=1,
                similarity_score=0.9
            )
        ]

        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf", "doc2.pdf"],
            similar_chunks=chunks,
            document_name="Principal.pdf",
            download_url="https://example.com/download"
        )

        assert result.document_name == "Principal.pdf"
        assert result.download_url == "https://example.com/download"

    def test_has_sources_true(self):
        """Prueba has_sources cuando hay fuentes"""
        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf"],
            similar_chunks=[]
        )

        assert result.has_sources() is True

    def test_has_sources_false(self):
        """Prueba has_sources cuando no hay fuentes"""
        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=[],
            similar_chunks=[]
        )

        assert result.has_sources() is False

    def test_has_sources_multiple(self):
        """Prueba has_sources con múltiples fuentes"""
        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
            similar_chunks=[]
        )

        assert result.has_sources() is True

    def test_get_unique_documents(self):
        """Prueba obtener documentos únicos"""
        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf", "doc2.pdf", "doc1.pdf", "doc3.pdf", "doc2.pdf"],
            similar_chunks=[]
        )

        unique = result.get_unique_documents()

        assert len(unique) == 3
        assert set(unique) == {"doc1.pdf", "doc2.pdf", "doc3.pdf"}

    def test_get_unique_documents_empty(self):
        """Prueba obtener documentos únicos cuando no hay fuentes"""
        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=[],
            similar_chunks=[]
        )

        unique = result.get_unique_documents()

        assert len(unique) == 0
        assert unique == []

    def test_get_unique_documents_single(self):
        """Prueba obtener documentos únicos con una sola fuente"""
        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf"],
            similar_chunks=[]
        )

        unique = result.get_unique_documents()

        assert len(unique) == 1
        assert unique == ["doc1.pdf"]

    def test_get_average_similarity_single_chunk(self):
        """Prueba promedio de similitud con un chunk"""
        chunks = [
            SimilarChunk(
                text="Chunk 1",
                document_name="doc1.pdf",
                document_id="1",
                page_number=1,
                similarity_score=0.85
            )
        ]

        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf"],
            similar_chunks=chunks
        )

        avg = result.get_average_similarity()

        assert avg == 0.85

    def test_get_average_similarity_multiple_chunks(self):
        """Prueba promedio de similitud con múltiples chunks"""
        chunks = [
            SimilarChunk(
                text="Chunk 1",
                document_name="doc1.pdf",
                document_id="1",
                page_number=1,
                similarity_score=0.9
            ),
            SimilarChunk(
                text="Chunk 2",
                document_name="doc2.pdf",
                document_id="2",
                page_number=2,
                similarity_score=0.8
            ),
            SimilarChunk(
                text="Chunk 3",
                document_name="doc3.pdf",
                document_id="3",
                page_number=3,
                similarity_score=0.7
            )
        ]

        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
            similar_chunks=chunks
        )

        avg = result.get_average_similarity()

        expected = (0.9 + 0.8 + 0.7) / 3
        assert abs(avg - expected) < 0.0001  # Comparación con tolerancia para floats

    def test_get_average_similarity_empty_chunks(self):
        """Prueba promedio de similitud sin chunks"""
        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=[],
            similar_chunks=[]
        )

        avg = result.get_average_similarity()

        assert avg == 0.0

    def test_get_average_similarity_high_precision(self):
        """Prueba promedio de similitud con alta precisión"""
        chunks = [
            SimilarChunk(
                text="Chunk 1",
                document_name="doc1.pdf",
                document_id="1",
                page_number=1,
                similarity_score=0.8765
            ),
            SimilarChunk(
                text="Chunk 2",
                document_name="doc2.pdf",
                document_id="2",
                page_number=2,
                similarity_score=0.9234
            )
        ]

        result = QueryResult(
            query="Pregunta",
            answer="Respuesta",
            sources=["doc1.pdf", "doc2.pdf"],
            similar_chunks=chunks
        )

        avg = result.get_average_similarity()

        expected = (0.8765 + 0.9234) / 2
        assert abs(avg - expected) < 0.0001  # Comparación con tolerancia

    def test_integration_complete_query_result(self):
        """Prueba integración completa con escenario real"""
        chunks = [
            SimilarChunk(
                text="Para solicitar una licencia de construcción...",
                document_name="Ley de Construcción 2024.pdf",
                document_id="ley-123",
                page_number=15,
                similarity_score=0.92,
                metadata={"category": "ley", "year": 2024}
            ),
            SimilarChunk(
                text="Los requisitos incluyen DNI, RUC...",
                document_name="Reglamento de Licencias.pdf",
                document_id="reg-456",
                page_number=8,
                similarity_score=0.88,
                metadata={"category": "reglamento", "year": 2023}
            ),
            SimilarChunk(
                text="Formulario de solicitud disponible en...",
                document_name="Guía de Trámites.pdf",
                document_id="guia-789",
                page_number=3,
                similarity_score=0.75,
                metadata={"category": "guia", "year": 2024}
            )
        ]

        result = QueryResult(
            query="¿Cómo solicitar licencia de construcción?",
            answer="Para solicitar una licencia de construcción debes presentar DNI, RUC y el formulario de solicitud.",
            sources=[
                "Ley de Construcción 2024.pdf",
                "Reglamento de Licencias.pdf",
                "Guía de Trámites.pdf"
            ],
            similar_chunks=chunks,
            document_name="Ley de Construcción 2024.pdf",
            download_url="https://storage.example.com/ley-construccion-2024.pdf"
        )

        # Verificar resultado
        assert result.has_sources() is True
        assert len(result.get_unique_documents()) == 3

        avg_similarity = result.get_average_similarity()
        expected_avg = (0.92 + 0.88 + 0.75) / 3
        assert abs(avg_similarity - expected_avg) < 0.01

        # Verificar chunks
        assert len(result.similar_chunks) == 3
        assert result.similar_chunks[0].metadata["category"] == "ley"
        assert result.similar_chunks[1].page_number == 8
        assert result.similar_chunks[2].similarity_score == 0.75
