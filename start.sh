#!/bin/bash

# Script de inicio rápido para el backend RAG

echo "🚀 Iniciando Backend RAG..."
echo ""

# Verificar si existe venv
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv venv
    echo "✅ Entorno virtual creado"
    echo ""
fi

# Activar venv
echo "🔧 Activando entorno virtual..."
source venv/bin/activate || source venv/Scripts/activate
echo "✅ Entorno virtual activado"
echo ""

# Verificar si existe .env
if [ ! -f ".env" ]; then
    echo "⚠️  No se encontró archivo .env"
    echo "📋 Copiando .env.example a .env..."
    cp .env.example .env
    echo "⚙️  Por favor, edita .env con tus credenciales antes de continuar"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
fi

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt
echo "✅ Dependencias instaladas"
echo ""

# Ejecutar servidor
echo "🌐 Iniciando servidor en http://localhost:8000"
echo "📖 Documentación disponible en http://localhost:8000/docs"
echo ""
python main.py
