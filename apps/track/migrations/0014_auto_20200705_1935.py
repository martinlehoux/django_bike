# Generated by Django 3.0.7 on 2020-07-06 02:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0013_auto_20200705_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackstat',
            name='duration',
            field=models.DurationField(blank=True, default=datetime.timedelta(0)),
        ),
    ]
