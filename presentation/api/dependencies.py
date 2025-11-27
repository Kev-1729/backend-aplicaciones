"""
Dependency Injection para FastAPI

Este módulo define las factory functions para inyectar dependencias
en los endpoints de la API.
"""
from functools import lru_cache
from fastapi import Depends
from supabase import create_client, Client
from typing import Annotated

from application.use_cases.query_rag import QueryRAGUseCase
from application.use_cases.get_statistics import GetStatisticsUseCase
from infrastructure.ai.gemini_embedding_service import GeminiEmbeddingService
from infrastructure.ai.gemini_chat_service import GeminiChatService
from infrastructure.database.supabase_vector_store import SupabaseVectorStore
from infrastructure.config.settings import get_settings


# ========== Infrastructure Dependencies ==========

@lru_cache()
def get_embedding_service() -> GeminiEmbeddingService:
    """
    Singleton: Servicio de embeddings con Gemini

    Returns:
        GeminiEmbeddingService: Instancia única del servicio
    """
    return GeminiEmbeddingService()


@lru_cache()
def get_chat_service() -> GeminiChatService:
    """
    Singleton: Servicio de chat con Gemini

    Returns:
        GeminiChatService: Instancia única del servicio
    """
    return GeminiChatService()


@lru_cache()
def get_supabase_client() -> Client:
    """
    Singleton: Cliente de Supabase

    Returns:
        Client: Instancia única del cliente Supabase
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@lru_cache()
def get_vector_store(
    supabase_client: Annotated[Client, Depends(get_supabase_client)]
) -> SupabaseVectorStore:
    """
    Singleton: Vector store con Supabase

    Args:
        supabase_client: Cliente de Supabase (inyectado)

    Returns:
        SupabaseVectorStore: Instancia única del vector store
    """
    return SupabaseVectorStore(supabase_client)


# ========== Use Case Dependencies ==========

def get_query_rag_use_case(
    embedding_service: Annotated[GeminiEmbeddingService, Depends(get_embedding_service)],
    vector_store: Annotated[SupabaseVectorStore, Depends(get_vector_store)],
    chat_service: Annotated[GeminiChatService, Depends(get_chat_service)]
) -> QueryRAGUseCase:
    """
    Factory: Caso de uso QueryRAG con dependencias inyectadas

    Args:
        embedding_service: Servicio de embeddings (inyectado)
        vector_store: Vector store (inyectado)
        chat_service: Servicio de chat (inyectado)

    Returns:
        QueryRAGUseCase: Instancia del caso de uso con dependencias
    """
    settings = get_settings()
    return QueryRAGUseCase(
        embedding_service=embedding_service,
        vector_store=vector_store,
        chat_service=chat_service,
        similarity_threshold=settings.RAG_SIMILARITY_THRESHOLD,
        top_k=settings.RAG_TOP_K_RESULTS
    )


def get_statistics_use_case(
    vector_store: Annotated[SupabaseVectorStore, Depends(get_vector_store)]
) -> GetStatisticsUseCase:
    """
    Factory: Caso de uso GetStatistics con dependencias inyectadas

    Args:
        vector_store: Vector store (inyectado)

    Returns:
        GetStatisticsUseCase: Instancia del caso de uso
    """
    return GetStatisticsUseCase(vector_store=vector_store)
