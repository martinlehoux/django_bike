# Generated by Django 3.0.7 on 2020-06-10 22:42

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("track", "0002_auto_20200610_2230"),
    ]

    operations = [
        migrations.AddField(
            model_name="track",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
