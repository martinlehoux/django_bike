from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import validate_version_number


class ReleaseNoteTestCase(TestCase):
    def test_validate_version_number(self):
        validate_version_number("0.1")
        validate_version_number("0.1.1")
        validate_version_number("3.1")
        with self.assertRaises(ValidationError):
            validate_version_number("a")
        with self.assertRaises(ValidationError):
            validate_version_number("0")
