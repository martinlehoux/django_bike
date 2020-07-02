from __future__ import absolute_import, unicode_literals

import os
from pathlib import Path

from celery import Celery
import dotenv

dotenv.read_dotenv(Path(os.path.dirname(__file__)) / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_bike.settings")

app = Celery("django_bike")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
