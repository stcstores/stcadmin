# Generated by Django 3.1.8 on 2021-04-22 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchase",
            name="cancelled",
            field=models.BooleanField(default=False),
        ),
    ]
