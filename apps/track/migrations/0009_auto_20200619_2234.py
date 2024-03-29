# Generated by Django 3.0.7 on 2020-06-20 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("track", "0008_auto_20200610_2350"),
    ]

    operations = [
        migrations.RenameField(
            model_name="track",
            old_name="gpx_file",
            new_name="source_file",
        ),
        migrations.AddField(
            model_name="track",
            name="parser",
            field=models.CharField(
                choices=[("amazfit-gpx-parser", "amazfit-gpx-parser")],
                default="amazfit-gpx-parser",
                max_length=32,
            ),
            preserve_default=False,
        ),
    ]
