"""
Importacion por lote de RFQ desde una carpeta controlada (Fase 6).

    python manage.py importar_rfq_lote --carpeta C:\\ruta\\rfq_entrada
    python manage.py importar_rfq_lote --carpeta C:\\ruta\\rfq_entrada --confirmar

SEGURIDAD (modo seguro por defecto):
  - Sin --confirmar, corre en DRY-RUN: solo LEE y reporta, NO escribe al Excel.
  - Con --confirmar, escribe usando el MISMO flujo seguro que la web
    (backup + lock via seguimiento.services.escribir_confirmado).
  - No mueve ni borra los archivos de origen.
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

# Motor (dispatcher de extractores) + servicio seguro de escritura.
from src.extractores import elegir_extractor
from seguimiento.services import MotorError, escribir_confirmado


class Command(BaseCommand):
    help = "Importa RFQ desde una carpeta. Dry-run por defecto (no escribe al Excel)."

    def add_arguments(self, parser):
        parser.add_argument("--carpeta", required=True,
                            help="Carpeta con archivos RFQ a procesar.")
        parser.add_argument("--confirmar", action="store_true",
                            help="Escribe al Excel. Sin este flag es dry-run (no escribe).")

    def handle(self, *args, **options):
        carpeta = Path(options["carpeta"])
        confirmar = options["confirmar"]
        if not carpeta.is_dir():
            raise CommandError(f"La carpeta no existe: {carpeta}")

        archivos = sorted(p for p in carpeta.iterdir()
                          if p.is_file() and not p.name.startswith("."))
        if not archivos:
            self.stdout.write("No hay archivos para procesar.")
            return

        modo = "ESCRITURA (--confirmar)" if confirmar else "DRY-RUN (no escribe)"
        self.stdout.write(self.style.WARNING(f"Modo: {modo}"))
        self.stdout.write(f"Carpeta: {carpeta}\n")

        n_ok = n_error = n_escritos = 0
        for path in archivos:
            extractor = elegir_extractor(path)
            if extractor is None:
                self.stdout.write(self.style.ERROR(
                    f"[X] {path.name}: formato no soportado"))
                n_error += 1
                continue
            try:
                registros = extractor.extraer(path)
            except NotImplementedError as e:
                self.stdout.write(self.style.WARNING(f"[~] {path.name}: {e}"))
                n_error += 1
                continue
            except Exception as e:  # noqa: BLE001
                self.stdout.write(self.style.ERROR(f"[X] {path.name}: error: {e}"))
                n_error += 1
                continue

            if not registros:
                self.stdout.write(self.style.WARNING(
                    f"[~] {path.name}: no se encontro RFQ"))
                n_error += 1
                continue

            for dato in registros:
                faltan = ", ".join(dato.faltantes) or "ninguno"
                self.stdout.write(
                    f"[OK] {path.name} -> RFQ {dato.rfq} "
                    f"({extractor.__class__.__name__}) faltantes: {faltan}")
                n_ok += 1

                if confirmar:
                    try:
                        resumen = escribir_confirmado(dato)
                        self.stdout.write(self.style.SUCCESS(
                            f"     escrito: {resumen['accion']} (backup {resumen['backup']})"))
                        n_escritos += 1
                    except MotorError as e:
                        self.stdout.write(self.style.ERROR(f"     no escrito: {e}"))
                        n_error += 1

        # Resumen
        self.stdout.write("\n--- Resumen ---")
        self.stdout.write(f"RFQ leidos: {n_ok} | errores/omitidos: {n_error}")
        if confirmar:
            self.stdout.write(f"Escritos al Excel: {n_escritos}")
        else:
            self.stdout.write(self.style.WARNING(
                "DRY-RUN: no se escribio nada. Usa --confirmar para aplicar."))
