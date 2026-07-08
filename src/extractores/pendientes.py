"""
Extractores PLACEHOLDER para .msg, PDF y Word (Fase 6: mejorados).

Aun NO implementados a nivel de extraccion real: dejan el sistema preparado
para recibirlos sin cambiar el resto del codigo, y dan mensajes claros segun el
caso. Cuando haya archivos de ejemplo reales y se apruebe la dependencia, se
implementa extraer() y se agrega la libreria a requirements.txt.

Dependencias propuestas (NO instaladas todavia):
  - .msg  -> extract-msg   (formato binario de Outlook)
  - .pdf  -> pdfplumber    (PDF con capa de texto; los escaneados requieren OCR)
  - .docx -> python-docx   (estructura variable entre plantillas)
"""
import importlib.util
from pathlib import Path

from src.extractores.base import Extractor
from src.modelo import RFQData


def _dependencia_disponible(modulo: str) -> bool:
    """True si la libreria esta instalada (sin importarla)."""
    return importlib.util.find_spec(modulo) is not None


class _PlaceholderExtractor(Extractor):
    """Base de placeholders: mensaje claro segun dependencia y ejemplo real."""
    nombre = "generico"
    dependencia = ""   # modulo Python que haria falta

    def extraer(self, path: Path) -> list[RFQData]:
        if self.dependencia and not _dependencia_disponible(self.dependencia):
            raise NotImplementedError(
                f"[{self.nombre}] Dependencia no instalada: se requiere "
                f"'{self.dependencia}' para leer {path.name}. Formato soportado "
                f"parcialmente (aun no implementado)."
            )
        raise NotImplementedError(
            f"[{self.nombre}] Formato soportado parcialmente: falta implementar "
            f"la extraccion para {path.name}. Se requiere un archivo de ejemplo "
            f"real para definir el mapeo."
        )


class MsgExtractor(_PlaceholderExtractor):
    extensiones = (".msg",)
    nombre = "Outlook .msg"
    dependencia = "extract_msg"


class PdfExtractor(_PlaceholderExtractor):
    extensiones = (".pdf",)
    nombre = "PDF"
    dependencia = "pdfplumber"


class WordExtractor(_PlaceholderExtractor):
    extensiones = (".docx",)
    nombre = "Word"
    dependencia = "docx"
