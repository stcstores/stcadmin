# Generated by Django 3.0.7 on 2020-06-11 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("orders", "0005_auto_20200312_1602")]

    operations = [
        migrations.AlterField(
            model_name="breakage", name="timestamp", field=models.DateTimeField()
        )
    ]
