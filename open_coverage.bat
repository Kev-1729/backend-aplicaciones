@echo off
REM Script para abrir el reporte de cobertura HTML en el navegador

echo ========================================
echo   Ejecutando Tests con Cobertura
echo ========================================
echo.

echo Ejecutando todos los tests unitarios...
python -m pytest tests/unit/ --cov=domain --cov=application --cov-report=html --cov-report=term-missing --cov-branch -v

echo.
echo ========================================
echo   Resumen de Cobertura
echo ========================================
echo.
echo Reporte HTML generado en: htmlcov\index.html
echo.

echo Abriendo reporte en el navegador...
start htmlcov\index.html

echo.
echo Reporte abierto en tu navegador predeterminado
echo.
pause
