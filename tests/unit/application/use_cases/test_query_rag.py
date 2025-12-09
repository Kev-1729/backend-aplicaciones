"""
Unit tests for QueryRAGUseCase
"""
import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from application.use_cases.query_rag import QueryRAGUseCase
from application.dtos.query_dto import QueryInput, QueryOutput
from domain.entities.chat_message import ChatMessage


class TestQueryRAGUseCase:
    """Tests para QueryRAGUseCase"""

    @pytest.fixture
    def use_case(
        self,
        mock_embedding_service,
        mock_vector_store,
        mock_chat_service,
        mock_session_store
    ):
        """Fixture: Instancia de QueryRAGUseCase con mocks"""
        return QueryRAGUseCase(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            chat_service=mock_chat_service,
            session_store=mock_session_store,
            similarity_threshold=0.4,
            top_k=5,
            max_history_messages=10
        )

    @pytest.mark.asyncio
    async def test_execute_query_without_session(
        self,
        use_case,
        sample_query_input_no_session,
        mock_embedding_service,
        mock_vector_store,
        mock_chat_service
    ):
        """Test: Ejecutar query sin session_id (nueva conversación)"""
        result = await use_case.execute(sample_query_input_no_session)

        # Verificar que se generó el embedding
        mock_embedding_service.generate_query_embedding.assert_called_once()

        # Verificar que se buscaron chunks similares
        mock_vector_store.search_similar_chunks.assert_called_once()

        # Verificar que se generó respuesta con LLM
        mock_chat_service.generate_answer.assert_called_once()

        # Verificar resultado
        assert isinstance(result, QueryOutput)
        assert result.answer is not None
        assert len(result.sources) > 0

    @pytest.mark.asyncio
    async def test_execute_query_with_session(
        self,
        use_case,
        sample_query_input,
        mock_session_store,
        mock_embedding_service,
        mock_chat_service
    ):
        """Test: Ejecutar query con session_id (conversación existente)"""
        # Configurar mock: sesión existe con historial
        mock_session_store.session_exists.return_value = True
        mock_session_store.get_messages.return_value = [
            ChatMessage(
                role='user',
                content="¿Qué es una licencia?",
                created_at=datetime.now()
            ),
            ChatMessage(
                role='assistant',
                content="Una licencia es...",
                created_at=datetime.now()
            )
        ]

        result = await use_case.execute(sample_query_input)

        # Verificar que se cargó el historial
        # Nota: session_exists se llama 2 veces (en load_history y save_interaction)
        assert mock_session_store.session_exists.call_count >= 1
        mock_session_store.session_exists.assert_called_with("session-abc-123")
        mock_session_store.get_messages.assert_called_once()

        # Verificar que se guardaron los mensajes
        assert mock_session_store.add_message.call_count == 2  # user + assistant

        # Verificar que se pasó historial al LLM
        call_args = mock_chat_service.generate_answer.call_args
        assert 'conversation_history' in call_args.kwargs
        assert len(call_args.kwargs['conversation_history']) == 2

        assert isinstance(result, QueryOutput)

    @pytest.mark.asyncio
    async def test_execute_query_creates_new_session_if_not_exists(
        self,
        use_case,
        sample_query_input,
        mock_session_store
    ):
        """Test: Crear nueva sesión si no existe"""
        # Configurar mock: sesión NO existe
        mock_session_store.session_exists.return_value = False

        await use_case.execute(sample_query_input)

        # Verificar que se creó la sesión
        mock_session_store.create_session.assert_called_with("session-abc-123")

    @pytest.mark.asyncio
    async def test_execute_query_no_results_found(
        self,
        use_case,
        sample_query_input_no_session,
        mock_vector_store
    ):
        """Test: No se encuentran chunks similares"""
        # Configurar mock: búsqueda sin resultados
        mock_vector_store.search_similar_chunks.return_value = []

        result = await use_case.execute(sample_query_input_no_session)

        assert isinstance(result, QueryOutput)
        assert "No se encontraron resultados" in result.answer
        assert result.sources == []

    @pytest.mark.asyncio
    async def test_execute_query_special_command_help(self, use_case):
        """Test: Comando especial 'ayuda'"""
        query_input = QueryInput(query="ayuda", session_id=None)

        result = await use_case.execute(query_input)

        assert "Asistente de Trámites Municipales" in result.answer
        assert result.sources == []
        assert result.document_name == "Sistema de Ayuda"

    @pytest.mark.asyncio
    async def test_execute_query_special_command_faq(self, use_case):
        """Test: Comando especial 'faq'"""
        query_input = QueryInput(query="preguntas frecuentes", session_id=None)

        result = await use_case.execute(query_input)

        assert "Preguntas Frecuentes" in result.answer
        assert result.sources == []

    @pytest.mark.asyncio
    async def test_execute_query_special_command_topics(self, use_case):
        """Test: Comando especial 'temas disponibles'"""
        query_input = QueryInput(query="temas disponibles", session_id=None)

        result = await use_case.execute(query_input)

        assert "Temas Disponibles" in result.answer
        assert result.sources == []

    @pytest.mark.asyncio
    async def test_execute_query_special_command_rag_help(self, use_case):
        """Test: Comando especial 'ayuda con el RAG'"""
        query_input = QueryInput(query="ayuda con el RAG", session_id=None)

        result = await use_case.execute(query_input)

        assert "De qué trata este sistema RAG" in result.answer
        assert result.document_name == "Guía Técnica RAG"

    @pytest.mark.asyncio
    async def test_build_context_from_chunks(
        self,
        use_case,
        sample_similar_chunks
    ):
        """Test: Construcción de contexto desde chunks"""
        context = use_case._build_context(sample_similar_chunks)

        assert "Fuente 1:" in context
        assert "Fuente 2:" in context
        assert "Licencia_Funcionamiento.pdf" in context
        assert "Requisitos" in context

    @pytest.mark.asyncio
    async def test_handle_special_commands_none(self, use_case):
        """Test: Query normal no es comando especial"""
        result = use_case._handle_special_commands(
            "¿Cuánto cuesta una licencia de funcionamiento?"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_load_conversation_history_session_exists(
        self,
        use_case,
        mock_session_store,
        sample_conversation_history
    ):
        """Test: Cargar historial de sesión existente"""
        mock_session_store.session_exists.return_value = True
        mock_session_store.get_messages.return_value = sample_conversation_history

        history = await use_case._load_conversation_history("session-123")

        assert len(history) == 4
        mock_session_store.get_messages.assert_called_once_with("session-123", limit=10)

    @pytest.mark.asyncio
    async def test_load_conversation_history_session_not_exists(
        self,
        use_case,
        mock_session_store
    ):
        """Test: Cargar historial de sesión que no existe (crear nueva)"""
        mock_session_store.session_exists.return_value = False

        history = await use_case._load_conversation_history("session-new")

        assert len(history) == 0
        mock_session_store.create_session.assert_called_once_with("session-new")

    @pytest.mark.asyncio
    async def test_load_conversation_history_error_handling(
        self,
        use_case,
        mock_session_store
    ):
        """Test: Manejo de error al cargar historial (continuar sin historial)"""
        mock_session_store.session_exists.side_effect = Exception("Database error")

        history = await use_case._load_conversation_history("session-error")

        # Debería retornar lista vacía y no lanzar excepción
        assert history == []

    @pytest.mark.asyncio
    async def test_save_interaction(
        self,
        use_case,
        mock_session_store
    ):
        """Test: Guardar interacción usuario-asistente"""
        mock_session_store.session_exists.return_value = True

        await use_case._save_interaction(
            session_id="session-123",
            user_query="¿Cuánto cuesta?",
            assistant_answer="El costo es S/. 50.00",
            sources=["doc.pdf"]
        )

        # Verificar que se guardaron ambos mensajes (user + assistant)
        assert mock_session_store.add_message.call_count == 2

        # Verificar contenido de los mensajes
        user_msg_call = mock_session_store.add_message.call_args_list[0]
        assistant_msg_call = mock_session_store.add_message.call_args_list[1]

        user_msg = user_msg_call[0][1]
        assistant_msg = assistant_msg_call[0][1]

        assert user_msg.role == 'user'
        assert user_msg.content == "¿Cuánto cuesta?"

        assert assistant_msg.role == 'assistant'
        assert assistant_msg.content == "El costo es S/. 50.00"
        assert assistant_msg.metadata['sources'] == ["doc.pdf"]

    @pytest.mark.asyncio
    async def test_save_interaction_creates_session_if_not_exists(
        self,
        use_case,
        mock_session_store
    ):
        """Test: Guardar interacción crea sesión si no existe"""
        mock_session_store.session_exists.return_value = False

        await use_case._save_interaction(
            session_id="session-new",
            user_query="Test",
            assistant_answer="Answer",
            sources=[]
        )

        mock_session_store.create_session.assert_called_once_with("session-new")

    @pytest.mark.asyncio
    async def test_save_interaction_error_handling(
        self,
        use_case,
        mock_session_store
    ):
        """Test: Error al guardar interacción no detiene el flujo"""
        mock_session_store.add_message.side_effect = Exception("Save error")

        # No debería lanzar excepción
        await use_case._save_interaction(
            session_id="session-error",
            user_query="Test",
            assistant_answer="Answer",
            sources=[]
        )

    @pytest.mark.asyncio
    async def test_execute_extracts_unique_sources(
        self,
        use_case,
        sample_query_input_no_session,
        mock_vector_store
    ):
        """Test: Extracción de fuentes únicas"""
        # Configurar chunks con fuentes duplicadas
        mock_vector_store.search_similar_chunks.return_value = [
            {'chunk_id': '1', 'chunk_text': 'Text 1', 'filename': 'doc1.pdf', 'similarity_score': 0.9},
            {'chunk_id': '2', 'chunk_text': 'Text 2', 'filename': 'doc1.pdf', 'similarity_score': 0.85},
            {'chunk_id': '3', 'chunk_text': 'Text 3', 'filename': 'doc2.pdf', 'similarity_score': 0.8},
        ]

        result = await use_case.execute(sample_query_input_no_session)

        # Verificar que las fuentes son únicas
        assert len(result.sources) == 2
        assert set(result.sources) == {'doc1.pdf', 'doc2.pdf'}

    @pytest.mark.asyncio
    async def test_execute_passes_correct_parameters_to_vector_store(
        self,
        use_case,
        sample_query_input_no_session,
        mock_vector_store,
        mock_embedding_service
    ):
        """Test: Parámetros correctos al vector store"""
        embedding = [0.1] * 768
        mock_embedding_service.generate_query_embedding.return_value = embedding

        await use_case.execute(sample_query_input_no_session)

        # Verificar llamada al vector store con parámetros correctos
        mock_vector_store.search_similar_chunks.assert_called_once_with(
            embedding=embedding,
            threshold=0.4,
            limit=5
        )

    @pytest.mark.asyncio
    async def test_execute_passes_context_to_llm(
        self,
        use_case,
        sample_query_input_no_session,
        mock_chat_service
    ):
        """Test: Contexto correcto pasado al LLM"""
        await use_case.execute(sample_query_input_no_session)

        # Verificar que se llamó con query, context y conversation_history
        call_args = mock_chat_service.generate_answer.call_args
        assert 'query' in call_args.kwargs
        assert 'context' in call_args.kwargs
        assert 'conversation_history' in call_args.kwargs

    @pytest.mark.asyncio
    async def test_max_history_messages_limit(
        self,
        mock_embedding_service,
        mock_vector_store,
        mock_chat_service,
        mock_session_store
    ):
        """Test: Límite de mensajes en historial"""
        use_case = QueryRAGUseCase(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            chat_service=mock_chat_service,
            session_store=mock_session_store,
            max_history_messages=3  # Límite de 3 mensajes
        )

        # Simular sesión con 10 mensajes
        long_history = [
            ChatMessage(role='user', content=f"Message {i}", created_at=datetime.now())
            for i in range(10)
        ]
        mock_session_store.session_exists.return_value = True
        mock_session_store.get_messages.return_value = long_history

        query_input = QueryInput(query="Test", session_id="session-123")
        await use_case.execute(query_input)

        # Verificar que se solicitó solo el límite
        mock_session_store.get_messages.assert_called_once_with("session-123", limit=3)


class TestQueryRAGUseCaseEdgeCases:
    """Tests de casos extremos y errores"""

    @pytest.mark.asyncio
    async def test_empty_query_string(
        self,
        mock_embedding_service,
        mock_vector_store,
        mock_chat_service,
        mock_session_store
    ):
        """Test: Query vacía"""
        use_case = QueryRAGUseCase(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            chat_service=mock_chat_service,
            session_store=mock_session_store
        )

        # Query vacía debería ser manejada (probablemente retornar ayuda)
        query_input = QueryInput(query="", session_id=None)

        # Puede que necesite verificar el comportamiento esperado
        # dependiendo de cómo manejes queries vacías

    @pytest.mark.asyncio
    async def test_embedding_service_failure(
        self,
        mock_embedding_service,
        mock_vector_store,
        mock_chat_service,
        mock_session_store
    ):
        """Test: Fallo en servicio de embeddings"""
        use_case = QueryRAGUseCase(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            chat_service=mock_chat_service,
            session_store=mock_session_store
        )

        # Simular fallo en embedding
        mock_embedding_service.generate_query_embedding.side_effect = Exception("Embedding API error")

        query_input = QueryInput(query="Test query", session_id=None)

        with pytest.raises(Exception, match="Embedding API error"):
            await use_case.execute(query_input)

    @pytest.mark.asyncio
    async def test_vector_store_failure(
        self,
        mock_embedding_service,
        mock_vector_store,
        mock_chat_service,
        mock_session_store
    ):
        """Test: Fallo en vector store"""
        use_case = QueryRAGUseCase(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            chat_service=mock_chat_service,
            session_store=mock_session_store
        )

        # Simular fallo en búsqueda
        mock_vector_store.search_similar_chunks.side_effect = Exception("Database error")

        query_input = QueryInput(query="Test query", session_id=None)

        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(query_input)

    @pytest.mark.asyncio
    async def test_llm_service_failure(
        self,
        mock_embedding_service,
        mock_vector_store,
        mock_chat_service,
        mock_session_store
    ):
        """Test: Fallo en servicio de chat (LLM)"""
        use_case = QueryRAGUseCase(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            chat_service=mock_chat_service,
            session_store=mock_session_store
        )

        # Simular fallo en LLM
        mock_chat_service.generate_answer.side_effect = Exception("LLM timeout")

        query_input = QueryInput(query="Test query", session_id=None)

        with pytest.raises(Exception, match="LLM timeout"):
            await use_case.execute(query_input)
