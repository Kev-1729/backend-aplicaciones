@echo off
REM Script de utilidades Docker para RAG Backend (Windows)

setlocal enabledelayedexpansion

REM ========================================
REM Comandos disponibles
REM ========================================

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help

if "%1"=="build" goto build
if "%1"=="build-dev" goto build_dev
if "%1"=="up" goto up
if "%1"=="up-dev" goto up_dev
if "%1"=="down" goto down
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="logs-dev" goto logs_dev
if "%1"=="shell" goto shell
if "%1"=="shell-dev" goto shell_dev
if "%1"=="ps" goto ps
if "%1"=="clean" goto clean
if "%1"=="rebuild" goto rebuild
if "%1"=="health" goto health
if "%1"=="test" goto test

echo [ERROR] Unknown command: %1
echo.
goto help

:build
echo [+] Building Docker image...
docker-compose build
echo [OK] Image built successfully
goto end

:build_dev
echo [+] Building Docker image (dev mode)...
docker-compose -f docker-compose.dev.yml build
echo [OK] Dev image built successfully
goto end

:up
echo [+] Starting containers...
docker-compose up -d
echo [OK] Containers started
echo [i] API available at: http://localhost:8000
echo [i] Docs available at: http://localhost:8000/docs
goto end

:up_dev
echo [+] Starting containers (dev mode with hot-reload)...
docker-compose -f docker-compose.dev.yml up
goto end

:down
echo [+] Stopping containers...
docker-compose down
echo [OK] Containers stopped
goto end

:restart
echo [+] Restarting containers...
docker-compose restart
echo [OK] Containers restarted
goto end

:logs
echo [+] Showing logs (Ctrl+C to exit)...
docker-compose logs -f backend
goto end

:logs_dev
echo [+] Showing dev logs (Ctrl+C to exit)...
docker-compose -f docker-compose.dev.yml logs -f backend-dev
goto end

:shell
echo [+] Opening shell in container...
docker-compose exec backend /bin/bash
goto end

:shell_dev
echo [+] Opening shell in dev container...
docker-compose -f docker-compose.dev.yml exec backend-dev /bin/bash
goto end

:ps
echo [+] Container status:
docker-compose ps
goto end

:clean
echo [+] Cleaning up Docker resources...
docker-compose down -v --remove-orphans
docker system prune -f
echo [OK] Cleanup complete
goto end

:rebuild
echo [+] Rebuilding from scratch...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo [OK] Rebuild complete
goto end

:health
echo [+] Checking health status...
curl -f http://localhost:8000/health
if %ERRORLEVEL% EQU 0 (
    echo [OK] Service is healthy
) else (
    echo [ERROR] Service is unhealthy
)
goto end

:test
echo [+] Running tests in container...
docker-compose exec backend pytest
goto end

:help
echo ========================================
echo   Docker Utility Script for RAG Backend
echo ========================================
echo.
echo Usage: docker.bat [command]
echo.
echo Production Commands:
echo   build         Build Docker image
echo   up            Start containers in background
echo   down          Stop containers
echo   restart       Restart containers
echo   logs          View container logs
echo   ps            Show container status
echo   shell         Open bash shell in container
echo   health        Check service health
echo.
echo Development Commands:
echo   build-dev     Build Docker image (dev mode)
echo   up-dev        Start containers with hot-reload
echo   logs-dev      View dev container logs
echo   shell-dev     Open bash shell in dev container
echo.
echo Maintenance Commands:
echo   clean         Remove containers and clean up
echo   rebuild       Rebuild from scratch (no cache)
echo   test          Run tests in container
echo.
echo Examples:
echo   docker.bat build         # Build production image
echo   docker.bat up            # Start in production mode
echo   docker.bat up-dev        # Start in dev mode with hot-reload
echo   docker.bat logs          # View logs
echo   docker.bat shell         # Open shell in container
echo.
goto end

:end
endlocal
