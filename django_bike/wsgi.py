"""
WSGI config for django_bike project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

import dotenv
from django.core.wsgi import get_wsgi_application

dotenv.read_dotenv(Path(__file__).parent / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_bike.settings.dev")

application = get_wsgi_application()
