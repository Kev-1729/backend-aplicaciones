# Arquitectura del Sistema RAG

## 📐 Diagrama de Arquitectura en Capas

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  (HTTP API - FastAPI)                                           │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  presentation/api/routes/rag_routes.py                   │  │
│  │  • POST /api/rag/query                                   │  │
│  │  • GET  /api/rag/stats                                   │  │
│  │  • GET  /health                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  presentation/api/dependencies.py                        │  │
│  │  • get_query_rag_use_case()                              │  │
│  │  • get_statistics_use_case()                             │  │
│  │  • Dependency Injection con FastAPI Depends()            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                              │
│  (Casos de Uso - Orquestación de la lógica de negocio)         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  application/use_cases/query_rag.py                      │  │
│  │  QueryRAGUseCase:                                        │  │
│  │    1. Detectar comandos especiales (ayuda, FAQ)          │  │
│  │    2. Generar embedding de query                         │  │
│  │    3. Buscar chunks similares                            │  │
│  │    4. Construir contexto                                 │  │
│  │    5. Generar respuesta con LLM                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  application/use_cases/get_statistics.py                 │  │
│  │  GetStatisticsUseCase:                                   │  │
│  │    • Obtener stats del vector store                      │  │
│  │    • Agregar métricas del sistema                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  application/dtos/                                       │  │
│  │  • QueryInput, QueryOutput                               │  │
│  │  • StatsOutput                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                                │
│  (Reglas de Negocio Puras - Sin dependencias externas)         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  domain/entities/                                        │  │
│  │  • Document (documento municipal)                        │  │
│  │  • DocumentChunk (fragmento con embedding)               │  │
│  │  • QueryResult (resultado de búsqueda RAG)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  domain/interfaces/  (Contratos abstractos)              │  │
│  │  • IEmbeddingService                                     │  │
│  │  • IVectorStore                                          │  │
│  │  • IChatService                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↑
                    (implementan las interfaces)
                             ↑
┌─────────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                            │
│  (Implementaciones Concretas - Detalles Técnicos)              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  infrastructure/ai/                                      │  │
│  │  • GeminiEmbeddingService  ← implementa IEmbeddingService│  │
│  │  • GeminiChatService       ← implementa IChatService     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  infrastructure/database/                                │  │
│  │  • SupabaseVectorStore     ← implementa IVectorStore     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  infrastructure/config/                                  │  │
│  │  • Settings (Pydantic BaseSettings)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SERVICIOS EXTERNOS                             │
│                                                                  │
│  • Google Gemini API (embeddings + chat)                       │
│  • Supabase (PostgreSQL + pgvector)                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de una Consulta RAG

```
1. Usuario → Frontend
        ↓
2. HTTP Request → POST /api/rag/query
        ↓
3. presentation/api/routes/rag_routes.py
   • Recibe QueryRequest (Pydantic validation)
   • Obtiene QueryRAGUseCase via Depends()
        ↓
4. application/use_cases/query_rag.py
   QueryRAGUseCase.execute():
        ↓
   4a. _handle_special_commands()
       ¿Es "ayuda", "FAQ", "temas"?
       → SÍ: Retorna mensaje predefinido
       → NO: Continúa al paso 4b
        ↓
   4b. embedding_service.generate_query_embedding(query)
       ↓ llama a ↓
       infrastructure/ai/gemini_embedding_service.py
       → Gemini API → Vector[768]
        ↓
   4c. vector_store.search_similar_chunks(embedding)
       ↓ llama a ↓
       infrastructure/database/supabase_vector_store.py
       → Supabase RPC: search_similar_chunks()
       → Retorna top K chunks similares
        ↓
   4d. _build_context(chunks)
       → Concatena textos de chunks con fuentes
        ↓
   4e. chat_service.generate_answer(query, context)
       ↓ llama a ↓
       infrastructure/ai/gemini_chat_service.py
       → Gemini API (gemini-2.0-flash-exp)
       → Respuesta en HTML
        ↓
5. QueryOutput (DTO)
   → Se convierte a QueryResponse (Pydantic schema)
        ↓
6. HTTP Response → JSON
        ↓
7. Frontend → Muestra respuesta al usuario
```

---

## 🧩 Componentes Principales

### 1. Domain Layer (Dominio)

**Responsabilidad:** Definir las reglas de negocio puras

**Archivos:**
- `domain/entities/document.py`
  - Lógica de negocio:
    - `is_legal_document()`: ¿Es ley/ordenanza/decreto?
    - `should_chunk_by_articles()`: ¿Debe chunkearse por artículos?
    - `should_keep_as_single_chunk()`: ¿Documento pequeño?

- `domain/entities/chunk.py`
  - Validación:
    - `validate_embedding_dimension()`: Verifica 768 dims
    - `has_valid_text()`: Verifica que no esté vacío

- `domain/interfaces/`
  - Contratos abstractos (ABC) que deben implementar las capas externas

**No depende de:** Ninguna otra capa (PURO)

---

### 2. Application Layer (Aplicación)

**Responsabilidad:** Orquestar casos de uso del negocio

**Archivos:**
- `application/use_cases/query_rag.py`
  - Flujo completo de consulta RAG
  - Manejo de comandos especiales (ayuda, FAQ)
  - Orquestación de embedding → búsqueda → LLM

- `application/use_cases/get_statistics.py`
  - Consulta de métricas del sistema

- `application/dtos/`
  - Data Transfer Objects (desacoplados de HTTP)

**Depende de:** `domain/` (interfaces + entities)
**No depende de:** `infrastructure/`, `presentation/`

---

### 3. Infrastructure Layer (Infraestructura)

**Responsabilidad:** Implementar detalles técnicos

**Archivos:**
- `infrastructure/ai/gemini_embedding_service.py`
  - Implementa `IEmbeddingService`
  - Usa Google Gemini API
  - **Fácilmente reemplazable** por OpenAI/Cohere

- `infrastructure/ai/gemini_chat_service.py`
  - Implementa `IChatService`
  - Genera respuestas con Gemini
  - **Fácilmente reemplazable** por GPT/Claude

- `infrastructure/database/supabase_vector_store.py`
  - Implementa `IVectorStore`
  - Usa Supabase + pgvector
  - **Fácilmente reemplazable** por Pinecone/Weaviate

**Depende de:** `domain/` (implementa interfaces)
**No depende de:** `application/`, `presentation/`

---

### 4. Presentation Layer (Presentación)

**Responsabilidad:** Exponer API HTTP

**Archivos:**
- `presentation/api/routes/rag_routes.py`
  - Define endpoints HTTP
  - Valida request/response con Pydantic
  - Delega lógica a casos de uso

- `presentation/api/dependencies.py`
  - **Dependency Injection** con FastAPI `Depends()`
  - Factory functions para casos de uso
  - Singletons para servicios

- `presentation/api/schemas.py`
  - Pydantic models para HTTP (request/response)

**Depende de:** `application/` (casos de uso), `infrastructure/` (implementaciones)

---

## 🎯 Principios SOLID Aplicados

### Single Responsibility Principle (SRP)
Cada clase tiene una sola razón para cambiar:
- `QueryRAGUseCase`: Solo orquesta la consulta RAG
- `GeminiEmbeddingService`: Solo genera embeddings con Gemini
- `SupabaseVectorStore`: Solo interactúa con Supabase

### Open/Closed Principle (OCP)
Abierto para extensión, cerrado para modificación:
- Puedes agregar `OpenAIEmbeddingService` sin modificar código existente
- Solo cambias la factory function en `dependencies.py`

### Liskov Substitution Principle (LSP)
Las implementaciones son intercambiables:
```python
# Gemini
embedding_service: IEmbeddingService = GeminiEmbeddingService()

# OpenAI (drop-in replacement)
embedding_service: IEmbeddingService = OpenAIEmbeddingService()
```

### Interface Segregation Principle (ISP)
Interfaces específicas y cohesivas:
- `IEmbeddingService`: Solo embeddings
- `IChatService`: Solo chat/LLM
- `IVectorStore`: Solo vector search

### Dependency Inversion Principle (DIP)
Las capas internas definen contratos, las externas implementan:
```python
# domain/interfaces/embedding_service.py (Interface)
class IEmbeddingService(ABC):
    @abstractmethod
    async def generate_query_embedding(self, query: str) -> List[float]:
        pass

# infrastructure/ai/gemini_embedding_service.py (Implementation)
class GeminiEmbeddingService(IEmbeddingService):
    async def generate_query_embedding(self, query: str) -> List[float]:
        # Implementación concreta con Gemini
        ...
```

---

## 🔄 Ventajas de esta Arquitectura

### 1. Testabilidad Total
```python
# Test unitario para QueryRAGUseCase
mock_embedding = Mock(spec=IEmbeddingService)
mock_vector_store = Mock(spec=IVectorStore)
mock_chat = Mock(spec=IChatService)

use_case = QueryRAGUseCase(
    embedding_service=mock_embedding,
    vector_store=mock_vector_store,
    chat_service=mock_chat
)

# Test sin tocar servicios externos
result = await use_case.execute(QueryInput(query="Test"))
```

### 2. Flexibilidad
Cambiar Gemini por OpenAI requiere:
1. Crear `OpenAIEmbeddingService` (implementa `IEmbeddingService`)
2. Cambiar 1 línea en `dependencies.py`:
   ```python
   def get_embedding_service() -> IEmbeddingService:
       return OpenAIEmbeddingService()  # ← Solo esto
   ```

### 3. Mantenibilidad
- Código organizado por responsabilidades
- Fácil ubicar bugs (capas aisladas)
- Cambios localizados (bajo acoplamiento)

### 4. Escalabilidad
- Agregar nuevos casos de uso sin tocar código existente
- Implementar nuevos adaptadores (bases de datos, LLMs)
- Horizontal scaling (stateless API)

---

## 📊 Métricas de Calidad del Código

| Métrica | Valor | Descripción |
|---------|-------|-------------|
| **Layers** | 4 | Domain, Application, Infrastructure, Presentation |
| **Interfaces** | 3 | IEmbeddingService, IVectorStore, IChatService |
| **Use Cases** | 2 | QueryRAG, GetStatistics |
| **Entities** | 3 | Document, Chunk, QueryResult |
| **Coupling** | Bajo | Capas internas no dependen de externas |
| **Cohesion** | Alta | Cada módulo tiene una responsabilidad clara |
| **Testability** | 100% | Todos los componentes son testeables |

---

## 🚀 Próximos Pasos

Para mejorar aún más la arquitectura:

1. **Agregar capa de caching** (Redis)
   - Crear `ICacheService` en `domain/interfaces/`
   - Implementar `RedisCacheService` en `infrastructure/cache/`

2. **Implementar event sourcing**
   - Crear `IEventBus` en `domain/interfaces/`
   - Emitir eventos en casos de uso

3. **Agregar observabilidad**
   - OpenTelemetry para tracing
   - Prometheus metrics

4. **Rate limiting por usuario**
   - Middleware en `presentation/middleware/`

---

## 📚 Referencias

- **Clean Architecture**: Robert C. Martin
- **Dependency Injection**: Martin Fowler
- **Domain-Driven Design**: Eric Evans
- **FastAPI Best Practices**: https://fastapi.tiangolo.com/
