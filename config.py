"""
Configuracion central del MVP (Fase 1 - motor local).

Estructura confirmada tras inspeccionar el PROYECTO.xlsx real:
  - Hoja: "SEGUIMIENTO " (OJO: lleva un ESPACIO al final del nombre).
  - Encabezados en la fila 2; los datos empiezan en la fila 3.
  - Columnas gestionadas: A, B, C, D, F.
  - Columnas O y P tienen formulas (O=IF, P=resta) -> NO se escriben.
"""
import os
from pathlib import Path

# --- Rutas ---
RAIZ = Path(__file__).resolve().parent


def _ruta_env(nombre_env: str, default: Path) -> Path:
    """Ruta configurable por variable de entorno, con fallback al default.

    Permite que Django (Fase 3) apunte el maestro/carpetas a otra ubicacion
    SIN cambiar el comportamiento de la CLI: si la variable no esta definida,
    se usa exactamente la ruta de siempre.
    """
    valor = os.environ.get(nombre_env)
    return Path(valor).expanduser() if valor else default


ARCHIVO_MAESTRO = _ruta_env("RFQ_ARCHIVO_MAESTRO", RAIZ / "PROYECTO.xlsx")
CARPETA_ENTRADA = _ruta_env("RFQ_CARPETA_ENTRADA", RAIZ / "entrada")       # RFQ nuevos
CARPETA_PROCESADOS = _ruta_env("RFQ_CARPETA_PROCESADOS", RAIZ / "procesados")  # ya procesados
CARPETA_BACKUPS = _ruta_env("RFQ_CARPETA_BACKUPS", RAIZ / "backups")       # copias del maestro
CARPETA_REPORTES = _ruta_env("RFQ_CARPETA_REPORTES", RAIZ / "reportes")    # bitacoras

# --- Estructura de la hoja SEGUIMIENTO ---
# IMPORTANTE: el nombre real de la hoja termina con un ESPACIO. No lo quites.
HOJA_SEGUIMIENTO = "SEGUIMIENTO "
FILA_ENCABEZADOS = 2        # fila donde estan los titulos de columna
PRIMERA_FILA_DATOS = 3      # primera fila con datos reales

# Mapeo campo -> columna (letra de Excel)
COLUMNAS = {
    "rfq": "A",
    "descripcion": "B",
    "fecha_arranque": "C",
    "solicitante": "D",
    "planta": "F",
}

# --- Comportamiento ---
FORMATO_FECHA = "DD/MM/YYYY"   # formato numerico de Excel para la fecha de arranque
VALOR_FALTANTE = ""            # que poner si falta un dato. Usa "" para vacio,
                               # o "No encontrado" para marcarlo explicitamente.
COPIAR_ESTILO_FILA_NUEVA = True  # al agregar fila nueva, copia estilo/formato de la
                                 # fila anterior (bordes, formulas de otras columnas)

# --- Extractor de correos Form Approvals ---
# REGLA DE NEGOCIO (confirmada): el RFQ se toma del NUMERO DE PEDIDO del correo.
#   "PEDIDO #228" / "Request #228" -> RFQ = "228".
# Opciones: "pedido" (default) o "clave_capex" (Clave del proyecto / No. CapEx).
FUENTE_RFQ_CORREO = "pedido"

# PENDIENTE de confirmar con negocio: si "Selecciona Unidad de Negocio" equivale
# directo a Planta o si necesita mapeo. Vacio = se usa el valor tal cual.
# Cuando se confirme, llenar asi:  "Questum Maquinados Ramos": "Ramos Arizpe"
MAPA_UNIDAD_A_PLANTA = {
}
