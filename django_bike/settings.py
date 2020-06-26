import os

from django.urls import reverse_lazy
from django.contrib.messages import constants as messages

# ENV VARIABLES
SECRET_KEY = os.environ.get("SECRET_KEY")
SERVER_TYPE = os.environ.get("SERVER_TYPE", "dev")
JAWG_TOKEN = os.environ.get("JAWG_TOKEN")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(";")

assert SERVER_TYPE in ["dev", "test", "stage", "prod"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = SERVER_TYPE in ["dev"]
DOCKER = SERVER_TYPE in ["prod", "stage"]
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    "apps.account",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "apps.track",
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

ROOT_URLCONF = "django_bike.urls"

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_bike.wsgi.application"

if SERVER_TYPE in ["dev", "test"]:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "django_bike",
            "USER": "django_bike",
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
            "HOST": "db",
            "PORT": "5432",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
if DEBUG:
    STATICFILES_DIRS = ["static"]
else:
    STATIC_ROOT = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = "media/"

if DOCKER:
    CELERY_BROKER_URL = "redis://redis:6379"
else:
    CELERY_BROKER_URL = "redis://localhost:6379"

LOGOUT_REDIRECT_URL = reverse_lazy("track:list")
LOGIN_REDIRECT_URL = reverse_lazy("track:list")

MESSAGE_TAGS = {
    messages.DEBUG: "primary",
    messages.ERROR: "danger",
}

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

SERVER_EMAIL = "martin@lehoux.net"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, "mail")

if DOCKER:
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = os.environ.get("SENDGRID_KEY")

ADMINS = [("Martin Lehoux", "martin@lehoux.net")]
