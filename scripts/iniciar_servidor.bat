@echo off
REM Inicia el sistema RFQ con Waitress (uso interno). Fase 5.
REM Las variables de entorno se leen automaticamente desde .env (settings.py).
setlocal
cd /d "%~dp0.."

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [AVISO] No se encontro .venv. Se usara el Python del sistema.
)

echo === Chequeo operativo ===
python manage.py check_operativo --simple
if errorlevel 1 (
    echo.
    echo [ERROR] El chequeo operativo fallo. No se inicia el servidor.
    echo         Revisa el mensaje de arriba y corrige antes de continuar.
    exit /b 1
)

echo === Iniciando servidor Waitress ===
python run_waitress.py
if errorlevel 1 (
    echo [ERROR] El servidor termino con error. Revisa logs\rfq.log
    exit /b 1
)
