"""
Tests para Stats DTOs
"""
import pytest
from application.dtos.stats_dto import StatsOutput


class TestStatsOutput:
    """Tests para StatsOutput DTO"""

    def test_create_stats_output(self):
        """Prueba creación básica de StatsOutput"""
        stats = StatsOutput(
            total_documents=100,
            total_chunks=500,
            total_pages=1200,
            categories={"legal": 50, "administrativo": 50},
            document_types={"ley": 30, "ordenanza": 70}
        )

        assert stats.total_documents == 100
        assert stats.total_chunks == 500
        assert stats.total_pages == 1200
        assert stats.categories == {"legal": 50, "administrativo": 50}
        assert stats.document_types == {"ley": 30, "ordenanza": 70}

    def test_create_stats_output_empty_collections(self):
        """Prueba creación de StatsOutput con colecciones vacías"""
        stats = StatsOutput(
            total_documents=0,
            total_chunks=0,
            total_pages=0,
            categories={},
            document_types={}
        )

        assert stats.total_documents == 0
        assert stats.total_chunks == 0
        assert stats.total_pages == 0
        assert stats.categories == {}
        assert stats.document_types == {}

    def test_to_dict(self):
        """Prueba conversión a diccionario"""
        stats = StatsOutput(
            total_documents=50,
            total_chunks=200,
            total_pages=300,
            categories={"legal": 30, "administrativo": 20},
            document_types={"ley": 25, "decreto": 25}
        )

        result = stats.to_dict()

        assert result == {
            "total_documents": 50,
            "total_chunks": 200,
            "total_pages": 300,
            "categories": {"legal": 30, "administrativo": 20},
            "document_types": {"ley": 25, "decreto": 25}
        }

    def test_to_dict_preserves_structure(self):
        """Prueba que to_dict preserva la estructura exacta"""
        stats = StatsOutput(
            total_documents=10,
            total_chunks=50,
            total_pages=100,
            categories={"cat1": 5, "cat2": 3, "cat3": 2},
            document_types={"type1": 4, "type2": 6}
        )

        result = stats.to_dict()

        # Verificar que todas las keys están presentes
        assert "total_documents" in result
        assert "total_chunks" in result
        assert "total_pages" in result
        assert "categories" in result
        assert "document_types" in result

        # Verificar valores
        assert result["total_documents"] == 10
        assert result["total_chunks"] == 50
        assert result["total_pages"] == 100

        # Verificar diccionarios anidados
        assert len(result["categories"]) == 3
        assert len(result["document_types"]) == 2

    def test_categories_with_multiple_entries(self):
        """Prueba categorías con múltiples entradas"""
        stats = StatsOutput(
            total_documents=150,
            total_chunks=800,
            total_pages=2000,
            categories={
                "legal": 50,
                "administrativo": 40,
                "fiscal": 30,
                "laboral": 20,
                "otros": 10
            },
            document_types={"ley": 100, "ordenanza": 50}
        )

        assert len(stats.categories) == 5
        assert stats.categories["legal"] == 50
        assert stats.categories["otros"] == 10

    def test_document_types_with_multiple_entries(self):
        """Prueba tipos de documento con múltiples entradas"""
        stats = StatsOutput(
            total_documents=200,
            total_chunks=1000,
            total_pages=3000,
            categories={"legal": 200},
            document_types={
                "ley": 80,
                "ordenanza": 50,
                "decreto": 30,
                "reglamento": 20,
                "resolucion": 15,
                "otros": 5
            }
        )

        assert len(stats.document_types) == 6
        assert stats.document_types["ley"] == 80
        assert stats.document_types["otros"] == 5

    def test_large_numbers(self):
        """Prueba con números grandes"""
        stats = StatsOutput(
            total_documents=10000,
            total_chunks=500000,
            total_pages=1000000,
            categories={"legal": 10000},
            document_types={"ley": 10000}
        )

        result = stats.to_dict()

        assert result["total_documents"] == 10000
        assert result["total_chunks"] == 500000
        assert result["total_pages"] == 1000000

    @pytest.mark.parametrize("total_docs,total_chunks,total_pages", [
        (0, 0, 0),
        (1, 1, 1),
        (10, 50, 100),
        (100, 500, 1000),
        (1000, 5000, 10000),
    ])
    def test_various_totals(self, total_docs, total_chunks, total_pages):
        """Prueba con varios valores de totales"""
        stats = StatsOutput(
            total_documents=total_docs,
            total_chunks=total_chunks,
            total_pages=total_pages,
            categories={},
            document_types={}
        )

        assert stats.total_documents == total_docs
        assert stats.total_chunks == total_chunks
        assert stats.total_pages == total_pages

    def test_integration_realistic_stats(self):
        """Prueba integración con estadísticas realistas"""
        stats = StatsOutput(
            total_documents=247,
            total_chunks=3856,
            total_pages=8912,
            categories={
                "legal": 120,
                "administrativo": 85,
                "fiscal": 42
            },
            document_types={
                "ley": 89,
                "ordenanza": 78,
                "decreto": 45,
                "reglamento": 35
            }
        )

        result = stats.to_dict()

        # Verificar que los totales de categorías y tipos suman correctamente
        total_categories = sum(stats.categories.values())
        total_types = sum(stats.document_types.values())

        assert total_categories == 247
        assert total_types == 247
        assert result["total_documents"] == 247

        # Verificar estructura del diccionario
        assert isinstance(result, dict)
        assert isinstance(result["categories"], dict)
        assert isinstance(result["document_types"], dict)
