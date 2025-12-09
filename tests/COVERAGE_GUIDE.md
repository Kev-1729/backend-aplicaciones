# 📊 Guía del Reporte HTML de Cobertura

## ¿Qué es el Reporte HTML de Cobertura?

El reporte HTML de cobertura es una **interfaz visual interactiva** que te muestra:

- ✅ Qué líneas de código están cubiertas por tests (en **verde**)
- ❌ Qué líneas NO están cubiertas (en **rojo**)
- ⚠️ Qué branches (if/else) están parcialmente cubiertos (en **amarillo**)
- 📊 Estadísticas detalladas por archivo y módulo
- 🔍 Navegación interactiva por el código fuente

---

## 🚀 Cómo Abrir el Reporte HTML

### **Opción 1: Script Automático (Recomendado)**
```bash
# En Windows
.\open_coverage.bat

# En Linux/Mac
./open_coverage.sh
```

### **Opción 2: Manual**
```bash
# 1. Generar el reporte
cd backend-aplicaciones
pytest tests/unit/ --cov=domain --cov=application --cov-report=html

# 2. Abrir en el navegador
# Windows
start htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Mac
open htmlcov/index.html
```

### **Opción 3: Abrir Directamente**
Navega a la carpeta y abre el archivo:
```
backend-aplicaciones/htmlcov/index.html
```

---

## 📖 Cómo Leer el Reporte

### **Página Principal (index.html)**

```
┌─────────────────────────────────────────────────┐
│  Coverage Report                                │
│  Total Coverage: 80%                            │
├─────────────────────────────────────────────────┤
│  Archivo                     Stmts  Miss  Cover │
│  domain/entities/document.py   24     0   100% │ ✅
│  domain/entities/chunk.py      18     0   100% │ ✅
│  application/query_rag.py     125     4    95% │ ⚠️
│  domain/entities/feedback.py   82    42    36% │ ❌
└─────────────────────────────────────────────────┘
```

**Columnas explicadas:**
- **Stmts** - Total de líneas de código ejecutables
- **Miss** - Líneas NO cubiertas por tests
- **Branch** - Branches condicionales (if/else)
- **BrPart** - Branches parcialmente cubiertos
- **Cover** - Porcentaje de cobertura

**Códigos de color:**
- 🟢 **Verde (≥90%)** - Excelente cobertura
- 🟡 **Amarillo (70-89%)** - Buena cobertura, mejorable
- 🔴 **Rojo (<70%)** - Necesita más tests

---

### **Vista de Archivo Individual**

Al hacer clic en un archivo, verás el código fuente con colores:

```python
1  ✅  def is_legal_document(self) -> bool:
2  ✅      """Determina si es un documento legal"""
3  ✅      legal_types = {"ley", "ordenanza", "decreto"}
4  ✅      return self.document_type in legal_types
5
6  ❌  def nueva_funcionalidad(self):
7  ❌      """Esta función no tiene tests"""
8  ❌      return "Sin tests"
```

**Colores en el código:**
- 🟢 **Verde** - Línea ejecutada por tests
- 🔴 **Rojo** - Línea NUNCA ejecutada por tests
- 🟡 **Amarillo** - Branch parcialmente cubierto
- ⚪ **Blanco/Gris** - Línea no ejecutable (comentarios, declaraciones)

---

## 🎯 Ejemplo Práctico

### **Situación: query_rag.py tiene 95% de cobertura**

1. **Abre el reporte HTML**
   ```bash
   start htmlcov/index.html
   ```

2. **Haz clic en** `application/use_cases/query_rag.py`

3. **Verás algo como:**
   ```python
   125  ✅  answer = await self._chat_service.generate_answer(...)
   126  ✅  logger.info(f"Answer generated")
   127
   128  ❌  except TimeoutError as e:
   129  ❌      logger.error(f"Timeout: {e}")
   130  ❌      raise
   ```

4. **Interpretación:**
   - Líneas 125-126: ✅ Cubiertas (hay un test que ejecuta esto)
   - Líneas 128-130: ❌ No cubiertas (falta test para TimeoutError)

5. **Acción:**
   - Crear un nuevo test que simule un TimeoutError:
   ```python
   @pytest.mark.asyncio
   async def test_chat_service_timeout(use_case, mock_chat_service):
       mock_chat_service.generate_answer.side_effect = TimeoutError()
       with pytest.raises(TimeoutError):
           await use_case.execute(sample_query_input)
   ```

---

## 📊 Navegación del Reporte

### **Índice Principal**
- **index.html** - Vista general de todos los módulos
- **class_index.html** - Índice de clases
- **function_index.html** - Índice de funciones

### **Funciones Útiles**
- 🔍 **Búsqueda** - Buscar archivos específicos
- 📁 **Filtros** - Filtrar por cobertura (solo <90%, etc.)
- ↕️ **Ordenar** - Ordenar por nombre, cobertura, líneas faltantes
- 🖱️ **Click en archivo** - Ver código fuente con colores

---

## 🎨 Interpretación Visual

### **Ejemplo de Código Coloreado**

```python
1   ✅  @dataclass
2   ✅  class Document:
3   ✅      id: str
4   ✅      filename: str
5
6   ✅      def is_legal_document(self) -> bool:
7   ⚠️          if self.document_type in legal_types:  # Branch cubierto
8   ✅              return True
9   ❌          else:                                   # Branch NO cubierto
10  ❌              logger.warning("Not legal")
11  ❌              return False
```

**Análisis:**
- Líneas 1-5: ✅ Totalmente cubiertas
- Línea 6: ✅ Función llamada por tests
- Línea 7: ⚠️ `if True` cubierto, pero `if False` no
- Líneas 8: ✅ Return True ejecutado
- Líneas 9-11: ❌ Bloque `else` nunca ejecutado

**Solución:** Agregar test que pase por el `else`:
```python
def test_is_legal_document_false():
    doc = Document(..., document_type="formulario")
    assert doc.is_legal_document() == False
```

---

## 🔥 Casos de Uso Comunes

### **1. Encontrar qué falta testear**
```
1. Abre index.html
2. Ordena por "Cover" (ascendente)
3. Los archivos con menor % están primero
4. Haz clic en el archivo con menor cobertura
5. Las líneas rojas son las que necesitan tests
```

### **2. Verificar un módulo específico**
```
1. Abre index.html
2. Usa Ctrl+F para buscar "query_rag.py"
3. Haz clic en el archivo
4. Revisa las líneas rojas/amarillas
5. Crea tests para esas líneas
```

### **3. Mejorar cobertura de branches**
```
1. Busca líneas amarillas (⚠️)
2. Son if/else o switch parcialmente cubiertos
3. Crea tests para el camino no cubierto
```

---

## 📈 Metas de Cobertura

### **Recomendaciones por Tipo**
| Tipo de Código | Meta de Cobertura |
|----------------|-------------------|
| **Entidades de Dominio** | **100%** (lógica crítica) |
| **Casos de Uso** | **≥95%** (orquestación) |
| **Servicios** | **≥90%** (integraciones) |
| **APIs/Routes** | **≥85%** (endpoints) |
| **Configuración** | **≥70%** (settings) |

### **Tu Estado Actual**
```
✅ domain/entities/document.py      100%  (Meta: 100%)
✅ domain/entities/chunk.py          100%  (Meta: 100%)
✅ domain/entities/chat_message.py   100%  (Meta: 100%)
✅ domain/entities/chat_session.py   100%  (Meta: 100%)
✅ application/get_statistics.py     100%  (Meta: 95%)
⚠️ application/query_rag.py           95%  (Meta: 95%)
❌ domain/entities/feedback.py        36%  (Meta: 100%)
```

---

## 🛠️ Comandos Útiles

### **Generar Diferentes Reportes**
```bash
# Solo HTML
pytest tests/unit/ --cov=domain --cov=application --cov-report=html

# HTML + Terminal
pytest tests/unit/ --cov=domain --cov=application --cov-report=html --cov-report=term

# HTML + Terminal + XML (para CI/CD)
pytest tests/unit/ --cov=domain --cov=application --cov-report=html --cov-report=term --cov-report=xml

# Mostrar líneas faltantes en terminal
pytest tests/unit/ --cov=domain --cov=application --cov-report=term-missing

# Con threshold mínimo (falla si <80%)
pytest tests/unit/ --cov=domain --cov=application --cov-fail-under=80
```

### **Filtrar Módulos Específicos**
```bash
# Solo domain
pytest tests/unit/ --cov=domain --cov-report=html

# Solo application
pytest tests/unit/ --cov=application --cov-report=html

# Módulo específico
pytest tests/unit/ --cov=domain.entities.document --cov-report=html
```

---

## 📚 Recursos Adicionales

- [Documentación pytest-cov](https://pytest-cov.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Interpreting Coverage Reports](https://coverage.readthedocs.io/en/latest/index.html)

---

## 💡 Tips Profesionales

1. **Abre el reporte después de cada sesión de testing**
   - Identifica gaps rápidamente
   - Prioriza qué testear primero

2. **Usa el reporte para code reviews**
   - Compartir `htmlcov/` con tu equipo
   - Asegurar que nuevo código tenga tests

3. **No persigas 100% ciegamente**
   - 100% en lógica de negocio (entidades, use cases)
   - 80-90% en infraestructura es aceptable
   - Algunos archivos de config no necesitan tests

4. **Ignora archivos generados/externos**
   ```bash
   # En pytest.ini o .coveragerc
   omit =
       */migrations/*
       */tests/*
       */venv/*
   ```

5. **Integra con CI/CD**
   ```yaml
   # .github/workflows/test.yml
   - name: Generate Coverage Report
     run: pytest --cov --cov-report=html
   - name: Upload Coverage
     uses: codecov/codecov-action@v3
   ```

---

## 🎯 Próximos Pasos

1. ✅ Abre el reporte: `start htmlcov/index.html`
2. 📊 Revisa la cobertura general (80%)
3. 🔍 Identifica archivos con baja cobertura
4. ✏️ Crea tests para líneas rojas
5. 🔄 Re-genera el reporte y verifica mejoras
6. 🎉 Celebra cuando llegues a >90%

---

**¡Explora tu código visualmente y mejora la calidad con tests! 🚀**
