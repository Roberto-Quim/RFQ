"""Helpers compartidos por los extractores."""
from datetime import date, datetime


def parsear_fecha(valor):
    """Intenta convertir un valor a date. Devuelve None si no se puede.

    Acepta: date/datetime (tal cual), y strings comunes en Mexico:
    dd/mm/aaaa, dd-mm-aaaa, aaaa-mm-dd.
    """
    if valor in (None, ""):
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = str(valor).strip()
    formatos = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%m/%d/%Y")
    for fmt in formatos:
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None  # no se pudo interpretar -> se reportara como faltante/aviso


def limpiar_texto(valor):
    """Normaliza un texto: quita espacios sobrantes. None si viene vacio."""
    if valor in (None, ""):
        return None
    return " ".join(str(valor).split()).strip() or None
