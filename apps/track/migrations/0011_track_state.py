# Generated by Django 3.0.7 on 2020-06-21 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0010_move_gpx_to_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='state',
            field=models.CharField(choices=[('processing', 'Processing'), ('ready', 'Ready')], default='ready', max_length=32),
        ),
    ]