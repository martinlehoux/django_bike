from __future__ import absolute_import, unicode_literals

import os
from pathlib import Path

import dotenv

from celery import Celery

dotenv.read_dotenv(Path(__file__).parent / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_bike.settings.dev")

app = Celery("django_bike")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
