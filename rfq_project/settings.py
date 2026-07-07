"""
Settings de Django para el proyecto RFQ (Fase 2).

Fase 2 envuelve el motor local (Fase 1) que vive en config.py y src/.
Se agrega BASE_DIR al sys.path para que Django pueda importar el motor
(`import config`, `from src ...`) igual que la CLI.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Permitir importar el motor de Fase 1 (config.py y src/ en la raiz del repo).
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# --- Seguridad (valores de DESARROLLO; en produccion usar variables de entorno) ---
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "dev-inseguro-solo-local-cambiar-en-produccion"
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"
).split(",")

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
MEDIA_ROOT = BASE_DIR / "media"

# Limites de subida (defensa basica contra archivos enormes).
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024   # 2 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024   # 2 MB

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Autenticacion ---
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "subir_rfq"
LOGOUT_REDIRECT_URL = "login"
