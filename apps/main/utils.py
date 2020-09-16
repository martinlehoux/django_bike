import shutil
from pathlib import Path
from typing import List

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


class TestMixin:
    def assertIsClose(self, a: float, b: float, rel_tol=0.05, msg: str = ""):
        diff = abs(a - b) / max(abs(a), abs(b))
        if not diff <= rel_tol:
            raise AssertionError(
                f"{a:.3f} and {b:.3f} are not close ({diff:.3%}): {msg}"
            )
        return True


def smoother(array: List[float], smooth_size: int = 30) -> List[float]:
    new_array = []
    for i in range(len(array)):
        start = max(i - smooth_size, 0)
        end = min(i + smooth_size, len(array))
        new_array.append(sum(array[start:end]) / len(array[start:end]))
    return new_array
