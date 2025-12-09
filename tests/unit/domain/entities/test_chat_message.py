"""
Unit tests for ChatMessage entity
"""
import pytest
from datetime import datetime
from domain.entities.chat_message import ChatMessage


class TestChatMessage:
    """Tests para la entidad ChatMessage"""

    def test_create_user_message(self, sample_user_message):
        """Test: Crear mensaje de usuario correctamente"""
        assert sample_user_message.role == 'user'
        assert "licencia de funcionamiento" in sample_user_message.content
        assert isinstance(sample_user_message.created_at, datetime)

    def test_create_assistant_message(self, sample_assistant_message):
        """Test: Crear mensaje del asistente correctamente"""
        assert sample_assistant_message.role == 'assistant'
        assert "Para obtener" in sample_assistant_message.content
        assert sample_assistant_message.metadata is not None
        assert "sources" in sample_assistant_message.metadata

    def test_create_system_message(self):
        """Test: Crear mensaje del sistema correctamente"""
        msg = ChatMessage(
            role='system',
            content="Sistema iniciado correctamente",
            created_at=datetime.now()
        )
        assert msg.role == 'system'
        assert msg.content == "Sistema iniciado correctamente"

    def test_is_user_message_true(self, sample_user_message):
        """Test: is_user_message retorna True para mensaje de usuario"""
        assert sample_user_message.is_user_message() is True

    def test_is_user_message_false(self, sample_assistant_message):
        """Test: is_user_message retorna False para mensaje del asistente"""
        assert sample_assistant_message.is_user_message() is False

    def test_is_assistant_message_true(self, sample_assistant_message):
        """Test: is_assistant_message retorna True para mensaje del asistente"""
        assert sample_assistant_message.is_assistant_message() is True

    def test_is_assistant_message_false(self, sample_user_message):
        """Test: is_assistant_message retorna False para mensaje de usuario"""
        assert sample_user_message.is_assistant_message() is False

    def test_is_system_message_true(self):
        """Test: is_system_message retorna True para mensaje del sistema"""
        msg = ChatMessage(
            role='system',
            content="System message",
            created_at=datetime.now()
        )
        assert msg.is_system_message() is True

    def test_is_system_message_false(self, sample_user_message):
        """Test: is_system_message retorna False para mensaje de usuario"""
        assert sample_user_message.is_system_message() is False

    def test_invalid_role_raises_error(self):
        """Test: Rol inválido lanza ValueError"""
        with pytest.raises(ValueError, match="Rol inválido"):
            ChatMessage(
                role='invalid_role',
                content="Test",
                created_at=datetime.now()
            )

    def test_empty_content_raises_error(self):
        """Test: Contenido vacío lanza ValueError"""
        with pytest.raises(ValueError, match="contenido del mensaje no puede estar vacío"):
            ChatMessage(
                role='user',
                content="",
                created_at=datetime.now()
            )

    def test_whitespace_content_raises_error(self):
        """Test: Contenido solo con espacios lanza ValueError"""
        with pytest.raises(ValueError, match="contenido del mensaje no puede estar vacío"):
            ChatMessage(
                role='user',
                content="   \n\t  ",
                created_at=datetime.now()
            )

    @pytest.mark.parametrize("role", ['user', 'assistant', 'system'])
    def test_valid_roles(self, role):
        """Test parametrizado: Todos los roles válidos funcionan"""
        msg = ChatMessage(
            role=role,
            content="Test content",
            created_at=datetime.now()
        )
        assert msg.role == role

    @pytest.mark.parametrize("role", ['admin', 'bot', 'moderator', '', None])
    def test_invalid_roles(self, role):
        """Test parametrizado: Roles inválidos lanzan error"""
        with pytest.raises(ValueError):
            ChatMessage(
                role=role,
                content="Test content",
                created_at=datetime.now()
            )

    def test_get_metadata_value_exists(self, sample_assistant_message):
        """Test: Obtener valor de metadata existente"""
        sources = sample_assistant_message.get_metadata_value('sources')
        assert sources == ["Licencia_Funcionamiento.pdf"]

    def test_get_metadata_value_not_exists(self, sample_assistant_message):
        """Test: Obtener valor de metadata inexistente retorna default"""
        value = sample_assistant_message.get_metadata_value('nonexistent', default="N/A")
        assert value == "N/A"

    def test_get_metadata_value_no_metadata(self, sample_user_message):
        """Test: Obtener valor cuando no hay metadata retorna default"""
        value = sample_user_message.get_metadata_value('key', default=None)
        assert value is None

    def test_to_dict(self, sample_user_message):
        """Test: Conversión a diccionario"""
        msg_dict = sample_user_message.to_dict()

        assert msg_dict['role'] == 'user'
        assert msg_dict['content'] == sample_user_message.content
        assert 'created_at' in msg_dict
        assert msg_dict['metadata'] == {}

    def test_to_dict_with_metadata(self, sample_assistant_message):
        """Test: Conversión a diccionario con metadata"""
        msg_dict = sample_assistant_message.to_dict()

        assert msg_dict['role'] == 'assistant'
        assert msg_dict['metadata']['sources'] == ["Licencia_Funcionamiento.pdf"]

    def test_message_with_custom_metadata(self):
        """Test: Mensaje con metadata personalizado"""
        metadata = {
            "sources": ["doc1.pdf", "doc2.pdf"],
            "similarity_scores": [0.9, 0.85],
            "chunks_used": 3
        }
        msg = ChatMessage(
            role='assistant',
            content="Answer based on multiple sources",
            created_at=datetime.now(),
            metadata=metadata
        )

        assert msg.get_metadata_value('sources') == ["doc1.pdf", "doc2.pdf"]
        assert msg.get_metadata_value('chunks_used') == 3
        assert msg.get_metadata_value('similarity_scores') == [0.9, 0.85]
