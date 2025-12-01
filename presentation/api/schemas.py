"""
Pydantic schemas for HTTP API (Request/Response models)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# Query Schemas
class QueryRequest(BaseModel):
    """Request schema for RAG queries with session support"""
    query: str = Field(..., min_length=1, description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation memory")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "¿Cómo saco una licencia de funcionamiento para una bodega?",
                    "session_id": "session_abc123"
                }
            ]
        }
    }


class QueryResponse(BaseModel):
    """Response schema for RAG queries"""
    answer: str = Field(..., description="Generated answer (HTML formatted)")
    sources: List[str] = Field(default_factory=list, description="Source documents")
    document_name: Optional[str] = Field(None, description="Primary document name")
    download_url: Optional[str] = Field(None, description="Document download URL")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "<h3>Licencia de Funcionamiento para Bodega</h3><p>Para obtener...</p>",
                    "sources": ["Procedimiento de Licencia de Funcionamiento.pdf"],
                    "document_name": "Procedimiento de Licencia de Funcionamiento.pdf",
                    "download_url": None
                }
            ]
        }
    }


# Statistics Schemas
class StatisticsResponse(BaseModel):
    """Response schema for system statistics"""
    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    total_pages: int = Field(..., description="Total number of pages")
    categories: Dict[str, int] = Field(..., description="Documents grouped by category")
    document_types: Dict[str, int] = Field(..., description="Documents grouped by type")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_documents": 15,
                    "total_chunks": 127,
                    "total_pages": 85,
                    "categories": {"comercio": 10, "normativa": 5},
                    "document_types": {"formulario": 8, "ley": 3, "ordenanza": 4}
                }
            ]
        }
    }


# Health Check Schema
class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    app_name: str = Field(..., description="Application name")


# Chat Session Schemas
class CreateSessionRequest(BaseModel):
    """Request schema for creating a new chat session"""
    session_id: str = Field(..., min_length=1, description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User ID (optional)")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "user_abc_20250130_001",
                    "user_id": "user_abc",
                    "metadata": {"user_agent": "Mozilla/5.0"}
                }
            ]
        }
    }


class ChatMessageResponse(BaseModel):
    """Response schema for a single chat message"""
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")
    created_at: str = Field(..., description="Timestamp of message creation")
    metadata: Optional[Dict] = Field(None, description="Additional message metadata")


class ChatSessionResponse(BaseModel):
    """Response schema for a chat session"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(None, description="User ID")
    created_at: str = Field(..., description="Session creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages in session")
    messages: List[ChatMessageResponse] = Field(default_factory=list, description="Session messages")


class SessionListResponse(BaseModel):
    """Response schema for list of sessions"""
    sessions: List[ChatSessionResponse] = Field(..., description="List of chat sessions")
    total: int = Field(..., description="Total number of sessions")


class DeleteSessionResponse(BaseModel):
    """Response schema for session deletion"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")
    session_id: str = Field(..., description="Deleted session ID")


# Feedback Schemas
class SubmitFeedbackRequest(BaseModel):
    """Request schema for submitting feedback"""
    message_id: str = Field(..., description="ID of the message being evaluated")
    session_id: Optional[str] = Field(None, description="Session ID")
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="RAG answer")
    is_correct: Optional[bool] = Field(None, description="Is the answer correct? (true/false/null)")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Optional 1-5 star rating")
    comment: Optional[str] = Field(None, description="Optional user comment")
    sources: Optional[List[str]] = Field(None, description="Sources used")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message_id": "msg_12345",
                    "session_id": "session_abc",
                    "query": "¿Qué necesito para una licencia?",
                    "answer": "Necesitas...",
                    "is_correct": True,
                    "rating": 5,
                    "sources": ["documento1.pdf"]
                }
            ]
        }
    }


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission"""
    success: bool = Field(..., description="Whether feedback was saved")
    message: str = Field(..., description="Status message")
    message_id: str = Field(..., description="Message ID")


class ExactitudMetricsResponse(BaseModel):
    """Response schema for exactitud metrics"""
    total_evaluaciones: int = Field(..., description="Total evaluations")
    respuestas_correctas: int = Field(..., description="Correct responses")
    respuestas_incorrectas: int = Field(..., description="Incorrect responses")
    sin_evaluar: int = Field(..., description="Unevaluated responses")
    exactitud_porcentaje: float = Field(..., description="Exactitud percentage (0-100)")
    rating_promedio: Optional[float] = Field(None, description="Average star rating")
    exactitud_label: str = Field(..., description="Exactitud label (Excelente/Buena/Regular/Necesita mejora)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_evaluaciones": 100,
                    "respuestas_correctas": 85,
                    "respuestas_incorrectas": 15,
                    "sin_evaluar": 20,
                    "exactitud_porcentaje": 85.0,
                    "rating_promedio": 4.2,
                    "exactitud_label": "Buena"
                }
            ]
        }
    }
