# Generated by Django 3.0.7 on 2020-06-10 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0003_track_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]