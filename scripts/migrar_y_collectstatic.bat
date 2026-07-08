@echo off
REM Aplica migraciones y recolecta estaticos. Fase 5.
REM Ejecutar tras actualizar el codigo o cambiar dependencias.
setlocal
cd /d "%~dp0.."

if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"

echo === Aplicando migraciones ===
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] migrate fallo.
    exit /b 1
)

echo === Recolectando estaticos ===
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo [ERROR] collectstatic fallo.
    exit /b 1
)

echo === Listo ===
