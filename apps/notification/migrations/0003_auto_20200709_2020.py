# Generated by Django 3.0.7 on 2020-07-10 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0002_notification_level"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="level",
            field=models.CharField(
                choices=[
                    ("is-info", "Info"),
                    ("is-success", "Success"),
                    ("is-warning", "Warning"),
                    ("is-danger", "Error"),
                ],
                default="is-info",
                max_length=64,
            ),
        ),
    ]
