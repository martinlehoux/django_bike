# Generated by Django 3.0.8 on 2020-09-06 19:11

import apps.account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20200719_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='default-avatar.png', upload_to=apps.account.models.upload_avatar_to),
        ),
    ]