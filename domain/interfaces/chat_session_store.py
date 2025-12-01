"""
Interfaz para el repositorio de sesiones de chat
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.chat_session import ChatSession
from domain.entities.chat_message import ChatMessage


class IChatSessionStore(ABC):
    """
    Contrato abstracto para almacenar y recuperar sesiones de chat.

    Esta interfaz define las operaciones necesarias para gestionar
    sesiones de conversación y su historial de mensajes.
    """

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> ChatSession:
        """
        Crea una nueva sesión de chat

        Args:
            session_id: Identificador único de la sesión
            user_id: ID del usuario (opcional)
            metadata: Metadata adicional (opcional)

        Returns:
            ChatSession creada

        Raises:
            VectorStoreError: Si hay error al crear la sesión
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Obtiene una sesión existente con su historial completo

        Args:
            session_id: ID de la sesión

        Returns:
            ChatSession si existe, None si no existe

        Raises:
            VectorStoreError: Si hay error al obtener la sesión
        """
        pass

    @abstractmethod
    async def session_exists(self, session_id: str) -> bool:
        """
        Verifica si una sesión existe

        Args:
            session_id: ID de la sesión

        Returns:
            True si existe, False si no

        Raises:
            VectorStoreError: Si hay error al verificar
        """
        pass

    @abstractmethod
    async def add_message(
        self,
        session_id: str,
        message: ChatMessage
    ) -> None:
        """
        Agrega un mensaje a una sesión existente

        Args:
            session_id: ID de la sesión
            message: Mensaje a agregar

        Raises:
            VectorStoreError: Si hay error al agregar el mensaje
        """
        pass

    @abstractmethod
    async def get_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ChatMessage]:
        """
        Obtiene los mensajes de una sesión

        Args:
            session_id: ID de la sesión
            limit: Número máximo de mensajes a retornar (más recientes)

        Returns:
            Lista de mensajes ordenados cronológicamente

        Raises:
            VectorStoreError: Si hay error al obtener mensajes
        """
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """
        Elimina una sesión y todos sus mensajes

        Args:
            session_id: ID de la sesión

        Returns:
            True si se eliminó, False si no existía

        Raises:
            VectorStoreError: Si hay error al eliminar
        """
        pass

    @abstractmethod
    async def clear_session_history(self, session_id: str) -> bool:
        """
        Limpia el historial de mensajes de una sesión sin eliminar la sesión

        Args:
            session_id: ID de la sesión

        Returns:
            True si se limpió, False si no existía

        Raises:
            VectorStoreError: Si hay error al limpiar
        """
        pass

    @abstractmethod
    async def get_all_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ChatSession]:
        """
        Obtiene todas las sesiones (opcionalmente filtradas por usuario)

        Args:
            user_id: Filtrar por ID de usuario (opcional)
            limit: Número máximo de sesiones a retornar

        Returns:
            Lista de sesiones (más recientes primero)

        Raises:
            VectorStoreError: Si hay error al obtener sesiones
        """
        pass
