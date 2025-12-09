"""
Tests para Query DTOs
"""
import pytest
from application.dtos.query_dto import QueryInput, QueryOutput


class TestQueryInput:
    """Tests para QueryInput DTO"""

    def test_create_query_input(self):
        """Prueba creación básica de QueryInput"""
        query_input = QueryInput(query="¿Cómo solicitar licencia?")

        assert query_input.query == "¿Cómo solicitar licencia?"
        assert query_input.session_id is None

    def test_create_query_input_with_session(self):
        """Prueba creación de QueryInput con session_id"""
        query_input = QueryInput(
            query="¿Requisitos?",
            session_id="session-123"
        )

        assert query_input.query == "¿Requisitos?"
        assert query_input.session_id == "session-123"

    def test_is_valid_true(self):
        """Prueba is_valid con query válida"""
        query_input = QueryInput(query="Pregunta válida")
        assert query_input.is_valid() is True

    def test_is_valid_false_empty(self):
        """Prueba is_valid con query vacía"""
        query_input = QueryInput(query="")
        assert query_input.is_valid() is False

    def test_is_valid_false_whitespace(self):
        """Prueba is_valid con query de solo espacios"""
        query_input = QueryInput(query="   ")
        assert query_input.is_valid() is False

    def test_is_valid_false_none(self):
        """Prueba is_valid con query None"""
        query_input = QueryInput(query=None)
        assert query_input.is_valid() is False

    @pytest.mark.parametrize("query,expected", [
        ("Pregunta válida", True),
        ("¿Cómo?", True),
        ("a", True),
        ("", False),
        ("   ", False),
        ("\t\n", False),
        (None, False),
    ])
    def test_is_valid_parametrized(self, query, expected):
        """Prueba is_valid con múltiples valores"""
        query_input = QueryInput(query=query)
        assert query_input.is_valid() is expected


class TestQueryOutput:
    """Tests para QueryOutput DTO"""

    def test_create_query_output(self):
        """Prueba creación básica de QueryOutput"""
        output = QueryOutput(
            answer="Debes presentar DNI.",
            sources=["doc1.pdf"]
        )

        assert output.answer == "Debes presentar DNI."
        assert output.sources == ["doc1.pdf"]
        assert output.document_name is None
        assert output.download_url is None

    def test_create_query_output_with_all_fields(self):
        """Prueba creación de QueryOutput con todos los campos"""
        output = QueryOutput(
            answer="Respuesta completa",
            sources=["doc1.pdf", "doc2.pdf"],
            document_name="Principal.pdf",
            download_url="https://example.com/download"
        )

        assert output.answer == "Respuesta completa"
        assert len(output.sources) == 2
        assert output.document_name == "Principal.pdf"
        assert output.download_url == "https://example.com/download"

    def test_to_dict(self):
        """Prueba conversión a diccionario"""
        output = QueryOutput(
            answer="Respuesta",
            sources=["doc1.pdf"],
            document_name="Principal.pdf",
            download_url="https://example.com/download"
        )

        result = output.to_dict()

        assert result == {
            "answer": "Respuesta",
            "sources": ["doc1.pdf"],
            "document_name": "Principal.pdf",
            "download_url": "https://example.com/download"
        }

    def test_to_dict_minimal(self):
        """Prueba conversión a diccionario con campos mínimos"""
        output = QueryOutput(
            answer="Respuesta",
            sources=[]
        )

        result = output.to_dict()

        assert result == {
            "answer": "Respuesta",
            "sources": [],
            "document_name": None,
            "download_url": None
        }

    def test_to_dict_multiple_sources(self):
        """Prueba conversión a diccionario con múltiples fuentes"""
        output = QueryOutput(
            answer="Respuesta",
            sources=["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        )

        result = output.to_dict()

        assert len(result["sources"]) == 3
        assert "doc1.pdf" in result["sources"]
        assert "doc2.pdf" in result["sources"]
        assert "doc3.pdf" in result["sources"]

    def test_empty_sources_list(self):
        """Prueba con lista de fuentes vacía"""
        output = QueryOutput(
            answer="No se encontraron resultados",
            sources=[]
        )

        assert output.sources == []
        assert len(output.sources) == 0
