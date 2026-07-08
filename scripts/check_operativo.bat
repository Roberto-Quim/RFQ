@echo off
REM Chequeo operativo del sistema RFQ. Fase 5.
REM Uso:  scripts\check_operativo.bat            (salida detallada)
REM       scripts\check_operativo.bat --simple   (salida compacta)
setlocal
cd /d "%~dp0.."

if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"

python manage.py check_operativo %*
if errorlevel 1 (
    echo [ERROR] Chequeo operativo con problemas. Revisa arriba.
    exit /b 1
)
