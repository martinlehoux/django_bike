# Generated by Django 3.0.8 on 2020-09-15 22:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("track", "0020_auto_20200915_1401"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="text",
            field=models.TextField(
                validators=[django.core.validators.MaxLengthValidator(200)]
            ),
        ),
    ]
