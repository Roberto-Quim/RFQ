"""
Pruebas del servicio Django de Fase 2 (datos FICTICIOS, sin PROYECTO.xlsx real).

Ejecuta:
    python tests/test_servicios.py

Verifica:
  - extraer_preview() saca RFQ = numero de pedido y deja fecha faltante.
  - extraer_preview() NO escribe ni crea el archivo maestro (modo seguro).
  - carga limpia de la configuracion de Django (settings + import del motor).
"""
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rfq_project.settings")
import django  # noqa: E402
django.setup()

import config  # noqa: E402  (motor de Fase 1)
from seguimiento import services  # noqa: E402

CORREO_FICTICIO = """PEDIDO #777 | JUL 07, 2026

Nombre del Solicitante:
Persona Ficticia
Selecciona Unidad de Negocio:
Planta Demo Sur
Breve descripción de la solicitud de CapEx:
Equipo ficticio de prueba
"""


def _check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK  {msg}")


def test_preview_extrae():
    print("[1] Servicio extraer_preview() con .txt ficticio")
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "ficticio_777.txt"
        f.write_text(CORREO_FICTICIO, encoding="utf-8")
        dato = services.extraer_preview(f)
    _check(dato.rfq == "777", "RFQ = numero de pedido (777)")
    _check(dato.solicitante == "Persona Ficticia", "solicitante del formulario")
    _check(dato.planta == "Planta Demo Sur", "planta de Unidad de Negocio")
    _check(dato.fecha_arranque is None, "fecha de arranque queda faltante")


def test_preview_no_escribe():
    print("[2] extraer_preview() NO toca el Excel maestro (modo seguro)")
    original = config.ARCHIVO_MAESTRO
    with tempfile.TemporaryDirectory() as d:
        # Apuntar el maestro a una ruta temporal que NO existe.
        falso_maestro = Path(d) / "PROYECTO.xlsx"
        config.ARCHIVO_MAESTRO = falso_maestro
        try:
            txt = Path(d) / "ficticio_777.txt"
            txt.write_text(CORREO_FICTICIO, encoding="utf-8")
            services.extraer_preview(txt)
            _check(not falso_maestro.exists(),
                   "el preview no creo ni escribio PROYECTO.xlsx")
        finally:
            config.ARCHIVO_MAESTRO = original


def test_preview_sin_rfq_falla_claro():
    print("[3] extraer_preview() da error claro si no hay RFQ")
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "sin_rfq.txt"
        f.write_text("Correo sin numero de pedido.", encoding="utf-8")
        try:
            services.extraer_preview(f)
            raise AssertionError("deberia haber lanzado MotorError")
        except services.MotorError as e:
            _check("PEDIDO" in str(e) or "Request" in str(e),
                   "MotorError con mensaje claro sobre PEDIDO/Request")


if __name__ == "__main__":
    test_preview_extrae()
    test_preview_no_escribe()
    test_preview_sin_rfq_falla_claro()
    print("\nTODAS LAS PRUEBAS DEL SERVICIO PASARON.")
