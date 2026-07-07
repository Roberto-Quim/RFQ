"""
Serializacion de la escritura al Excel (Fase 3), solo con la libreria estandar.

Combina dos niveles:
  1) threading.Lock  -> serializa entre hilos del MISMO proceso
                        (el `runserver` por defecto es monoproceso).
  2) lockfile atomico (os.open con O_CREAT|O_EXCL) -> serializa entre PROCESOS
                        distintos (por si se corre con varios workers).

Limitaciones (documentadas):
  - Es un lock cooperativo: solo protege a quien use `lock_escritura_excel()`.
    Si alguien edita PROYECTO.xlsx por fuera (ej. Excel abierto), esto no lo
    impide; para eso el motor ya da un error claro al no poder guardar.
  - Si un proceso muere dejando el lockfile, se considera "viejo" tras
    `stale_segundos` y se rompe automaticamente.
"""
import contextlib
import os
import threading
import time
from pathlib import Path

# Lock intra-proceso (compartido por todos los hilos de este proceso).
_lock_hilo = threading.Lock()


class LockOcupado(Exception):
    """Otra escritura al Excel esta en curso y no se libero a tiempo."""


def _es_lock_viejo(ruta_lock: Path, stale_segundos: float) -> bool:
    try:
        edad = time.time() - os.path.getmtime(ruta_lock)
        return edad > stale_segundos
    except FileNotFoundError:
        return False


@contextlib.contextmanager
def lock_escritura_excel(ruta_lock, timeout: float = 30.0,
                         espera: float = 0.2, stale_segundos: float = 120.0):
    """Context manager que garantiza UNA sola escritura al Excel a la vez.

    Lanza LockOcupado si no se logra adquirir dentro de `timeout` segundos.
    """
    ruta_lock = Path(ruta_lock)
    ruta_lock.parent.mkdir(parents=True, exist_ok=True)
    inicio = time.time()

    # Nivel 1: intra-proceso.
    with _lock_hilo:
        fd = None
        # Nivel 2: entre procesos, via creacion atomica del lockfile.
        while True:
            try:
                fd = os.open(str(ruta_lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                break
            except FileExistsError:
                if _es_lock_viejo(ruta_lock, stale_segundos):
                    with contextlib.suppress(FileNotFoundError):
                        os.remove(str(ruta_lock))
                    continue
                if time.time() - inicio > timeout:
                    raise LockOcupado(
                        "Otra escritura al Excel esta en curso. "
                        "Espera unos segundos y reintenta."
                    )
                time.sleep(espera)
        try:
            yield
        finally:
            if fd is not None:
                os.close(fd)
            with contextlib.suppress(FileNotFoundError):
                os.remove(str(ruta_lock))
