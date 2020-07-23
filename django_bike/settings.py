import os

from django.urls import reverse_lazy
from django.contrib.messages import constants as messages

# ENV VARIABLES
SECRET_KEY = os.environ.get("SECRET_KEY")
SERVER_TYPE = os.environ.get("SERVER_TYPE", "dev")
JAWG_TOKEN = os.environ.get("JAWG_TOKEN")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(";")
TRACK_CHARTS_DISPLAY = bool(os.environ.get("TRACK_CHARTS_DISPLAY", True))

assert SERVER_TYPE in ["dev", "test", "stage", "prod"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = SERVER_TYPE in ["dev"]
DOCKER = SERVER_TYPE in ["prod", "stage"]
INTERNAL_IPS = ["127.0.0.1"]
REDIS_HOSTNAME = "redis" if DOCKER else "localhost"

INSTALLED_APPS = [
    "apps.main.apps.MainConfig",
    "apps.account.apps.AccountConfig",
    "apps.track.apps.TrackConfig",
    "apps.notification.apps.NotificationConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "django_cleanup.apps.CleanupConfig",
    "rules.apps.AutodiscoverRulesConfig",
    "channels",
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
        "DIRS": [],
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
ASGI_APPLICATION = "django_bike.routing.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(REDIS_HOSTNAME, 6379)]},
    },
}

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
STATIC_ROOT = "static/"
STATICFILES_DIRS = ["webapp/public/build"]
MEDIA_URL = "/media/"
MEDIA_ROOT = "media/"

CELERY_BROKER_URL = f"redis://{REDIS_HOSTNAME}:6379/0"

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
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 25

if DOCKER:
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = os.environ.get("SENDGRID_KEY")

ADMINS = [("Martin Lehoux", "martin@lehoux.net")]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        "simple": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}][{name}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["mail_admins", "console"], "level": "INFO"},
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "django.channels.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {"level": "INFO", "handlers": ["console"]},
    },
}

AUTHENTICATION_BACKENDS = (
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
)

if SERVER_TYPE == "test":
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOSTNAME}:6379/1",
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "KEY_PREFIX": "django_bike.cache",
        }
    }

AVATAR_SIZE = (128, 128)
