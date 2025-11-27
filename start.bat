@echo off
REM Script de inicio rápido para el backend RAG (Windows)

echo ========================================
echo    Backend RAG - Inicio Rapido
echo ========================================
echo.

REM Verificar si existe venv
if not exist "venv" (
    echo [+] Creando entorno virtual...
    python -m venv venv
    echo [OK] Entorno virtual creado
    echo.
)

REM Activar venv
echo [+] Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado
echo.

REM Verificar si existe .env
if not exist ".env" (
    echo [!] No se encontro archivo .env
    echo [+] Copiando .env.example a .env...
    copy .env.example .env
    echo.
    echo [!] IMPORTANTE: Edita .env con tus credenciales antes de continuar
    echo.
    pause
)

REM Instalar dependencias
echo [+] Instalando dependencias...
pip install -r requirements.txt
echo [OK] Dependencias instaladas
echo.

REM Ejecutar servidor
echo ========================================
echo  Servidor iniciado en http://localhost:8000
echo  Documentacion: http://localhost:8000/docs
echo ========================================
echo.
python main.py
