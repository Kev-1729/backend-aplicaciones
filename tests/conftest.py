"""
Pytest configuration and shared fixtures
"""
import pytest
from datetime import datetime
from typing import List
from unittest.mock import AsyncMock, Mock

# Import domain entities
from domain.entities.document import Document
from domain.entities.chunk import DocumentChunk
from domain.entities.chat_message import ChatMessage
from domain.entities.chat_session import ChatSession

# Import DTOs
from application.dtos.query_dto import QueryInput, QueryOutput


# ============================================================================
# FIXTURES: Domain Entities
# ============================================================================

@pytest.fixture
def sample_document() -> Document:
    """Fixture: Documento de prueba"""
    return Document(
        id="doc-123",
        filename="Licencia_Funcionamiento.pdf",
        document_type="guia",
        category="comercio",
        total_pages=10,
        file_hash="abc123hash",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        processing_status="completed",
        total_chunks=5
    )


@pytest.fixture
def sample_legal_document() -> Document:
    """Fixture: Documento legal de prueba"""
    return Document(
        id="doc-456",
        filename="Ordenanza_Municipal_001.pdf",
        document_type="ordenanza",
        category="normativa",
        total_pages=25,
        file_hash="def456hash",
        created_at=datetime(2024, 2, 20, 14, 0, 0),
        processing_status="completed",
        total_chunks=15
    )


@pytest.fixture
def sample_small_document() -> Document:
    """Fixture: Documento pequeño de prueba"""
    return Document(
        id="doc-789",
        filename="Formulario_Solicitud.pdf",
        document_type="formulario",
        category="general",
        total_pages=3,
        file_hash="ghi789hash",
        created_at=datetime(2024, 3, 10, 9, 0, 0),
        processing_status="completed",
        total_chunks=1
    )


@pytest.fixture
def sample_embedding() -> List[float]:
    """Fixture: Embedding de 768 dimensiones (simulado)"""
    return [0.1] * 768


@pytest.fixture
def sample_chunk(sample_embedding: List[float]) -> DocumentChunk:
    """Fixture: Chunk de documento de prueba"""
    return DocumentChunk(
        id="chunk-001",
        document_id="doc-123",
        text="Requisitos para licencia de funcionamiento: DNI, RUC, croquis del local.",
        page_number=1,
        chunk_index=0,
        embedding=sample_embedding,
        metadata={"document_type": "guia", "category": "comercio"}
    )


@pytest.fixture
def sample_user_message() -> ChatMessage:
    """Fixture: Mensaje de usuario de prueba"""
    return ChatMessage(
        role='user',
        content="¿Cómo saco una licencia de funcionamiento?",
        created_at=datetime(2024, 12, 9, 10, 0, 0)
    )


@pytest.fixture
def sample_assistant_message() -> ChatMessage:
    """Fixture: Mensaje del asistente de prueba"""
    return ChatMessage(
        role='assistant',
        content="Para obtener una licencia de funcionamiento necesitas...",
        created_at=datetime(2024, 12, 9, 10, 0, 5),
        metadata={"sources": ["Licencia_Funcionamiento.pdf"]}
    )


@pytest.fixture
def sample_chat_session(
    sample_user_message: ChatMessage,
    sample_assistant_message: ChatMessage
) -> ChatSession:
    """Fixture: Sesión de chat de prueba con mensajes"""
    session = ChatSession(
        session_id="session-abc-123",
        user_id="user-456",
        created_at=datetime(2024, 12, 9, 10, 0, 0),
        updated_at=datetime(2024, 12, 9, 10, 0, 5),
        metadata={"platform": "web"}
    )
    session.add_message(sample_user_message)
    session.add_message(sample_assistant_message)
    return session


@pytest.fixture
def empty_chat_session() -> ChatSession:
    """Fixture: Sesión de chat vacía"""
    return ChatSession(
        session_id="session-empty-001",
        user_id="user-789",
        created_at=datetime(2024, 12, 9, 11, 0, 0)
    )


# ============================================================================
# FIXTURES: DTOs
# ============================================================================

@pytest.fixture
def sample_query_input() -> QueryInput:
    """Fixture: QueryInput de prueba"""
    return QueryInput(
        query="¿Cuánto cuesta una licencia de funcionamiento?",
        session_id="session-abc-123"
    )


@pytest.fixture
def sample_query_input_no_session() -> QueryInput:
    """Fixture: QueryInput sin session_id"""
    return QueryInput(
        query="¿Qué es una licencia provisional?",
        session_id=None
    )


@pytest.fixture
def sample_query_output() -> QueryOutput:
    """Fixture: QueryOutput de prueba"""
    return QueryOutput(
        answer="<h3>Costos de Licencia de Funcionamiento</h3><p>Los costos varían según el tipo...</p>",
        sources=["Licencia_Funcionamiento.pdf", "Tarifario_Municipal.pdf"],
        document_name="Licencia_Funcionamiento.pdf",
        download_url=None
    )


# ============================================================================
# FIXTURES: Mocks for Interfaces
# ============================================================================

@pytest.fixture
def mock_embedding_service():
    """Mock del servicio de embeddings"""
    mock = AsyncMock()
    mock.generate_query_embedding.return_value = [0.1] * 768
    mock.generate_embeddings.return_value = [[0.1] * 768, [0.2] * 768]
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock del vector store"""
    mock = AsyncMock()
    mock.search_similar_chunks.return_value = [
        {
            'chunk_id': 'chunk-001',
            'chunk_text': 'Requisitos: DNI, RUC, croquis del local.',
            'filename': 'Licencia_Funcionamiento.pdf',
            'page_number': 1,
            'similarity_score': 0.85
        },
        {
            'chunk_id': 'chunk-002',
            'chunk_text': 'El costo es de S/. 50.00 para bodegas.',
            'filename': 'Tarifario_Municipal.pdf',
            'page_number': 3,
            'similarity_score': 0.78
        }
    ]
    mock.get_statistics.return_value = {
        'total_documents': 10,
        'total_chunks': 150,
        'total_pages': 320,
        'categories': ['comercio', 'normativa', 'general']
    }
    return mock


@pytest.fixture
def mock_chat_service():
    """Mock del servicio de chat (LLM)"""
    mock = AsyncMock()
    mock.generate_answer.return_value = "<h3>Licencia de Funcionamiento</h3><p>Para obtener una licencia necesitas...</p>"
    return mock


@pytest.fixture
def mock_session_store():
    """Mock del almacén de sesiones"""
    mock = AsyncMock()
    mock.session_exists.return_value = True
    mock.create_session.return_value = None
    mock.get_messages.return_value = []
    mock.add_message.return_value = None
    return mock


# ============================================================================
# FIXTURES: Test Data Collections
# ============================================================================

@pytest.fixture
def sample_conversation_history() -> List[ChatMessage]:
    """Fixture: Historial de conversación de prueba"""
    return [
        ChatMessage(
            role='user',
            content="¿Qué es una licencia de funcionamiento?",
            created_at=datetime(2024, 12, 9, 10, 0, 0)
        ),
        ChatMessage(
            role='assistant',
            content="Una licencia de funcionamiento es...",
            created_at=datetime(2024, 12, 9, 10, 0, 5)
        ),
        ChatMessage(
            role='user',
            content="¿Cuánto cuesta?",
            created_at=datetime(2024, 12, 9, 10, 1, 0)
        ),
        ChatMessage(
            role='assistant',
            content="El costo varía según el tipo de establecimiento...",
            created_at=datetime(2024, 12, 9, 10, 1, 5)
        )
    ]


@pytest.fixture
def sample_similar_chunks() -> List[dict]:
    """Fixture: Lista de chunks similares (resultado de búsqueda vectorial)"""
    return [
        {
            'chunk_id': 'chunk-001',
            'chunk_text': 'Requisitos para licencia: DNI original y copia, RUC, croquis del local.',
            'filename': 'Licencia_Funcionamiento.pdf',
            'page_number': 1,
            'similarity_score': 0.92
        },
        {
            'chunk_id': 'chunk-002',
            'chunk_text': 'Costos: S/. 50.00 para bodegas, S/. 150.00 para restaurantes.',
            'filename': 'Tarifario_Municipal.pdf',
            'page_number': 3,
            'similarity_score': 0.85
        },
        {
            'chunk_id': 'chunk-003',
            'chunk_text': 'Plazo de atención: 1 día hábil para licencias automáticas.',
            'filename': 'Procedimientos_TUPA.pdf',
            'page_number': 5,
            'similarity_score': 0.78
        }
    ]
