# Generated by Django 3.1.2 on 2020-10-21 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0004_auto_20201021_1407"),
    ]

    operations = [
        migrations.AddField(
            model_name="fbaorder",
            name="small_and_light",
            field=models.BooleanField(default=False),
        ),
    ]
