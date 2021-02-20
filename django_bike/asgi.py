import os
from pathlib import Path

import django
import dotenv
from channels.routing import get_default_application

dotenv.read_dotenv(Path(__file__).parent / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_bike.settings.dev")
django.setup()
application = get_default_application()
