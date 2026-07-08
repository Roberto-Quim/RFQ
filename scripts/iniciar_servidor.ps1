# Inicia el sistema RFQ con Waitress (uso interno). Fase 5.
# Ejecutar:  powershell -ExecutionPolicy Bypass -File scripts\iniciar_servidor.ps1
# Las variables de entorno se leen automaticamente desde .env (settings.py).
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$venv = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    & $venv
} else {
    Write-Warning "No se encontro .venv. Se usara el Python del sistema."
}

Write-Host "=== Chequeo operativo ===" -ForegroundColor Cyan
python manage.py check_operativo --simple
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] El chequeo operativo fallo. No se inicia el servidor." -ForegroundColor Red
    exit 1
}

Write-Host "=== Iniciando servidor Waitress ===" -ForegroundColor Cyan
python run_waitress.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] El servidor termino con error. Revisa logs\rfq.log" -ForegroundColor Red
    exit 1
}
