"""
Settings de Django para el proyecto RFQ (Fase 2).

Fase 2 envuelve el motor local (Fase 1) que vive en config.py y src/.
Se agrega BASE_DIR al sys.path para que Django pueda importar el motor
(`import config`, `from src ...`) igual que la CLI.
"""
import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Permitir importar el motor de Fase 1 (config.py y src/ en la raiz del repo).
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# --- Cargador minimo de .env (sin dependencias externas) ---
def _cargar_dotenv(ruta: Path):
    """Lee un .env local (KEY=VALUE) y lo vuelca a os.environ si no esta ya.

    Ignora comentarios y lineas vacias. No sobrescribe variables que ya
    existan en el entorno del sistema (estas tienen prioridad).
    """
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


_cargar_dotenv(BASE_DIR / ".env")

# --- Seguridad ---
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# SECRET_KEY: en DEBUG se permite una clave de desarrollo; en produccion
# (DEBUG=False) es OBLIGATORIO definir DJANGO_SECRET_KEY.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-inseguro-solo-local-cambiar-en-produccion"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY es obligatoria cuando DEBUG=False. "
            "Definela como variable de entorno o en .env."
        )

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "seguimiento",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rfq_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "rfq_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# Archivos subidos por los usuarios (RFQ .txt). Carpeta IGNORADA por Git.
MEDIA_URL = "media/"
MEDIA_ROOT = Path(os.environ.get("RFQ_MEDIA_ROOT", BASE_DIR / "media"))

# Limites de subida (defensa basica contra archivos enormes).
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024   # 2 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024   # 2 MB

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Autenticacion ---
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "subir_rfq"
LOGOUT_REDIRECT_URL = "login"

# --- Logging (a carpeta IGNORADA por Git) ---
LOGS_DIR = Path(os.environ.get("RFQ_LOGS_DIR", BASE_DIR / "logs"))
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detallado": {
            "format": "{asctime} {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "archivo": {
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "rfq.log"),
            "formatter": "detallado",
            "encoding": "utf-8",
        },
        "consola": {"class": "logging.StreamHandler", "formatter": "detallado"},
    },
    "loggers": {
        "seguimiento": {
            "handlers": ["archivo", "consola"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
