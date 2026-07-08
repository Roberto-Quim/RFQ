"""
Registro/dispatcher de extractores.

Para agregar un formato nuevo: importa su clase y agregala a REGISTRO.
elegir_extractor(path) devuelve el primer extractor que sepa manejar el archivo.
"""
from pathlib import Path

from src.extractores.base import Extractor
from src.extractores.csv_manual import CsvManualExtractor
from src.extractores.excel_rfq import ExcelRfqExtractor
from src.extractores.correo_formapprovals import FormApprovalsExtractor
from src.extractores.pendientes import MsgExtractor, PdfExtractor, WordExtractor

# Orden importa si dos extractores comparten extension (aqui no ocurre).
# FormApprovalsExtractor va antes que MsgExtractor: .eml lo maneja Form Approvals.
REGISTRO: list[Extractor] = [
    CsvManualExtractor(),        # .csv  (funcional, para pruebas/carga manual)
    ExcelRfqExtractor(),         # .xlsx .xlsm (plantilla adaptable)
    FormApprovalsExtractor(),    # .txt .eml (correos Form Approvals - FUNCIONAL)
    MsgExtractor(),              # .msg  (placeholder mejorado)
    PdfExtractor(),              # .pdf  (placeholder mejorado)
    WordExtractor(),             # .docx (placeholder mejorado)
]


def elegir_extractor(path: Path):
    """Devuelve el extractor adecuado o None si ningun formato coincide."""
    for extractor in REGISTRO:
        if extractor.puede_procesar(path):
            return extractor
    return None
