# Generated by Django 3.0.8 on 2020-09-06 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("track", "0017_auto_20200906_1222"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="datetime",
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=False,
        ),
    ]
