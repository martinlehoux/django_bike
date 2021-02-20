from .base import *
from .base import BASE_DIR

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
