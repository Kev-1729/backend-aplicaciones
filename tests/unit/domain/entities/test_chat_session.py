"""
Unit tests for ChatSession entity
"""
import pytest
from datetime import datetime
from domain.entities.chat_session import ChatSession
from domain.entities.chat_message import ChatMessage


class TestChatSession:
    """Tests para la entidad ChatSession"""

    def test_create_empty_session(self, empty_chat_session):
        """Test: Crear sesión vacía correctamente"""
        assert empty_chat_session.session_id == "session-empty-001"
        assert empty_chat_session.user_id == "user-789"
        assert len(empty_chat_session.messages) == 0
        assert empty_chat_session.has_messages() is False

    def test_create_session_with_messages(self, sample_chat_session):
        """Test: Crear sesión con mensajes"""
        assert sample_chat_session.session_id == "session-abc-123"
        assert len(sample_chat_session.messages) == 2
        assert sample_chat_session.has_messages() is True

    def test_empty_session_id_raises_error(self):
        """Test: session_id vacío lanza ValueError"""
        with pytest.raises(ValueError, match="session_id no puede estar vacío"):
            ChatSession(session_id="")

    def test_whitespace_session_id_raises_error(self):
        """Test: session_id solo con espacios lanza ValueError"""
        with pytest.raises(ValueError, match="session_id no puede estar vacío"):
            ChatSession(session_id="   ")

    def test_add_message(self, empty_chat_session, sample_user_message):
        """Test: Agregar mensaje a sesión"""
        initial_count = empty_chat_session.get_message_count()
        empty_chat_session.add_message(sample_user_message)

        assert empty_chat_session.get_message_count() == initial_count + 1
        assert empty_chat_session.messages[-1] == sample_user_message

    def test_add_multiple_messages(self, empty_chat_session):
        """Test: Agregar múltiples mensajes"""
        messages = [
            ChatMessage(role='user', content=f"Message {i}", created_at=datetime.now())
            for i in range(5)
        ]

        for msg in messages:
            empty_chat_session.add_message(msg)

        assert empty_chat_session.get_message_count() == 5

    def test_get_message_count(self, sample_chat_session):
        """Test: Obtener conteo de mensajes"""
        assert sample_chat_session.get_message_count() == 2

    def test_get_user_messages(self, sample_chat_session):
        """Test: Filtrar solo mensajes de usuario"""
        user_msgs = sample_chat_session.get_user_messages()

        assert len(user_msgs) == 1
        assert all(msg.is_user_message() for msg in user_msgs)

    def test_get_assistant_messages(self, sample_chat_session):
        """Test: Filtrar solo mensajes del asistente"""
        assistant_msgs = sample_chat_session.get_assistant_messages()

        assert len(assistant_msgs) == 1
        assert all(msg.is_assistant_message() for msg in assistant_msgs)

    def test_get_recent_messages_within_limit(self, sample_chat_session):
        """Test: Obtener mensajes recientes dentro del límite"""
        recent = sample_chat_session.get_recent_messages(limit=5)

        assert len(recent) == 2  # Solo hay 2 mensajes

    def test_get_recent_messages_exceed_limit(self):
        """Test: Obtener mensajes recientes con límite menor a total"""
        session = ChatSession(session_id="session-test")

        # Agregar 10 mensajes
        for i in range(10):
            session.add_message(
                ChatMessage(
                    role='user' if i % 2 == 0 else 'assistant',
                    content=f"Message {i}",
                    created_at=datetime.now()
                )
            )

        recent = session.get_recent_messages(limit=5)
        assert len(recent) == 5
        assert recent[0].content == "Message 5"  # Debería empezar desde el mensaje 5

    def test_get_recent_messages_zero_limit(self, sample_chat_session):
        """Test: Límite 0 retorna todos los mensajes"""
        recent = sample_chat_session.get_recent_messages(limit=0)
        assert len(recent) == sample_chat_session.get_message_count()

    def test_get_recent_messages_negative_limit(self, sample_chat_session):
        """Test: Límite negativo retorna todos los mensajes"""
        recent = sample_chat_session.get_recent_messages(limit=-1)
        assert len(recent) == sample_chat_session.get_message_count()

    def test_get_conversation_context(self, sample_chat_session):
        """Test: Generar contexto de conversación"""
        context = sample_chat_session.get_conversation_context(max_messages=10)

        assert "Usuario:" in context
        assert "Asistente:" in context
        assert "licencia de funcionamiento" in context

    def test_get_conversation_context_empty_session(self, empty_chat_session):
        """Test: Contexto de sesión vacía retorna string vacío"""
        context = empty_chat_session.get_conversation_context()
        assert context == ""

    def test_get_conversation_context_with_limit(self):
        """Test: Contexto limitado a N mensajes"""
        session = ChatSession(session_id="session-test")

        # Agregar 6 mensajes
        for i in range(6):
            session.add_message(
                ChatMessage(
                    role='user' if i % 2 == 0 else 'assistant',
                    content=f"Message {i}",
                    created_at=datetime.now()
                )
            )

        context = session.get_conversation_context(max_messages=3)

        # Debería incluir solo los últimos 3 mensajes
        assert "Message 3" in context
        assert "Message 4" in context
        assert "Message 5" in context
        assert "Message 0" not in context
        assert "Message 1" not in context

    def test_clear_history(self, sample_chat_session):
        """Test: Limpiar historial de mensajes"""
        assert sample_chat_session.has_messages() is True

        sample_chat_session.clear_history()

        assert sample_chat_session.has_messages() is False
        assert sample_chat_session.get_message_count() == 0

    def test_has_messages_true(self, sample_chat_session):
        """Test: has_messages retorna True cuando hay mensajes"""
        assert sample_chat_session.has_messages() is True

    def test_has_messages_false(self, empty_chat_session):
        """Test: has_messages retorna False cuando no hay mensajes"""
        assert empty_chat_session.has_messages() is False

    def test_to_dict(self, sample_chat_session):
        """Test: Conversión a diccionario"""
        session_dict = sample_chat_session.to_dict()

        assert session_dict['session_id'] == "session-abc-123"
        assert session_dict['user_id'] == "user-456"
        assert session_dict['message_count'] == 2
        assert len(session_dict['messages']) == 2
        assert 'created_at' in session_dict
        assert 'updated_at' in session_dict

    def test_to_dict_empty_session(self, empty_chat_session):
        """Test: Conversión a diccionario de sesión vacía"""
        session_dict = empty_chat_session.to_dict()

        assert session_dict['message_count'] == 0
        assert session_dict['messages'] == []
        assert session_dict['metadata'] == {}

    def test_session_with_metadata(self):
        """Test: Sesión con metadata personalizado"""
        metadata = {
            "platform": "web",
            "browser": "Chrome",
            "version": "1.0"
        }
        session = ChatSession(
            session_id="session-meta",
            metadata=metadata
        )

        assert session.metadata == metadata
        assert session.to_dict()['metadata'] == metadata

    def test_updated_at_changes_on_add_message(self, empty_chat_session):
        """Test: updated_at se actualiza al agregar mensaje"""
        original_updated_at = empty_chat_session.updated_at

        # Simular paso del tiempo
        import time
        time.sleep(0.1)

        empty_chat_session.add_message(
            ChatMessage(
                role='user',
                content="Test",
                created_at=datetime.now()
            )
        )

        assert empty_chat_session.updated_at > original_updated_at

    def test_updated_at_changes_on_clear_history(self, sample_chat_session):
        """Test: updated_at se actualiza al limpiar historial"""
        original_updated_at = sample_chat_session.updated_at

        # Simular paso del tiempo
        import time
        time.sleep(0.1)

        sample_chat_session.clear_history()

        assert sample_chat_session.updated_at > original_updated_at

    def test_conversation_flow(self):
        """Test: Flujo completo de conversación"""
        session = ChatSession(session_id="session-flow", user_id="user-123")

        # Usuario hace pregunta
        session.add_message(ChatMessage(
            role='user',
            content="¿Cómo saco una licencia?",
            created_at=datetime.now()
        ))

        # Asistente responde
        session.add_message(ChatMessage(
            role='assistant',
            content="Necesitas presentar DNI y RUC",
            created_at=datetime.now()
        ))

        # Usuario hace seguimiento
        session.add_message(ChatMessage(
            role='user',
            content="¿Cuánto cuesta?",
            created_at=datetime.now()
        ))

        # Asistente responde
        session.add_message(ChatMessage(
            role='assistant',
            content="El costo es de S/. 50.00",
            created_at=datetime.now()
        ))

        assert session.get_message_count() == 4
        assert len(session.get_user_messages()) == 2
        assert len(session.get_assistant_messages()) == 2

        context = session.get_conversation_context()
        assert "¿Cómo saco una licencia?" in context
        assert "S/. 50.00" in context
