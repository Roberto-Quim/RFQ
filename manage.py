#!/usr/bin/env python
"""Utilidad de linea de comandos de Django para el proyecto RFQ (Fase 2)."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rfq_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Instala dependencias con "
            "'pip install -r requirements.txt' y activa tu entorno virtual."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
