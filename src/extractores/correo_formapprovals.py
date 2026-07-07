"""
Extractor de correos "Form Approvals" (RFQ de CapEx).

Estos RFQ llegan como correo reenviado con un bloque de campos:
    Etiqueta:
    valor
    Etiqueta:
    valor
    ...

Maneja:
  - .txt  : el correo pegado/guardado como texto plano.
  - .eml  : correo exportado (se extrae el cuerpo text/plain o se limpia el HTML).
  (.msg de Outlook requeriria la libreria extract-msg; se puede agregar luego.)

REGLA DE NEGOCIO (confirmada con Edith):
  - El numero de RFQ SE TOMA DEL NUMERO DE PEDIDO del correo.
        "PEDIDO #228"  -> RFQ = "228"
        "Request #228" -> RFQ = "228"
    Es el comportamiento por defecto (config.FUENTE_RFQ_CORREO = "pedido").

Puntos finos resueltos a partir del ejemplo real (Pedido #228):
  - El SOLICITANTE se toma del campo del formulario, NO del remitente
    (quien reenvia -Luis/Edith- no es el solicitante).
  - "TBD" se trata como dato faltante, no como valor.

PENDIENTES por confirmar con negocio:
  - Fecha de arranque: NO viene en este formato -> hoy queda faltante.
  - Planta: falta confirmar si "Unidad de Negocio" equivale directo a Planta
    o si requiere mapeo (config.MAPA_UNIDAD_A_PLANTA).
"""
import re
import unicodedata
from email import policy
from email.parser import BytesParser
from pathlib import Path

import config
from src.extractores.base import Extractor
from src.extractores.utilidades import limpiar_texto, parsear_fecha
from src.modelo import RFQData

VALORES_NULOS = {"tbd", "n/a", "na", "pendiente", "por definir", "-", ""}

# Etiqueta normalizada (sin acentos, minusculas, sin ':') -> clave interna
ETIQUETAS = {
    "direccion de correo electronico": "correo_solicitante",
    "nombre del solicitante": "solicitante",
    "selecciona unidad de negocio": "unidad_negocio",
    "clave del proyecto o numero de capex": "clave_capex",
    "tipo de capex": "tipo_capex",
    "breve descripcion de la solicitud de capex": "descripcion",
    "marca": "marca",
    "modelo": "modelo",
    "cantidad y lista de articulos a cotizar": "cantidad_lista",
}


def _norm(texto: str) -> str:
    """Minusculas, sin acentos, sin ':' final, espacios colapsados."""
    t = unicodedata.normalize("NFKD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.strip().lower().rstrip(":").strip()
    return " ".join(t.split())


def _valor_util(v):
    """Devuelve None si el valor es vacio o un marcador tipo 'TBD'."""
    v = limpiar_texto(v)
    if v is None or _norm(v) in VALORES_NULOS:
        return None
    return v


def parsear_texto(texto: str) -> dict:
    """Parsea el cuerpo del correo a un diccionario de campos crudos."""
    lineas = [ln.rstrip() for ln in texto.splitlines()]
    campos: dict[str, str] = {}

    # 1) Campos etiquetados: "Etiqueta:" y su valor en las lineas siguientes
    #    hasta la proxima etiqueta conocida.
    i = 0
    while i < len(lineas):
        clave = ETIQUETAS.get(_norm(lineas[i]))
        if clave:
            valores = []
            j = i + 1
            while j < len(lineas) and _norm(lineas[j]) not in ETIQUETAS:
                if lineas[j].strip():
                    valores.append(lineas[j].strip())
                # corta en linea vacia si ya capturamos algo (evita tragar texto de pie)
                elif valores:
                    break
                j += 1
            campos[clave] = " ".join(valores).strip()
            i = j
        else:
            i += 1

    # 2) Numero de pedido: "PEDIDO #228" o "Request #228".
    #    De aqui sale el RFQ por regla de negocio (RFQ = numero de pedido).
    m = re.search(r"(?:pedido|request)\s*#\s*(\d+)", texto, re.IGNORECASE)
    if m:
        campos["pedido"] = m.group(1)

    # 3) Fecha del correo/encabezado tipo "JUN 19, 2026" (fecha de solicitud,
    #    NO de arranque; disponible por si se decide usarla).
    m = re.search(r"([A-Z]{3})\s+(\d{1,2}),\s*(\d{4})", texto)
    if m:
        campos["fecha_solicitud_raw"] = m.group(0)

    return campos


def _leer_eml(path: Path) -> str:
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    cuerpo = msg.get_body(preferencelist=("plain", "html"))
    if cuerpo is None:
        return ""
    contenido = cuerpo.get_content()
    if cuerpo.get_content_type() == "text/html":
        contenido = re.sub(r"<[^>]+>", "\n", contenido)  # limpieza simple de HTML
    return contenido


class FormApprovalsExtractor(Extractor):
    extensiones = (".txt", ".eml")

    def extraer(self, path: Path) -> list[RFQData]:
        texto = _leer_eml(path) if path.suffix.lower() == ".eml" else \
            path.read_text(encoding="utf-8", errors="ignore")

        campos = parsear_texto(texto)

        # --- RFQ = numero de PEDIDO (regla de negocio confirmada). ---
        # Configurable via config.FUENTE_RFQ_CORREO; default "pedido".
        # El "or ... pedido" garantiza el fallback al numero de pedido aunque
        # se cambie la fuente y esa venga vacia.
        fuente = getattr(config, "FUENTE_RFQ_CORREO", "pedido")
        rfq = _valor_util(campos.get(fuente)) or _valor_util(campos.get("pedido"))
        if not rfq:
            return []  # sin identificador de RFQ no se puede registrar

        # --- Planta desde Unidad de Negocio (mapeo configurable) ---
        planta = _valor_util(campos.get("unidad_negocio"))
        mapa_planta = getattr(config, "MAPA_UNIDAD_A_PLANTA", {})
        if planta and planta in mapa_planta:
            planta = mapa_planta[planta]

        dato = RFQData(
            rfq=rfq,
            descripcion=_valor_util(campos.get("descripcion")),
            fecha_arranque=None,  # este formato no trae fecha de arranque
            solicitante=_valor_util(campos.get("solicitante")),
            planta=planta,
            origen_archivo=path.name,
        )
        dato.registrar_faltantes()
        return [dato]
