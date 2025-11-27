# 🐳 Docker Guide - RAG Backend

Guía completa para ejecutar y desplegar el backend RAG usando Docker.

---

## 📋 Tabla de Contenidos

1. [Inicio Rápido](#inicio-rápido)
2. [Estructura de Archivos](#estructura-de-archivos)
3. [Modos de Ejecución](#modos-de-ejecución)
4. [Comandos Disponibles](#comandos-disponibles)
5. [Deployment a Cloud](#deployment-a-cloud)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Inicio Rápido

### Prerequisitos

- **Docker Desktop** instalado y corriendo
- **Docker Compose** (incluido en Docker Desktop)
- Archivo `.env` configurado con tus credenciales

### Ejecución en 3 pasos

```bash
# 1. Navegar al directorio
cd backend

# 2. Build imagen
docker.bat build      # Windows
./docker.sh build     # Unix/macOS

# 3. Ejecutar
docker.bat up         # Windows
./docker.sh up        # Unix/macOS
```

**El servidor estará disponible en:** http://localhost:8000

**Documentación API:** http://localhost:8000/docs

---

## 📁 Estructura de Archivos

```
backend/
├── Dockerfile                 # Imagen de producción (multi-stage)
├── Dockerfile.dev             # Imagen de desarrollo (hot-reload)
├── docker-compose.yml         # Configuración producción
├── docker-compose.dev.yml     # Configuración desarrollo
├── .dockerignore              # Archivos excluidos
├── docker.sh                  # Script utilidades (Unix/macOS)
└── docker.bat                 # Script utilidades (Windows)
```

### `Dockerfile` (Producción)

**Características:**
- Multi-stage build (optimiza tamaño)
- Imagen base: `python:3.11-slim`
- Usuario no-root (`appuser`)
- Health checks automáticos
- Tamaño final: ~200MB

**Proceso de build:**
1. **Stage 1 (builder)**: Instala dependencias en virtual environment
2. **Stage 2 (runtime)**: Copia solo lo necesario, crea usuario, expone puerto

### `Dockerfile.dev` (Desarrollo)

**Características:**
- Single-stage build
- Hot-reload con Uvicorn
- Volúmenes montados para código fuente
- Logs en tiempo real

### `docker-compose.yml` (Producción)

**Configuración:**
- Service name: `backend`
- Container name: `rag-backend`
- Network: `rag-network` (bridge)
- Resource limits: 1 CPU, 2GB RAM
- Health checks cada 30s
- Logging con rotación automática

### `docker-compose.dev.yml` (Desarrollo)

**Configuración:**
- Service name: `backend-dev`
- Container name: `rag-backend-dev`
- Volúmenes montados para hot-reload
- Debug mode activado (`DEBUG=True`)

---

## 🎯 Modos de Ejecución

### 🚀 Modo Producción

**Cuándo usar:**
- Deployment a cloud (AWS, GCP, Azure)
- Testing de performance
- Producción local

**Características:**
- Imagen optimizada (multi-stage)
- Usuario no-root (seguridad)
- Resource limits
- Health checks
- Logs estructurados

**Comandos:**

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

# Estado
docker.bat ps
./docker.sh ps

# Verificar salud
docker.bat health
./docker.sh health

# Detener
docker.bat down
./docker.sh down
```

### 🔧 Modo Desarrollo

**Cuándo usar:**
- Desarrollo local
- Debugging
- Testing de cambios rápidos

**Características:**
- Hot-reload automático
- Código montado como volumen
- Logs en tiempo real
- Debug mode activado

**Comandos:**

```bash
# Build dev
docker.bat build-dev
./docker.sh build-dev

# Ejecutar (logs en terminal)
docker.bat up-dev
./docker.sh up-dev

# Ver logs
docker.bat logs-dev
./docker.sh logs-dev

# Shell en contenedor
docker.bat shell-dev
./docker.sh shell-dev
```

**Hot-reload en acción:**

1. Ejecuta `docker.bat up-dev`
2. Edita cualquier archivo `.py`
3. Guarda el archivo
4. El servidor se recarga automáticamente
5. Los cambios se reflejan instantáneamente

---

## 🛠️ Comandos Disponibles

### Comandos de Producción

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `build` | Construir imagen de producción | `docker.bat build` |
| `up` | Iniciar contenedores en background | `docker.bat up` |
| `down` | Detener y remover contenedores | `docker.bat down` |
| `restart` | Reiniciar contenedores | `docker.bat restart` |
| `logs` | Ver logs (Ctrl+C para salir) | `docker.bat logs` |
| `shell` | Abrir bash en contenedor | `docker.bat shell` |
| `ps` | Ver estado de contenedores | `docker.bat ps` |
| `health` | Verificar salud del servicio | `docker.bat health` |

### Comandos de Desarrollo

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `build-dev` | Construir imagen de desarrollo | `docker.bat build-dev` |
| `up-dev` | Iniciar en modo desarrollo | `docker.bat up-dev` |
| `logs-dev` | Ver logs de desarrollo | `docker.bat logs-dev` |
| `shell-dev` | Abrir shell en contenedor dev | `docker.bat shell-dev` |

### Comandos de Mantenimiento

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `clean` | Limpiar contenedores y recursos | `docker.bat clean` |
| `rebuild` | Reconstruir desde cero (no cache) | `docker.bat rebuild` |
| `test` | Ejecutar tests en contenedor | `docker.bat test` |

### Ver ayuda

```bash
docker.bat help      # Windows
./docker.sh help     # Unix/macOS
```

---

## ☁️ Deployment a Cloud

### AWS Elastic Container Service (ECS)

#### 1. Crear repositorio ECR

```bash
aws ecr create-repository --repository-name rag-backend --region us-east-1
```

#### 2. Autenticarse en ECR

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

#### 3. Build y push

```bash
# Build
docker build -t rag-backend:latest .

# Tag
docker tag rag-backend:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest

# Push
docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
```

#### 4. Crear task definition

```json
{
  "family": "rag-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "rag-backend",
      "image": "<aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "SUPABASE_URL", "value": "https://..."},
        {"name": "SUPABASE_KEY", "value": "..."},
        {"name": "GEMINI_API_KEY", "value": "..."}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### 5. Crear servicio ECS

```bash
aws ecs create-service \
  --cluster rag-cluster \
  --service-name rag-backend \
  --task-definition rag-backend:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

### Google Cloud Run

#### 1. Build y push a Google Container Registry

```bash
# Configurar proyecto
gcloud config set project <project-id>

# Build y push en un solo comando
gcloud builds submit --tag gcr.io/<project-id>/rag-backend
```

#### 2. Deploy a Cloud Run

```bash
gcloud run deploy rag-backend \
  --image gcr.io/<project-id>/rag-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --cpu 1 \
  --memory 2Gi \
  --max-instances 10 \
  --set-env-vars SUPABASE_URL=https://...,SUPABASE_KEY=...,GEMINI_API_KEY=...
```

#### 3. Verificar deployment

```bash
# Obtener URL
gcloud run services describe rag-backend --platform managed --region us-central1 --format 'value(status.url)'

# Test
curl https://rag-backend-xxx.run.app/health
```

---

### Azure Container Instances

#### 1. Crear Azure Container Registry

```bash
az acr create --resource-group rag-rg --name ragregistry --sku Basic
```

#### 2. Build y push

```bash
# Login a ACR
az acr login --name ragregistry

# Build
docker build -t rag-backend:latest .

# Tag
docker tag rag-backend:latest ragregistry.azurecr.io/rag-backend:latest

# Push
docker push ragregistry.azurecr.io/rag-backend:latest
```

#### 3. Deploy a Container Instances

```bash
az container create \
  --resource-group rag-rg \
  --name rag-backend \
  --image ragregistry.azurecr.io/rag-backend:latest \
  --cpu 1 \
  --memory 2 \
  --registry-login-server ragregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label rag-backend \
  --ports 8000 \
  --environment-variables SUPABASE_URL=https://... SUPABASE_KEY=... GEMINI_API_KEY=...
```

#### 4. Verificar deployment

```bash
az container show --resource-group rag-rg --name rag-backend --query ipAddress.fqdn

# Test
curl http://rag-backend.region.azurecontainer.io:8000/health
```

---

## 🔍 Troubleshooting

### Problema: Contenedor no inicia

**Síntomas:**
```
docker.bat up
Container exits immediately
```

**Solución:**
```bash
# Ver logs completos
docker.bat logs

# Verificar .env
cat .env

# Verificar que todas las variables estén configuradas
docker-compose config
```

---

### Problema: "Port 8000 already in use"

**Síntomas:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solución:**

```bash
# Opción 1: Detener el proceso que usa el puerto
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Unix/macOS
lsof -ti:8000 | xargs kill -9

# Opción 2: Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambia 8000 a 8001
```

---

### Problema: Cambios de código no se reflejan

**Síntomas:**
- Editaste código pero no se refleja en el contenedor

**Solución:**

```bash
# Si estás en modo producción, reconstruir
docker.bat rebuild

# Si estás en modo desarrollo, verificar volúmenes
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up
```

---

### Problema: "No module named 'xxx'"

**Síntomas:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solución:**

```bash
# Reconstruir imagen (actualiza requirements.txt)
docker.bat rebuild

# O forzar reinstalación
docker-compose exec backend pip install -r requirements.txt
```

---

### Problema: Health check failing

**Síntomas:**
```
Health check failed: unhealthy
```

**Solución:**

```bash
# Ver logs detallados
docker.bat logs

# Verificar manualmente
docker.bat shell
curl http://localhost:8000/health

# Verificar variables de entorno
docker.bat shell
env | grep SUPABASE
env | grep GEMINI
```

---

### Problema: Imagen muy grande

**Síntomas:**
- Imagen ocupa >500MB

**Solución:**

```bash
# Usar Dockerfile de producción (multi-stage)
docker build -f Dockerfile -t rag-backend:latest .

# Verificar tamaño
docker images rag-backend

# Limpiar imágenes antiguas
docker image prune -a
```

---

## 📊 Métricas y Monitoreo

### Ver uso de recursos

```bash
# CPU y RAM en tiempo real
docker stats rag-backend

# Logs con timestamp
docker logs -f --timestamps rag-backend
```

### Health checks

```bash
# Estado de salud
docker inspect --format='{{.State.Health.Status}}' rag-backend

# Últimos health checks
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' rag-backend
```

---

## 🔐 Seguridad

### Buenas prácticas implementadas

✅ **Usuario no-root**: Contenedor corre como `appuser` (UID 1000)
✅ **Multi-stage build**: Reduce superficie de ataque
✅ **Health checks**: Detecta contenedores no saludables
✅ **Resource limits**: Previene consumo excesivo
✅ **Logs rotados**: Evita llenar disco

### Recomendaciones adicionales

1. **No commitear .env** (ya está en .gitignore)
2. **Usar secrets en producción** (AWS Secrets Manager, GCP Secret Manager)
3. **Actualizar dependencias** regularmente
4. **Escanear vulnerabilidades**:
   ```bash
   docker scan rag-backend:latest
   ```

---

## 📚 Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [AWS ECS Guide](https://docs.aws.amazon.com/ecs/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Azure Container Instances](https://docs.microsoft.com/azure/container-instances/)
