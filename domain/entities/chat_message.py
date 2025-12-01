"""
Entidad ChatMessage - Mensaje individual en una conversación
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, Dict, Any


@dataclass
class ChatMessage:
    """
    Representa un mensaje individual en una conversación.

    Attributes:
        role: Rol del mensaje ('user', 'assistant', 'system')
        content: Contenido del mensaje
        created_at: Timestamp de creación
        metadata: Información adicional (chunks usados, scores, etc)
    """
    role: Literal['user', 'assistant', 'system']
    content: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validación post-inicialización"""
        if not self.content or not self.content.strip():
            raise ValueError("El contenido del mensaje no puede estar vacío")

        if self.role not in ('user', 'assistant', 'system'):
            raise ValueError(f"Rol inválido: {self.role}. Debe ser 'user', 'assistant' o 'system'")

    def is_user_message(self) -> bool:
        """Verifica si el mensaje es del usuario"""
        return self.role == 'user'

    def is_assistant_message(self) -> bool:
        """Verifica si el mensaje es del asistente"""
        return self.role == 'assistant'

    def is_system_message(self) -> bool:
        """Verifica si el mensaje es del sistema"""
        return self.role == 'system'

    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del metadata

        Args:
            key: Clave a buscar
            default: Valor por defecto si no existe

        Returns:
            Valor del metadata o default
        """
        if not self.metadata:
            return default
        return self.metadata.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el mensaje a diccionario"""
        return {
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'metadata': self.metadata or {}
        }
