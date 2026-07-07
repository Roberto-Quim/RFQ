"""
Modelo de datos comun. TODOS los extractores devuelven objetos RFQData,
sin importar si el origen fue Excel, PDF, Word o correo. Asi el resto del
sistema (escritura al maestro, bitacora) no depende del formato de origen.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class RFQData:
    rfq: str                                   # SIEMPRE texto: "185", "131/4", "185.5"
    descripcion: Optional[str] = None
    fecha_arranque: Optional[date] = None      # fecha real, no texto
    solicitante: Optional[str] = None
    planta: Optional[str] = None

    origen_archivo: str = ""                    # nombre del archivo de donde salio
    faltantes: list = field(default_factory=list)  # nombres de campos no encontrados

    def registrar_faltantes(self):
        """Detecta que campos vinieron vacios y los anota."""
        self.faltantes = [
            campo
            for campo in ("descripcion", "fecha_arranque", "solicitante", "planta")
            if getattr(self, campo) in (None, "")
        ]
        return self.faltantes
