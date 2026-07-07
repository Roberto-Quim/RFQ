"""
Extractor FUNCIONAL para pruebas de HOY.

Lee archivos .csv de la carpeta entrada/ con estas columnas (encabezado):
    rfq, descripcion, fecha_arranque, solicitante, planta

Sirve para probar TODO el flujo de actualizacion del maestro sin depender
todavia de los RFQ reales. Cuando los formatos reales esten definidos,
este extractor se puede conservar como "carga manual/masiva".
"""
import csv
from pathlib import Path

from src.extractores.base import Extractor
from src.extractores.utilidades import parsear_fecha, limpiar_texto
from src.modelo import RFQData


class CsvManualExtractor(Extractor):
    extensiones = (".csv",)

    def extraer(self, path: Path) -> list[RFQData]:
        resultados: list[RFQData] = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                # normaliza claves a minusculas sin espacios
                fila = {(k or "").strip().lower(): v for k, v in fila.items()}
                rfq = limpiar_texto(fila.get("rfq"))
                if not rfq:
                    continue  # sin RFQ no hay registro valido
                dato = RFQData(
                    rfq=rfq,
                    descripcion=limpiar_texto(fila.get("descripcion")),
                    fecha_arranque=parsear_fecha(fila.get("fecha_arranque")),
                    solicitante=limpiar_texto(fila.get("solicitante")),
                    planta=limpiar_texto(fila.get("planta")),
                    origen_archivo=path.name,
                )
                dato.registrar_faltantes()
                resultados.append(dato)
        return resultados
