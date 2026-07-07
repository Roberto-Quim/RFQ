"""
Puente entre Django (Fase 2) y el motor local (Fase 1).

Esta es la UNICA pieza de la app que importa el motor. Las vistas hablan con
el motor solo a traves de estas funciones, para no acoplar Django al motor y
mantener el motor reutilizable y sin cambios.

Regla de oro del modo seguro:
  - extraer_preview()  -> SOLO lee el .txt. NUNCA toca PROYECTO.xlsx.
  - escribir_confirmado() -> hace backup y ESCRIBE. Se llama solo tras confirmar.
"""
import logging
import time
from pathlib import Path

# Motor de Fase 1 (intacto).
import config
from src import excel_maestro as maestro
from src.extractores.correo_formapprovals import FormApprovalsExtractor
from src.modelo import RFQData

from .locking import LockOcupado, lock_escritura_excel

log = logging.getLogger("seguimiento")


class MotorError(Exception):
    """Error de negocio con mensaje claro para mostrar al usuario."""


# ----------------------------------------------------------------------
# Subida de archivo (a una carpeta ignorada por Git)
# ----------------------------------------------------------------------
def guardar_subida(archivo, media_root: Path) -> Path:
    """Guarda el archivo subido en media/subidas/ con nombre unico."""
    carpeta = Path(media_root) / "subidas"
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / f"{int(time.time())}_{archivo.name}"
    with open(destino, "wb") as f:
        for chunk in archivo.chunks():
            f.write(chunk)
    return destino


# ----------------------------------------------------------------------
# Paso 2: extraer datos (SOLO LECTURA - no escribe al Excel)
# ----------------------------------------------------------------------
def extraer_preview(ruta_txt: Path) -> RFQData:
    """Parsea el .txt con el motor y devuelve el RFQData (sin escribir nada)."""
    try:
        registros = FormApprovalsExtractor().extraer(Path(ruta_txt))
    except Exception as e:  # noqa: BLE001
        log.error("Error leyendo RFQ %s: %s", ruta_txt, e)
        raise MotorError(f"No se pudo leer el archivo: {e}") from e
    if not registros:
        log.warning("Archivo sin RFQ valido: %s", ruta_txt)
        raise MotorError(
            "No se encontro un RFQ en el archivo. Debe contener 'PEDIDO #NNN' "
            "o 'Request #NNN'."
        )
    return registros[0]


# ----------------------------------------------------------------------
# Paso 5: escribir al Excel (solo tras confirmacion del usuario)
# ----------------------------------------------------------------------
def _validar_maestro():
    """Verifica que el maestro y la hoja existan, con mensajes claros."""
    if not config.ARCHIVO_MAESTRO.exists():
        raise MotorError(
            f"No existe el archivo maestro: {config.ARCHIVO_MAESTRO}. "
            "Coloca PROYECTO.xlsx en la raiz del proyecto."
        )


def _ruta_lock() -> Path:
    """Lockfile junto al maestro (misma carpeta) para serializar escrituras."""
    return config.ARCHIVO_MAESTRO.parent / ".proyecto_xlsx.lock"


def escribir_confirmado(dato: RFQData) -> dict:
    """Backup + escribe la fila en PROYECTO.xlsx. Devuelve un resumen.

    La escritura esta SERIALIZADA por un lock: solo una a la vez (ver locking.py).
    Lanza MotorError con mensaje claro si el maestro/hoja no existen, si el
    archivo esta abierto en Excel (bloqueado), o si otra escritura esta en curso.
    """
    _validar_maestro()

    try:
        with lock_escritura_excel(_ruta_lock()):
            return _escribir_bajo_lock(dato)
    except LockOcupado as e:
        log.warning("Escritura rechazada por lock ocupado (RFQ %s)", dato.rfq)
        raise MotorError(str(e)) from e


def _escribir_bajo_lock(dato: RFQData) -> dict:
    # 1) Backup ANTES de escribir.
    try:
        ruta_backup = maestro.backup()
    except PermissionError as e:
        log.error("Backup fallo (archivo abierto?) RFQ %s: %s", dato.rfq, e)
        raise MotorError(
            "No se pudo crear el backup: el archivo parece estar abierto en Excel. "
            "Cierralo y reintenta."
        ) from e

    # 2) Abrir hoja (valida existencia de la hoja 'SEGUIMIENTO ').
    try:
        wb, ws = maestro.cargar()
    except KeyError as e:
        log.error("Hoja no encontrada: %s", e)
        raise MotorError(str(e)) from e
    except FileNotFoundError as e:
        raise MotorError(str(e)) from e

    # 3) Agregar o actualizar (el motor solo toca A,B,C,D,F; no toca O ni P).
    accion = maestro.agregar_o_actualizar(ws, dato)

    # 4) Guardar de forma atomica.
    try:
        maestro.guardar(wb)
    except PermissionError as e:
        log.error("Guardado fallo (archivo abierto?) RFQ %s: %s", dato.rfq, e)
        raise MotorError(
            "No se pudo guardar: el archivo parece estar abierto en Excel. "
            "El original quedo intacto (se escribio en un temporal). Cierralo y reintenta."
        ) from e

    log.info("RFQ %s %s (backup %s)", dato.rfq, accion, ruta_backup.name)
    return {
        "accion": accion,                 # "agregado" | "actualizado"
        "backup": ruta_backup.name,
        "faltantes": list(dato.faltantes),
    }
