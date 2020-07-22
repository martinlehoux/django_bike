import os
from pathlib import Path

import django
import dotenv
from channels.routing import get_default_application


dotenv.read_dotenv(Path(os.path.dirname(__file__)) / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_bike.settings")
django.setup()
application = get_default_application()
