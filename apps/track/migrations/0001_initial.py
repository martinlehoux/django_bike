# Generated by Django 3.0.7 on 2020-06-10 22:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.track.models.track


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Track",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("datetime", models.DateTimeField(blank=True)),
                (
                    "gpx_file",
                    models.FileField(
                        null=True, upload_to=apps.track.models.track.source_file_path
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TrackPoint",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("lat", models.FloatField()),
                ("lon", models.FloatField()),
                ("time", models.DurationField()),
                ("alt", models.FloatField(default=0)),
                ("x", models.FloatField(default=0)),
                ("y", models.FloatField(default=0)),
                ("dist", models.FloatField(default=0)),
                (
                    "track",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="track.Track"
                    ),
                ),
            ],
        ),
    ]
