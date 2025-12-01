"""
Entidad ChatSession - Sesión de conversación
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from .chat_message import ChatMessage


@dataclass
class ChatSession:
    """
    Representa una sesión de conversación con historial de mensajes.

    Attributes:
        session_id: Identificador único de la sesión
        messages: Lista de mensajes en la conversación
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
        user_id: ID del usuario (opcional)
        metadata: Información adicional de la sesión
    """
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validación post-inicialización"""
        if not self.session_id or not self.session_id.strip():
            raise ValueError("session_id no puede estar vacío")

    def add_message(self, message: ChatMessage) -> None:
        """
        Agrega un mensaje a la sesión

        Args:
            message: Mensaje a agregar
        """
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_message_count(self) -> int:
        """Retorna el número total de mensajes"""
        return len(self.messages)

    def get_user_messages(self) -> List[ChatMessage]:
        """Retorna solo los mensajes del usuario"""
        return [msg for msg in self.messages if msg.is_user_message()]

    def get_assistant_messages(self) -> List[ChatMessage]:
        """Retorna solo los mensajes del asistente"""
        return [msg for msg in self.messages if msg.is_assistant_message()]

    def get_recent_messages(self, limit: int = 10) -> List[ChatMessage]:
        """
        Retorna los N mensajes más recientes

        Args:
            limit: Número de mensajes a retornar

        Returns:
            Lista de mensajes más recientes
        """
        return self.messages[-limit:] if limit > 0 else self.messages

    def get_conversation_context(self, max_messages: int = 10) -> str:
        """
        Genera un string con el contexto de la conversación
        para enviarlo al LLM

        Args:
            max_messages: Número máximo de mensajes a incluir

        Returns:
            String formateado con el historial
        """
        recent_messages = self.get_recent_messages(max_messages)

        if not recent_messages:
            return ""

        context_parts = []
        for msg in recent_messages:
            role_label = {
                'user': 'Usuario',
                'assistant': 'Asistente',
                'system': 'Sistema'
            }.get(msg.role, msg.role)

            context_parts.append(f"{role_label}: {msg.content}")

        return "\n\n".join(context_parts)

    def clear_history(self) -> None:
        """Limpia el historial de mensajes"""
        self.messages.clear()
        self.updated_at = datetime.now()

    def has_messages(self) -> bool:
        """Verifica si la sesión tiene mensajes"""
        return len(self.messages) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la sesión a diccionario"""
        return {
            'session_id': self.session_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            'user_id': self.user_id,
            'metadata': self.metadata or {},
            'message_count': self.get_message_count()
        }
