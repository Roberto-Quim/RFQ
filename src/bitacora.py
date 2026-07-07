"""
Bitacora / reporte de cada corrida.

Acumula lo que va pasando y al final:
  - imprime un resumen en consola,
  - guarda un reporte .txt con fecha/hora en la carpeta reportes/.
"""
from datetime import datetime
from pathlib import Path


class Bitacora:
    def __init__(self, carpeta_reportes: Path):
        self.carpeta = carpeta_reportes
        self.inicio = datetime.now()
        self.archivos_procesados: list[str] = []
        self.archivos_con_error: list[tuple[str, str]] = []  # (archivo, motivo)
        self.rfq_agregados: list[str] = []
        self.rfq_actualizados: list[str] = []
        self.campos_faltantes: list[tuple[str, list]] = []   # (rfq, [campos])
        self.avisos: list[str] = []

    # --- registro de eventos ---
    def archivo_ok(self, nombre: str):
        self.archivos_procesados.append(nombre)

    def archivo_error(self, nombre: str, motivo: str):
        self.archivos_con_error.append((nombre, motivo))

    def agregado(self, rfq: str):
        self.rfq_agregados.append(rfq)

    def actualizado(self, rfq: str):
        self.rfq_actualizados.append(rfq)

    def faltantes(self, rfq: str, campos: list):
        if campos:
            self.campos_faltantes.append((rfq, campos))

    def aviso(self, texto: str):
        self.avisos.append(texto)

    # --- salida ---
    def _texto(self) -> str:
        L = []
        L.append("=" * 60)
        L.append(f"BITACORA DE CORRIDA - {self.inicio:%Y-%m-%d %H:%M:%S}")
        L.append("=" * 60)
        L.append(f"Archivos procesados : {len(self.archivos_procesados)}")
        for a in self.archivos_procesados:
            L.append(f"    OK  {a}")
        L.append(f"RFQ agregados       : {len(self.rfq_agregados)}")
        for r in self.rfq_agregados:
            L.append(f"    +   {r}")
        L.append(f"RFQ actualizados    : {len(self.rfq_actualizados)}")
        for r in self.rfq_actualizados:
            L.append(f"    ~   {r}")
        L.append(f"Errores             : {len(self.archivos_con_error)}")
        for a, m in self.archivos_con_error:
            L.append(f"    ERR {a}: {m}")
        L.append(f"RFQ con campos faltantes: {len(self.campos_faltantes)}")
        for r, campos in self.campos_faltantes:
            L.append(f"    ?   {r}: faltan {', '.join(campos)}")
        if self.avisos:
            L.append("Avisos:")
            for a in self.avisos:
                L.append(f"    !   {a}")
        L.append("=" * 60)
        return "\n".join(L)

    def finalizar(self) -> Path:
        texto = self._texto()
        print("\n" + texto)
        self.carpeta.mkdir(exist_ok=True)
        nombre = f"reporte_{self.inicio:%Y%m%d_%H%M%S}.txt"
        destino = self.carpeta / nombre
        destino.write_text(texto, encoding="utf-8")
        print(f"\n[i] Reporte guardado en: {destino}")
        return destino
