"""
Configuracion central del MVP.

TODO tras inspeccionar PROYECTO.xlsx:
  - Ajustar HOJA_SEGUIMIENTO si el nombre exacto es distinto.
  - Ajustar FILA_ENCABEZADOS y PRIMERA_FILA_DATOS.
  - Confirmar las letras de columna (A, B, C, D, F).
  - Confirmar FORMATO_FECHA segun como se muestran las fechas en el maestro.
"""
from pathlib import Path

# --- Rutas ---
RAIZ = Path(__file__).resolve().parent
ARCHIVO_MAESTRO = RAIZ / "PROYECTO.xlsx"
CARPETA_ENTRADA = RAIZ / "entrada"       # RFQ nuevos a procesar
CARPETA_PROCESADOS = RAIZ / "procesados" # se mueven aqui tras procesar
CARPETA_BACKUPS = RAIZ / "backups"       # copia del maestro antes de cada corrida
CARPETA_REPORTES = RAIZ / "reportes"     # bitacoras

# --- Estructura de la hoja SEGUIMIENTO ---
HOJA_SEGUIMIENTO = "SEGUIMIENTO"
FILA_ENCABEZADOS = 1        # fila donde estan los titulos de columna
PRIMERA_FILA_DATOS = 2      # primera fila con datos reales

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
