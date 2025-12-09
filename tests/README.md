# Tests - Backend RAG System

Este directorio contiene todos los tests del sistema backend RAG.

## Estructura

```
tests/
├── conftest.py                        # Fixtures compartidos
├── unit/                              # Tests unitarios
│   ├── domain/                        # Tests de entidades
│   │   └── entities/
│   │       ├── test_document.py       # Tests de Document
│   │       ├── test_chunk.py          # Tests de DocumentChunk
│   │       ├── test_chat_message.py   # Tests de ChatMessage
│   │       └── test_chat_session.py   # Tests de ChatSession
│   └── application/                   # Tests de casos de uso
│       └── use_cases/
│           ├── test_query_rag.py      # Tests de QueryRAGUseCase
│           └── test_get_statistics.py # Tests de GetStatisticsUseCase
├── integration/                       # Tests de integración (futuro)
└── api/                              # Tests de API (futuro)
```

## Requisitos

```bash
pip install -r requirements.txt
```

Dependencias de testing:
- pytest==8.3.4
- pytest-asyncio==0.25.2
- pytest-cov==6.0.0
- httpx==0.28.1

## Ejecutar Tests

### Todos los tests unitarios
```bash
pytest tests/unit/
```

### Tests con cobertura de código
```bash
pytest tests/unit/ --cov=domain --cov=application --cov-report=html
```

### Tests de una categoría específica
```bash
# Solo tests de entidades
pytest tests/unit/domain/entities/

# Solo tests de casos de uso
pytest tests/unit/application/use_cases/
```

### Tests de un archivo específico
```bash
pytest tests/unit/domain/entities/test_document.py
pytest tests/unit/application/use_cases/test_query_rag.py
```

### Tests con salida verbosa
```bash
pytest tests/unit/ -v
```

### Tests con salida mínima
```bash
pytest tests/unit/ -q
```

### Tests con marcadores específicos
```bash
# Solo tests unitarios (cuando se agreguen marcadores)
pytest -m unit

# Solo tests de integración (cuando se agreguen marcadores)
pytest -m integration
```

### Ver reporte de cobertura HTML
```bash
pytest tests/unit/ --cov=domain --cov=application --cov-report=html
# Abrir htmlcov/index.html en el navegador
```

## Resultados Actuales

### Estadísticas de Tests
- **Total de tests:** 139
- **Tests pasados:** 139 ✅
- **Cobertura total:** 80%

### Cobertura por módulo
| Módulo | Cobertura |
|--------|-----------|
| `domain/entities/document.py` | 100% |
| `domain/entities/chunk.py` | 100% |
| `domain/entities/chat_message.py` | 100% |
| `domain/entities/chat_session.py` | 100% |
| `application/use_cases/get_statistics.py` | 100% |
| `application/use_cases/query_rag.py` | 95% |
| **TOTAL** | **80%** |

## Tests Implementados

### Domain Entities (103 tests)

#### Document (28 tests)
- ✅ Creación de documentos
- ✅ Identificación de documentos legales
- ✅ Identificación de documentos pequeños
- ✅ Lógica de chunking por artículos
- ✅ Lógica de single chunk
- ✅ Tests parametrizados para múltiples casos

#### DocumentChunk (22 tests)
- ✅ Creación de chunks
- ✅ Validación de dimensión de embeddings (768 dims)
- ✅ Validación de texto
- ✅ Metadata opcional
- ✅ Tests parametrizados

#### ChatMessage (24 tests)
- ✅ Creación de mensajes (user, assistant, system)
- ✅ Validación de roles
- ✅ Validación de contenido
- ✅ Manejo de metadata
- ✅ Serialización a diccionario

#### ChatSession (29 tests)
- ✅ Creación de sesiones
- ✅ Agregar mensajes
- ✅ Filtrar mensajes por rol
- ✅ Obtener mensajes recientes
- ✅ Generar contexto para LLM
- ✅ Limpiar historial
- ✅ Actualización de timestamps

### Application Use Cases (36 tests)

#### QueryRAGUseCase (24 tests)
- ✅ Query sin session_id (nueva conversación)
- ✅ Query con session_id (continuación)
- ✅ Creación de sesión si no existe
- ✅ Búsqueda sin resultados
- ✅ Comandos especiales (ayuda, FAQ, temas, RAG help)
- ✅ Construcción de contexto
- ✅ Carga de historial conversacional
- ✅ Guardar interacciones
- ✅ Extracción de fuentes únicas
- ✅ Parámetros correctos a servicios
- ✅ Límite de historial
- ✅ Manejo de errores (embedding, vector store, LLM)

#### GetStatisticsUseCase (12 tests)
- ✅ Obtener estadísticas completas
- ✅ Base de datos vacía
- ✅ Campos faltantes (valores por defecto)
- ✅ Números grandes
- ✅ Muchas categorías
- ✅ Manejo de errores
- ✅ Casos extremos (valores negativos, None, timeout, conexión)

## Fixtures Disponibles

### Entidades de Dominio
- `sample_document` - Documento de prueba
- `sample_legal_document` - Documento legal (ordenanza)
- `sample_small_document` - Documento pequeño (formulario)
- `sample_embedding` - Embedding de 768 dimensiones
- `sample_chunk` - Chunk de documento
- `sample_user_message` - Mensaje de usuario
- `sample_assistant_message` - Mensaje del asistente
- `sample_chat_session` - Sesión con historial
- `empty_chat_session` - Sesión vacía

### DTOs
- `sample_query_input` - QueryInput con session_id
- `sample_query_input_no_session` - QueryInput sin session_id
- `sample_query_output` - QueryOutput de prueba

### Mocks
- `mock_embedding_service` - Mock de IEmbeddingService
- `mock_vector_store` - Mock de IVectorStore
- `mock_chat_service` - Mock de IChatService
- `mock_session_store` - Mock de IChatSessionStore

### Colecciones de Datos
- `sample_conversation_history` - Historial de 4 mensajes
- `sample_similar_chunks` - Lista de chunks similares (búsqueda vectorial)

## Agregar Nuevos Tests

### Ejemplo: Test Unitario de Entidad
```python
def test_nueva_funcionalidad(sample_document):
    """Test: Descripción de qué se está probando"""
    # Arrange
    documento = sample_document

    # Act
    resultado = documento.nueva_funcionalidad()

    # Assert
    assert resultado == valor_esperado
```

### Ejemplo: Test con Mock Asíncrono
```python
@pytest.mark.asyncio
async def test_caso_de_uso(use_case, mock_service):
    """Test: Descripción del caso de uso"""
    # Configurar mock
    mock_service.metodo.return_value = valor_esperado

    # Ejecutar
    resultado = await use_case.execute(input_dto)

    # Verificar
    assert resultado.campo == valor_esperado
    mock_service.metodo.assert_called_once()
```

## Buenas Prácticas

1. **Nombres descriptivos:** Usa nombres que expliquen qué se está probando
2. **Arrange-Act-Assert:** Estructura clara en cada test
3. **Un concepto por test:** No mezclar múltiples validaciones
4. **Usa fixtures:** Reutiliza datos de prueba
5. **Tests parametrizados:** Para probar múltiples casos similares
6. **Mocks para dependencias:** Aísla la lógica bajo test
7. **Tests asíncronos:** Usa `@pytest.mark.asyncio` para funciones async

## Comandos Útiles

```bash
# Ejecutar tests y detener en el primer fallo
pytest tests/unit/ -x

# Ejecutar tests que fallaron en la última ejecución
pytest --lf

# Ejecutar tests mostrando print statements
pytest tests/unit/ -s

# Ejecutar tests con timeout (útil para async)
pytest tests/unit/ --timeout=10

# Generar reporte XML (para CI/CD)
pytest tests/unit/ --junitxml=test-results.xml

# Limpiar cache de pytest
pytest --cache-clear
```

## Próximos Pasos

- [ ] Implementar tests de integración (infrastructure/)
- [ ] Implementar tests de API (presentation/)
- [ ] Agregar tests de performance
- [ ] Configurar CI/CD para ejecutar tests automáticamente
- [ ] Aumentar cobertura de código a >90%

## Troubleshooting

### Error: "async def functions are not natively supported"
**Solución:** Asegúrate de tener `pytest-asyncio` instalado y configurado en `pytest.ini`

### Error: "ModuleNotFoundError"
**Solución:** Ejecuta pytest desde el directorio `backend-aplicaciones/`

### Error: Fixtures no encontrados
**Solución:** Verifica que `conftest.py` esté en la raíz de `tests/`

### Tests lentos
**Solución:**
- Usa `-n auto` para ejecución paralela (requiere `pytest-xdist`)
- Marca tests lentos con `@pytest.mark.slow` y excluye con `-m "not slow"`

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Asyncio](https://pytest-asyncio.readthedocs.io/)
- [Python Mock/MagicMock](https://docs.python.org/3/library/unittest.mock.html)
- [Pytest Coverage](https://pytest-cov.readthedocs.io/)
