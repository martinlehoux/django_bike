import re
from datetime import date

from django.db import models
from django.core.validators import RegexValidator
from martor.models import MartorField


class VersionType(models.TextChoices):
    RELEASE = "RELEASE", "Release"
    PATCH = "PATCH", "Patch"


validate_version_number = RegexValidator(
    r"^\d+.\d+(.\d+)?$", "Enter a valid version number (x.x.x)"
)


class ReleaseNote(models.Model):
    class Meta:
        ordering = ["-version_date"]

    version_type = models.CharField(
        max_length=64, choices=VersionType.choices, default=VersionType.RELEASE
    )
    version_number = models.CharField(
        max_length=64, validators=[validate_version_number],
    )
    version_date = models.DateField(default=date.today)
    description = MartorField(
        blank=True, help_text="Will be rendered with Markdown engine"
    )

    def __str__(self) -> str:
        return f"{self.version_type} {self.version_number}"

