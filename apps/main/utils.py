import shutil
from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings


@override_settings(MEDIA_ROOT="media-test/")
class FileSystemTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        (Path(settings.BASE_DIR) / "media-test").mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(Path(settings.BASE_DIR) / "media-test")
