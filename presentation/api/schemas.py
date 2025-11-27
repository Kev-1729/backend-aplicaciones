"""
Pydantic schemas for HTTP API (Request/Response models)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# Query Schemas
class QueryRequest(BaseModel):
    """Request schema for RAG queries"""
    query: str = Field(..., min_length=1, description="User's question")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "¿Cómo saco una licencia de funcionamiento para una bodega?"
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
