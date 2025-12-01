"""
Session Management API Routes
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List

from presentation.api.schemas import (
    CreateSessionRequest,
    ChatSessionResponse,
    ChatMessageResponse,
    SessionListResponse,
    DeleteSessionResponse
)
from presentation.api.dependencies import get_session_store
from infrastructure.database.supabase_chat_session_store import SupabaseChatSessionStore
from core.exceptions import VectorStoreError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post(
    "/",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session"
)
async def create_session(
    request: CreateSessionRequest,
    session_store: Annotated[SupabaseChatSessionStore, Depends(get_session_store)]
):
    """
    Create a new chat session for conversation memory.

    - **session_id**: Unique identifier for the session
    - **user_id**: Optional user identifier
    - **metadata**: Optional additional information
    """
    try:
        logger.info(f"Creating new session: {request.session_id}")

        # Verificar si ya existe
        exists = await session_store.session_exists(request.session_id)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Session {request.session_id} already exists"
            )

        session = await session_store.create_session(
            session_id=request.session_id,
            user_id=request.user_id,
            metadata=request.metadata
        )

        return ChatSessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            message_count=0,
            messages=[]
        )

    except VectorStoreError as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{session_id}",
    response_model=ChatSessionResponse,
    summary="Get a chat session with its history"
)
async def get_session(
    session_id: str,
    session_store: Annotated[SupabaseChatSessionStore, Depends(get_session_store)]
):
    """
    Retrieve a chat session with its complete message history.

    - **session_id**: The session identifier
    """
    try:
        logger.info(f"Fetching session: {session_id}")

        session = await session_store.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        return ChatSessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
            message_count=session.get_message_count(),
            messages=[
                ChatMessageResponse(
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                    metadata=msg.metadata
                )
                for msg in session.messages
            ]
        )

    except VectorStoreError as e:
        logger.error(f"Error fetching session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=SessionListResponse,
    summary="List all chat sessions"
)
async def list_sessions(
    user_id: str = None,
    limit: int = 50,
    session_store: Annotated[SupabaseChatSessionStore, Depends(get_session_store)] = None
):
    """
    List all chat sessions, optionally filtered by user_id.

    - **user_id**: Filter by user (optional)
    - **limit**: Maximum number of sessions to return (default: 50)
    """
    try:
        logger.info(f"Listing sessions (user_id={user_id}, limit={limit})")

        sessions = await session_store.get_all_sessions(
            user_id=user_id,
            limit=limit
        )

        return SessionListResponse(
            sessions=[
                ChatSessionResponse(
                    session_id=session.session_id,
                    user_id=session.user_id,
                    created_at=session.created_at.isoformat(),
                    updated_at=session.updated_at.isoformat(),
                    message_count=session.get_message_count(),
                    messages=[]  # No incluir mensajes en listado
                )
                for session in sessions
            ],
            total=len(sessions)
        )

    except VectorStoreError as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{session_id}",
    response_model=DeleteSessionResponse,
    summary="Delete a chat session"
)
async def delete_session(
    session_id: str,
    session_store: Annotated[SupabaseChatSessionStore, Depends(get_session_store)]
):
    """
    Delete a chat session and all its messages.

    - **session_id**: The session identifier
    """
    try:
        logger.info(f"Deleting session: {session_id}")

        deleted = await session_store.delete_session(session_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        return DeleteSessionResponse(
            success=True,
            message=f"Session {session_id} deleted successfully",
            session_id=session_id
        )

    except VectorStoreError as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{session_id}/history",
    response_model=DeleteSessionResponse,
    summary="Clear session history"
)
async def clear_session_history(
    session_id: str,
    session_store: Annotated[SupabaseChatSessionStore, Depends(get_session_store)]
):
    """
    Clear all messages from a session without deleting the session itself.

    - **session_id**: The session identifier
    """
    try:
        logger.info(f"Clearing history for session: {session_id}")

        cleared = await session_store.clear_session_history(session_id)

        if not cleared:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        return DeleteSessionResponse(
            success=True,
            message=f"History cleared for session {session_id}",
            session_id=session_id
        )

    except VectorStoreError as e:
        logger.error(f"Error clearing session history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
