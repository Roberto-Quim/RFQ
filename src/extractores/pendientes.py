"""
Extractores PLACEHOLDER para PDF, Word y correo.

Aun no implementados: dejan el sistema preparado para recibirlos sin cambiar
el resto del codigo. Cuando tengas archivos reales, se implementa extraer()
y se descomenta la libreria correspondiente en requirements.txt.

  - PDF   -> pdfplumber
  - Word  -> python-docx (.docx)
  - Correo-> extract-msg (.msg de Outlook) / email (stdlib para .eml)
"""
from pathlib import Path

from src.extractores.base import Extractor
from src.modelo import RFQData


class _NoImplementado(Extractor):
    nombre = "generico"

    def extraer(self, path: Path) -> list[RFQData]:
        raise NotImplementedError(
            f"Extractor {self.nombre} aun no implementado para {path.name}. "
            f"Comparte un archivo de ejemplo para definir la extraccion."
        )


class PdfExtractor(_NoImplementado):
    extensiones = (".pdf",)
    nombre = "PDF"


class WordExtractor(_NoImplementado):
    extensiones = (".docx",)
    nombre = "Word"


class CorreoExtractor(_NoImplementado):
    extensiones = (".msg", ".eml")
    nombre = "Correo"
