"""
Lanzador de la app con Waitress (servidor WSGI para Windows) - Fase 4.

Uso:
    python run_waitress.py

Lee host/puerto desde variables de entorno (o .env):
    RFQ_WAITRESS_HOST  (default 127.0.0.1)  -> usa 0.0.0.0 para exponer en la LAN
    RFQ_WAITRESS_PORT  (default 8000)

Antes de usar en modo interno: DJANGO_DEBUG=0, DJANGO_SECRET_KEY definida,
ALLOWED_HOSTS correcto y `python manage.py collectstatic`.

get_application() se puede importar SIN arrancar el servidor (para pruebas).
"""
import os


def get_application():
    """Devuelve la app WSGI de Django (sin arrancar el servidor)."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rfq_project.settings")
    from rfq_project.wsgi import application
    return application


def main():
    from waitress import serve

    host = os.environ.get("RFQ_WAITRESS_HOST", "127.0.0.1")
    port = int(os.environ.get("RFQ_WAITRESS_PORT", "8000"))
    app = get_application()
    print(f"Sirviendo RFQ en http://{host}:{port}  (Ctrl+C para detener)")
    if host == "0.0.0.0":
        print("AVISO: 0.0.0.0 expone el servicio a la red local. "
              "Confirma ALLOWED_HOSTS y firewall.")
    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
