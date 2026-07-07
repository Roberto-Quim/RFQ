"""
Contrato base para TODOS los extractores.

La idea: cada tipo de archivo (Excel, PDF, Word, correo) tendra su propia
subclase, pero todas se ven igual desde afuera:
  - puede_procesar(path) -> ¿este extractor sabe leer este archivo?
  - extraer(path)        -> devuelve una lista de RFQData (un archivo puede traer varios)

Asi, agregar soporte para un nuevo formato = escribir una subclase nueva
sin tocar el resto del sistema.
"""
from abc import ABC, abstractmethod
from pathlib import Path

from src.modelo import RFQData


class Extractor(ABC):
    # extensiones que maneja este extractor, en minusculas (ej: (".xlsx",))
    extensiones: tuple[str, ...] = ()

    def puede_procesar(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensiones

    @abstractmethod
    def extraer(self, path: Path) -> list[RFQData]:
        """Lee el archivo y devuelve 0..N RFQData. Lanza excepcion si falla."""
        raise NotImplementedError
