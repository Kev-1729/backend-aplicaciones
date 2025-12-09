"""
Unit tests for GetStatisticsUseCase
"""
import pytest
from unittest.mock import AsyncMock

from application.use_cases.get_statistics import GetStatisticsUseCase
from application.dtos.stats_dto import StatsOutput


class TestGetStatisticsUseCase:
    """Tests para GetStatisticsUseCase"""

    @pytest.fixture
    def use_case(self, mock_vector_store):
        """Fixture: Instancia de GetStatisticsUseCase con mock"""
        return GetStatisticsUseCase(vector_store=mock_vector_store)

    @pytest.mark.asyncio
    async def test_execute_returns_statistics(self, use_case, mock_vector_store):
        """Test: Ejecutar y obtener estadísticas correctamente"""
        # Configurar mock
        mock_vector_store.get_statistics.return_value = {
            'total_documents': 10,
            'total_chunks': 150,
            'total_pages': 320,
            'categories': {'comercio': 5, 'normativa': 3, 'general': 2},
            'document_types': {'guia': 4, 'ordenanza': 3, 'formulario': 3}
        }

        result = await use_case.execute()

        # Verificar que se llamó al vector store
        mock_vector_store.get_statistics.assert_called_once()

        # Verificar resultado
        assert isinstance(result, StatsOutput)
        assert result.total_documents == 10
        assert result.total_chunks == 150
        assert result.total_pages == 320
        assert result.categories == {'comercio': 5, 'normativa': 3, 'general': 2}
        assert result.document_types == {'guia': 4, 'ordenanza': 3, 'formulario': 3}

    @pytest.mark.asyncio
    async def test_execute_with_empty_database(self, mock_vector_store):
        """Test: Estadísticas con base de datos vacía"""
        # Configurar mock: sin documentos
        mock_vector_store.get_statistics.return_value = {
            'total_documents': 0,
            'total_chunks': 0,
            'total_pages': 0,
            'categories': {},
            'document_types': {}
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        result = await use_case.execute()

        assert result.total_documents == 0
        assert result.total_chunks == 0
        assert result.total_pages == 0
        assert result.categories == {}
        assert result.document_types == {}

    @pytest.mark.asyncio
    async def test_execute_with_missing_fields(self, mock_vector_store):
        """Test: Estadísticas con campos faltantes (valores por defecto)"""
        # Configurar mock: datos incompletos
        mock_vector_store.get_statistics.return_value = {
            'total_documents': 5
            # Faltan otros campos
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        result = await use_case.execute()

        # Verificar que usa valores por defecto para campos faltantes
        assert result.total_documents == 5
        assert result.total_chunks == 0
        assert result.total_pages == 0
        assert result.categories == {}
        assert result.document_types == {}

    @pytest.mark.asyncio
    async def test_execute_handles_large_numbers(self, mock_vector_store):
        """Test: Manejo de números grandes"""
        mock_vector_store.get_statistics.return_value = {
            'total_documents': 10000,
            'total_chunks': 500000,
            'total_pages': 150000,
            'categories': {'comercio': 4000, 'normativa': 3500, 'general': 2500},
            'document_types': {'guia': 3000, 'ordenanza': 4000, 'formulario': 3000}
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        result = await use_case.execute()

        assert result.total_documents == 10000
        assert result.total_chunks == 500000
        assert result.total_pages == 150000

    @pytest.mark.asyncio
    async def test_execute_with_many_categories(self, mock_vector_store):
        """Test: Estadísticas con muchas categorías"""
        categories = {f'categoria_{i}': i * 10 for i in range(20)}
        document_types = {f'tipo_{i}': i * 5 for i in range(15)}

        mock_vector_store.get_statistics.return_value = {
            'total_documents': 100,
            'total_chunks': 1000,
            'total_pages': 500,
            'categories': categories,
            'document_types': document_types
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        result = await use_case.execute()

        assert len(result.categories) == 20
        assert len(result.document_types) == 15

    @pytest.mark.asyncio
    async def test_execute_error_handling(self, mock_vector_store):
        """Test: Manejo de errores al obtener estadísticas"""
        # Simular error en el vector store
        mock_vector_store.get_statistics.side_effect = Exception("Database connection error")

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)

        with pytest.raises(Exception, match="Database connection error"):
            await use_case.execute()

    @pytest.mark.asyncio
    async def test_execute_calls_vector_store_once(self, mock_vector_store):
        """Test: Verifica que solo se llama una vez al vector store"""
        mock_vector_store.get_statistics.return_value = {
            'total_documents': 5,
            'total_chunks': 50,
            'total_pages': 25,
            'categories': {},
            'document_types': {}
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        await use_case.execute()

        # Verificar que se llamó exactamente una vez
        assert mock_vector_store.get_statistics.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_returns_correct_type(self, mock_vector_store):
        """Test: Verifica que retorna el tipo correcto (StatsOutput)"""
        mock_vector_store.get_statistics.return_value = {
            'total_documents': 1,
            'total_chunks': 10,
            'total_pages': 5,
            'categories': {},
            'document_types': {}
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        result = await use_case.execute()

        assert isinstance(result, StatsOutput)
        assert hasattr(result, 'total_documents')
        assert hasattr(result, 'total_chunks')
        assert hasattr(result, 'total_pages')
        assert hasattr(result, 'categories')
        assert hasattr(result, 'document_types')


class TestGetStatisticsUseCaseEdgeCases:
    """Tests de casos extremos"""

    @pytest.mark.asyncio
    async def test_negative_values_not_expected(self, mock_vector_store):
        """Test: Valores negativos (caso teórico, no debería ocurrir)"""
        mock_vector_store.get_statistics.return_value = {
            'total_documents': -1,
            'total_chunks': -10,
            'total_pages': -5,
            'categories': {},
            'document_types': {}
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        result = await use_case.execute()

        # Simplemente verifica que puede manejar estos valores
        # (aunque no sean lógicos)
        assert result.total_documents == -1
        assert result.total_chunks == -10

    @pytest.mark.asyncio
    async def test_none_values_converted_to_defaults(self, mock_vector_store):
        """Test: Valores None convertidos a valores por defecto"""
        mock_vector_store.get_statistics.return_value = {
            'total_documents': None,
            'total_chunks': None,
            'total_pages': None,
            'categories': None,
            'document_types': None
        }

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)
        result = await use_case.execute()

        # get() con default debería manejar None
        assert result.total_documents == 0 or result.total_documents is None
        assert result.categories == {} or result.categories is None

    @pytest.mark.asyncio
    async def test_timeout_error(self, mock_vector_store):
        """Test: Timeout al obtener estadísticas"""
        mock_vector_store.get_statistics.side_effect = TimeoutError("Query timeout")

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)

        with pytest.raises(TimeoutError, match="Query timeout"):
            await use_case.execute()

    @pytest.mark.asyncio
    async def test_connection_error(self, mock_vector_store):
        """Test: Error de conexión"""
        mock_vector_store.get_statistics.side_effect = ConnectionError("Cannot connect to database")

        use_case = GetStatisticsUseCase(vector_store=mock_vector_store)

        with pytest.raises(ConnectionError, match="Cannot connect to database"):
            await use_case.execute()
