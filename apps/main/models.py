from datetime import date

from django.db import models
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from martor.models import MartorField

from .utils import send_mail_template

User = get_user_model()


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


@receiver(models.signals.post_save, sender=ReleaseNote)
def notification_post_save(sender, instance, created, *args, **kwargs):
    if created:
        mail_addresses = list(
            User.objects.filter(is_active=True).values_list("email", flat=True)
        )
        send_mail_template(
            "Django Bike: New version released",
            "new_version",
            from_email=None,
            recipient_list=mail_addresses,
            context={"release_note": instance},
        )
