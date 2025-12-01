"""
Implementación de IChatSessionStore usando Supabase
"""
import logging
from typing import Optional, List
from datetime import datetime
from supabase import Client

from domain.interfaces.chat_session_store import IChatSessionStore
from domain.entities.chat_session import ChatSession
from domain.entities.chat_message import ChatMessage
from core.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class SupabaseChatSessionStore(IChatSessionStore):
    """
    Implementación de IChatSessionStore usando Supabase PostgreSQL.

    Gestiona sesiones de chat y mensajes almacenados en las tablas
    'chat_sessions' y 'chat_messages'.
    """

    def __init__(self, client: Client):
        """
        Args:
            client: Cliente de Supabase configurado
        """
        self.client = client

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> ChatSession:
        """Crea una nueva sesión de chat"""
        try:
            logger.info(f"Creating new chat session: {session_id}")

            data = {
                "session_id": session_id,
                "user_id": user_id,
                "metadata": metadata or {}
            }

            response = self.client.table("chat_sessions").insert(data).execute()

            if not response.data:
                raise VectorStoreError(f"No se pudo crear la sesión {session_id}")

            session_data = response.data[0]
            return ChatSession(
                session_id=session_data["session_id"],
                user_id=session_data.get("user_id"),
                created_at=datetime.fromisoformat(session_data["created_at"]),
                updated_at=datetime.fromisoformat(session_data["updated_at"]),
                metadata=session_data.get("metadata"),
                messages=[]
            )

        except Exception as e:
            logger.error(f"Error creating session {session_id}: {str(e)}")
            raise VectorStoreError(f"Error al crear sesión: {str(e)}")

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Obtiene una sesión con su historial completo"""
        try:
            logger.info(f"Fetching session: {session_id}")

            # Obtener sesión
            session_response = self.client.table("chat_sessions")\
                .select("*")\
                .eq("session_id", session_id)\
                .execute()

            if not session_response.data:
                logger.info(f"Session {session_id} not found")
                return None

            session_data = session_response.data[0]

            # Obtener mensajes
            messages = await self.get_messages(session_id, limit=100)

            return ChatSession(
                session_id=session_data["session_id"],
                user_id=session_data.get("user_id"),
                created_at=datetime.fromisoformat(session_data["created_at"]),
                updated_at=datetime.fromisoformat(session_data["updated_at"]),
                metadata=session_data.get("metadata"),
                messages=messages
            )

        except Exception as e:
            logger.error(f"Error fetching session {session_id}: {str(e)}")
            raise VectorStoreError(f"Error al obtener sesión: {str(e)}")

    async def session_exists(self, session_id: str) -> bool:
        """Verifica si una sesión existe"""
        try:
            response = self.client.table("chat_sessions")\
                .select("session_id")\
                .eq("session_id", session_id)\
                .execute()

            return len(response.data) > 0

        except Exception as e:
            logger.error(f"Error checking session existence {session_id}: {str(e)}")
            raise VectorStoreError(f"Error al verificar sesión: {str(e)}")

    async def add_message(
        self,
        session_id: str,
        message: ChatMessage
    ) -> None:
        """Agrega un mensaje a una sesión existente"""
        try:
            logger.info(f"Adding message to session {session_id} (role: {message.role})")

            data = {
                "session_id": session_id,
                "role": message.role,
                "content": message.content,
                "metadata": message.metadata or {}
            }

            response = self.client.table("chat_messages").insert(data).execute()

            if not response.data:
                raise VectorStoreError(f"No se pudo agregar mensaje a sesión {session_id}")

            logger.info(f"Message added successfully to session {session_id}")

        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {str(e)}")
            raise VectorStoreError(f"Error al agregar mensaje: {str(e)}")

    async def get_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ChatMessage]:
        """Obtiene los mensajes de una sesión (más recientes primero)"""
        try:
            logger.info(f"Fetching messages for session {session_id} (limit: {limit})")

            response = self.client.table("chat_messages")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()

            messages = []
            for msg_data in response.data:
                messages.append(ChatMessage(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    created_at=datetime.fromisoformat(msg_data["created_at"]),
                    metadata=msg_data.get("metadata")
                ))

            logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
            return messages

        except Exception as e:
            logger.error(f"Error fetching messages for session {session_id}: {str(e)}")
            raise VectorStoreError(f"Error al obtener mensajes: {str(e)}")

    async def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión y todos sus mensajes (CASCADE)"""
        try:
            logger.info(f"Deleting session: {session_id}")

            response = self.client.table("chat_sessions")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()

            deleted = len(response.data) > 0
            if deleted:
                logger.info(f"Session {session_id} deleted successfully")
            else:
                logger.info(f"Session {session_id} not found for deletion")

            return deleted

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            raise VectorStoreError(f"Error al eliminar sesión: {str(e)}")

    async def clear_session_history(self, session_id: str) -> bool:
        """Limpia el historial de mensajes sin eliminar la sesión"""
        try:
            logger.info(f"Clearing history for session: {session_id}")

            # Verificar que la sesión existe
            exists = await self.session_exists(session_id)
            if not exists:
                return False

            # Eliminar todos los mensajes
            self.client.table("chat_messages")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()

            logger.info(f"History cleared for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error clearing history for session {session_id}: {str(e)}")
            raise VectorStoreError(f"Error al limpiar historial: {str(e)}")

    async def get_all_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ChatSession]:
        """Obtiene todas las sesiones (opcionalmente filtradas por usuario)"""
        try:
            logger.info(f"Fetching all sessions (user_id: {user_id}, limit: {limit})")

            query = self.client.table("chat_sessions").select("*")

            if user_id:
                query = query.eq("user_id", user_id)

            response = query.order("updated_at", desc=True).limit(limit).execute()

            sessions = []
            for session_data in response.data:
                # No cargamos mensajes aquí para optimizar performance
                sessions.append(ChatSession(
                    session_id=session_data["session_id"],
                    user_id=session_data.get("user_id"),
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    updated_at=datetime.fromisoformat(session_data["updated_at"]),
                    metadata=session_data.get("metadata"),
                    messages=[]  # Sin mensajes para listar
                ))

            logger.info(f"Retrieved {len(sessions)} sessions")
            return sessions

        except Exception as e:
            logger.error(f"Error fetching all sessions: {str(e)}")
            raise VectorStoreError(f"Error al obtener sesiones: {str(e)}")
