# Generated by Django 3.0.8 on 2020-09-15 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0019_like'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user', 'track'), name='like_unique'),
        ),
    ]
