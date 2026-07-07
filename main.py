"""
Orquestador del MVP.

Uso:
    python main.py

Flujo:
    1. Lee los archivos de entrada/.
    2. Elige el extractor segun la extension y obtiene RFQData.
    3. Hace backup del maestro.
    4. Abre PROYECTO.xlsx / hoja SEGUIMIENTO.
    5. Por cada RFQ: si existe -> actualiza; si no -> agrega al final.
    6. Guarda el maestro de forma atomica.
    7. Mueve los archivos procesados a procesados/.
    8. Genera el reporte en reportes/.
"""
import shutil
import sys

import config
from src import excel_maestro as maestro
from src.bitacora import Bitacora
from src.extractores import elegir_extractor


def listar_entrada():
    if not config.CARPETA_ENTRADA.exists():
        return []
    return sorted(p for p in config.CARPETA_ENTRADA.iterdir() if p.is_file())


def main():
    bit = Bitacora(config.CARPETA_REPORTES)

    archivos = listar_entrada()
    if not archivos:
        print(f"[i] No hay archivos en {config.CARPETA_ENTRADA}. Nada que hacer.")
        bit.finalizar()
        return

    # --- 1-2. Extraer datos de cada archivo ---
    datos = []
    archivos_ok = []
    for path in archivos:
        extractor = elegir_extractor(path)
        if extractor is None:
            bit.archivo_error(path.name, "formato no soportado")
            continue
        try:
            registros = extractor.extraer(path)
            if not registros:
                bit.archivo_error(path.name, "no se encontro RFQ en el archivo")
                continue
            datos.extend(registros)
            archivos_ok.append(path)
            bit.archivo_ok(path.name)
        except NotImplementedError as e:
            bit.archivo_error(path.name, str(e))
        except Exception as e:  # noqa: BLE001 - queremos que un archivo malo no tumbe todo
            bit.archivo_error(path.name, f"error inesperado: {e}")

    if not datos:
        print("[i] No se extrajo ningun RFQ valido.")
        bit.finalizar()
        return

    # --- 3-4. Backup y apertura del maestro ---
    try:
        ruta_backup = maestro.backup()
        bit.aviso(f"Backup creado: {ruta_backup.name}")
        wb, ws = maestro.cargar()
    except Exception as e:  # noqa: BLE001
        bit.archivo_error("PROYECTO.xlsx", f"no se pudo abrir: {e}")
        bit.finalizar()
        sys.exit(1)

    # --- 5. Agregar/actualizar ---
    for dato in datos:
        try:
            resultado = maestro.agregar_o_actualizar(ws, dato)
            if resultado == "agregado":
                bit.agregado(dato.rfq)
            else:
                bit.actualizado(dato.rfq)
            bit.faltantes(dato.rfq, dato.faltantes)
        except Exception as e:  # noqa: BLE001
            bit.archivo_error(f"RFQ {dato.rfq}", f"error al escribir: {e}")

    # --- 6. Guardar ---
    maestro.guardar(wb)

    # --- 7. Mover procesados ---
    config.CARPETA_PROCESADOS.mkdir(exist_ok=True)
    for path in archivos_ok:
        destino = config.CARPETA_PROCESADOS / path.name
        try:
            shutil.move(str(path), str(destino))
        except Exception as e:  # noqa: BLE001
            bit.aviso(f"No se pudo mover {path.name}: {e}")

    # --- 8. Reporte ---
    bit.finalizar()


if __name__ == "__main__":
    main()
