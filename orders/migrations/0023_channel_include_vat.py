# Generated by Django 3.2.6 on 2021-08-12 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0022_channel_channel_fee"),
    ]

    operations = [
        migrations.AddField(
            model_name="channel",
            name="include_vat",
            field=models.BooleanField(default=True),
        ),
    ]
