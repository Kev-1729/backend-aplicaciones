# RAG Backend - Layered Architecture

Sistema RAG (Retrieval Augmented Generation) para procedimientos municipales de Carabayllo, implementado con **Layered Architecture** (arquitectura en capas).

## 🏗️ Arquitectura

```
backend/
├── domain/                  # ← CAPA DE DOMINIO (Reglas de negocio)
│   ├── entities/           # Modelos del dominio (Document, Chunk, QueryResult)
│   └── interfaces/         # Contratos abstractos (IEmbeddingService, IVectorStore, IChatService)
│
├── application/            # ← CAPA DE APLICACIÓN (Casos de uso)
│   ├── use_cases/         # Lógica de orquestación (QueryRAGUseCase, GetStatisticsUseCase)
│   └── dtos/              # Data Transfer Objects (QueryInput, QueryOutput, StatsOutput)
│
├── infrastructure/         # ← CAPA DE INFRAESTRUCTURA (Implementaciones)
│   ├── ai/                # Servicios de IA (GeminiEmbeddingService, GeminiChatService)
│   ├── database/          # Almacenamiento (SupabaseVectorStore)
│   └── config/            # Configuración (Settings)
│
├── presentation/           # ← CAPA DE PRESENTACIÓN (HTTP API)
│   ├── api/
│   │   ├── routes/        # Endpoints HTTP (rag_routes.py)
│   │   ├── schemas.py     # Pydantic schemas para request/response
│   │   ├── dependencies.py # Dependency injection
│   │   └── app.py         # FastAPI factory
│   └── middleware/        # Error handlers
│
├── core/                   # ← UTILIDADES COMPARTIDAS
│   ├── exceptions.py      # Excepciones personalizadas
│   └── logging_config.py  # Configuración de logging
│
└── main.py                # Entry point del servidor
```

### Flujo de Dependencias

```
Presentation → Application → Domain ← Infrastructure
                                 ↑
                                 └─── (Dependency Injection)
```

**Regla clave:** `domain/` **nunca depende** de `infrastructure/` ni `presentation/`

---

## 🚀 Inicio Rápido

### 🐳 Opción 1: Docker (Recomendado)

**Requisitos:**
- Docker Desktop instalado
- Docker Compose

**Pasos:**

```bash
# 1. Navegar al directorio backend
cd backend

# 2. Tu archivo .env ya está configurado con las credenciales correctas

# 3. Build y ejecutar con Docker
docker.bat build     # Windows
./docker.sh build    # Unix/macOS

docker.bat up        # Windows
./docker.sh up       # Unix/macOS
```

El servidor estará disponible en `http://localhost:8000`

**Comandos útiles:**

```bash
# Ver logs
docker.bat logs      # Windows
./docker.sh logs     # Unix/macOS

# Detener contenedores
docker.bat down      # Windows
./docker.sh down     # Unix/macOS

# Reiniciar
docker.bat restart   # Windows
./docker.sh restart  # Unix/macOS

# Verificar salud del servicio
docker.bat health    # Windows
./docker.sh health   # Unix/macOS

# Ver todos los comandos disponibles
docker.bat help      # Windows
./docker.sh help     # Unix/macOS
```

### 💻 Opción 2: Local (sin Docker)

**Requisitos:**
- Python 3.11+

**Pasos:**

```bash
# 1. Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Unix/macOS)
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Tu archivo .env ya está configurado

# 4. Ejecutar servidor
python main.py
```

El servidor estará disponible en `http://localhost:8000`

---

## 📡 API Endpoints

### `POST /api/rag/query`
Consultar el sistema RAG

**Request:**
```json
{
  "query": "¿Cómo saco una licencia de funcionamiento para una bodega?"
}
```

**Response:**
```json
{
  "answer": "<h3>Licencia de Funcionamiento para Bodega</h3><p>Para obtener...</p>",
  "sources": ["Procedimiento de Licencia de Funcionamiento.pdf"],
  "document_name": "Procedimiento de Licencia de Funcionamiento.pdf",
  "download_url": null
}
```

### `GET /api/rag/stats`
Obtener estadísticas del sistema

**Response:**
```json
{
  "total_documents": 15,
  "total_chunks": 127,
  "total_pages": 85,
  "categories": {
    "comercio": 10,
    "normativa": 5
  },
  "document_types": {
    "formulario": 8,
    "ley": 3,
    "ordenanza": 4
  }
}
```

### `GET /health`
Health check

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "app_name": "Asistente de Trámites Municipales"
}
```

### 📚 Documentación interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐳 Docker

### Estructura de archivos Docker

```
backend/
├── Dockerfile              # Imagen de producción (multi-stage build)
├── Dockerfile.dev          # Imagen de desarrollo (con hot-reload)
├── docker-compose.yml      # Configuración para producción
├── docker-compose.dev.yml  # Configuración para desarrollo
├── .dockerignore           # Archivos excluidos de la imagen
├── docker.sh               # Script de utilidades (Unix/macOS)
└── docker.bat              # Script de utilidades (Windows)
```

### Modos de ejecución

#### 🚀 Modo Producción

Imagen optimizada con multi-stage build, usuario no-root, y health checks.

```bash
# Build
docker.bat build
./docker.sh build

# Ejecutar en background
docker.bat up
./docker.sh up

# Ver logs
docker.bat logs
./docker.sh logs

# Detener
docker.bat down
./docker.sh down
```

**Características:**
- Multi-stage build (imagen pequeña ~200MB)
- Usuario no-root (seguridad)
- Health checks automáticos
- Resource limits configurados
- Optimizado para cloud deployment

#### 🔧 Modo Desarrollo

Imagen con hot-reload para desarrollo local.

```bash
# Build dev
docker.bat build-dev
./docker.sh build-dev

# Ejecutar con hot-reload
docker.bat up-dev
./docker.sh up-dev
```

**Características:**
- Hot-reload automático (cambios de código se reflejan instantáneamente)
- Volúmenes montados para código fuente
- Logs en tiempo real
- Debug mode activado

### Comandos disponibles

```bash
# Producción
docker.bat build         # Construir imagen
docker.bat up            # Iniciar contenedores
docker.bat down          # Detener contenedores
docker.bat restart       # Reiniciar contenedores
docker.bat logs          # Ver logs
docker.bat shell         # Abrir shell en contenedor
docker.bat ps            # Ver estado de contenedores
docker.bat health        # Verificar salud del servicio

# Desarrollo
docker.bat build-dev     # Construir imagen dev
docker.bat up-dev        # Iniciar en modo desarrollo
docker.bat logs-dev      # Ver logs dev
docker.bat shell-dev     # Abrir shell en contenedor dev

# Mantenimiento
docker.bat clean         # Limpiar contenedores y recursos
docker.bat rebuild       # Reconstruir desde cero
docker.bat test          # Ejecutar tests en contenedor

# Ayuda
docker.bat help          # Ver todos los comandos
```

### Deployment a Cloud

#### AWS ECS

```bash
# 1. Build imagen
docker build -t rag-backend:latest .

# 2. Tag para ECR
docker tag rag-backend:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/rag-backend:latest

# 3. Push a ECR
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/rag-backend:latest

# 4. Actualizar servicio ECS
aws ecs update-service --cluster rag-cluster --service rag-backend --force-new-deployment
```

#### Google Cloud Run

```bash
# 1. Build y push a GCR
gcloud builds submit --tag gcr.io/<project-id>/rag-backend

# 2. Deploy
gcloud run deploy rag-backend \
  --image gcr.io/<project-id>/rag-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances

```bash
# 1. Build
docker build -t rag-backend:latest .

# 2. Tag para ACR
docker tag rag-backend:latest <registry-name>.azurecr.io/rag-backend:latest

# 3. Push a ACR
docker push <registry-name>.azurecr.io/rag-backend:latest

# 4. Deploy a ACI
az container create \
  --resource-group rag-rg \
  --name rag-backend \
  --image <registry-name>.azurecr.io/rag-backend:latest \
  --cpu 1 --memory 2 \
  --port 8000
```

### Variables de entorno en Docker

El archivo `.env` se carga automáticamente en el contenedor. Para producción en cloud, configura las variables de entorno directamente en el servicio:

**AWS ECS:**
```json
{
  "environment": [
    {"name": "SUPABASE_URL", "value": "https://..."},
    {"name": "SUPABASE_KEY", "value": "..."},
    {"name": "GEMINI_API_KEY", "value": "..."}
  ]
}
```

**Google Cloud Run:**
```bash
gcloud run deploy rag-backend \
  --set-env-vars SUPABASE_URL=https://...,SUPABASE_KEY=...,GEMINI_API_KEY=...
```

**Azure Container Instances:**
```bash
az container create \
  --environment-variables SUPABASE_URL=https://... SUPABASE_KEY=... GEMINI_API_KEY=...
```

---

## 🧪 Testing

### Local (sin Docker)

```bash
# Ejecutar tests unitarios
pytest tests/unit/

# Ejecutar tests de integración
pytest tests/integration/

# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=. --cov-report=html
```

### Con Docker

```bash
# Ejecutar tests en contenedor
docker.bat test
./docker.sh test

# O manualmente
docker-compose exec backend pytest
```

---

## 🔧 Desarrollo

### Agregar nuevo caso de uso

1. **Definir DTO en `application/dtos/`**
```python
# application/dtos/new_feature_dto.py
@dataclass
class NewFeatureInput:
    param: str

@dataclass
class NewFeatureOutput:
    result: str
```

2. **Crear caso de uso en `application/use_cases/`**
```python
# application/use_cases/new_feature.py
class NewFeatureUseCase:
    def __init__(self, dependency: IDependency):
        self._dependency = dependency

    async def execute(self, input_dto: NewFeatureInput) -> NewFeatureOutput:
        # Lógica del caso de uso
        result = await self._dependency.do_something(input_dto.param)
        return NewFeatureOutput(result=result)
```

3. **Agregar dependency injection en `presentation/api/dependencies.py`**
```python
def get_new_feature_use_case(
    dependency: Annotated[Dependency, Depends(get_dependency)]
) -> NewFeatureUseCase:
    return NewFeatureUseCase(dependency=dependency)
```

4. **Crear endpoint en `presentation/api/routes/`**
```python
@router.post("/new-feature")
async def new_feature(
    request: NewFeatureRequest,
    use_case: Annotated[NewFeatureUseCase, Depends(get_new_feature_use_case)]
):
    input_dto = NewFeatureInput(param=request.param)
    output_dto = await use_case.execute(input_dto)
    return NewFeatureResponse(result=output_dto.result)
```

### Cambiar proveedor de embeddings (Gemini → OpenAI)

1. **Crear nueva implementación en `infrastructure/ai/`**
```python
# infrastructure/ai/openai_embedding_service.py
class OpenAIEmbeddingService(IEmbeddingService):
    async def generate_query_embedding(self, query: str) -> List[float]:
        # Implementación con OpenAI
        ...
```

2. **Actualizar dependency en `presentation/api/dependencies.py`**
```python
@lru_cache()
def get_embedding_service() -> IEmbeddingService:
    return OpenAIEmbeddingService()  # ← Solo cambiar esta línea
```

---

## 🎯 Principios de Diseño

### 1. **Separation of Concerns**
Cada capa tiene una responsabilidad clara:
- `domain/`: Reglas de negocio puras (sin dependencias externas)
- `application/`: Orquestación de casos de uso
- `infrastructure/`: Implementaciones concretas (Gemini, Supabase)
- `presentation/`: API HTTP

### 2. **Dependency Inversion**
Las capas internas definen interfaces, las externas las implementan:
```python
# domain/interfaces/embedding_service.py (Interface)
class IEmbeddingService(ABC):
    @abstractmethod
    async def generate_query_embedding(self, query: str) -> List[float]:
        pass

# infrastructure/ai/gemini_embedding_service.py (Implementation)
class GeminiEmbeddingService(IEmbeddingService):
    async def generate_query_embedding(self, query: str) -> List[float]:
        # Implementación concreta
        ...
```

### 3. **Dependency Injection**
Las dependencias se inyectan via FastAPI `Depends()`:
```python
@router.post("/query")
async def query_rag(
    request: QueryRequest,
    use_case: Annotated[QueryRAGUseCase, Depends(get_query_rag_use_case)]
):
    # use_case ya está configurado con todas sus dependencias
    ...
```

### 4. **Testability**
Los casos de uso son fáciles de testear con mocks:
```python
@pytest.mark.asyncio
async def test_query_rag():
    # Arrange: Mockear dependencias
    mock_embedding = Mock(spec=IEmbeddingService)
    mock_vector_store = Mock(spec=IVectorStore)
    mock_chat = Mock(spec=IChatService)

    use_case = QueryRAGUseCase(
        embedding_service=mock_embedding,
        vector_store=mock_vector_store,
        chat_service=mock_chat
    )

    # Act
    result = await use_case.execute(QueryInput(query="Test"))

    # Assert
    assert result.answer is not None
```

---

## 📦 Dependencias Principales

- **FastAPI**: Web framework
- **Pydantic**: Validación de datos
- **Supabase**: Vector database (pgvector)
- **Google Generative AI**: Embeddings + Chat (Gemini)
- **Uvicorn**: ASGI server

---

## 🔐 Seguridad

- Variables sensibles en `.env` (nunca commitear)
- CORS configurado para orígenes específicos
- Validación de entrada con Pydantic
- Manejo de errores con excepciones personalizadas

---

## 📝 Licencia

MIT License

---

## 👥 Contribuir

1. Sigue los principios de Layered Architecture
2. Agrega tests para nuevas funcionalidades
3. Documenta interfaces y casos de uso
4. Usa type hints en todo el código

---

## 🆘 Soporte

Para reportar issues o contribuir:
- Revisa la documentación de arquitectura en este README
- Consulta los ejemplos en `tests/`
- Revisa el código existente como referencia
