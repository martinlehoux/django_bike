# Generated by Django 3.2 on 2021-04-20 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0022_auto_20210319_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='sport',
            field=models.CharField(choices=[('biking', 'Biking'), ('running', 'Running')], default='biking', max_length=32),
        ),
    ]