# Generated by Django 3.0 on 2019-12-19 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("orders", "0004_auto_20191219_1446")]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_ID",
            field=models.CharField(max_length=12, unique=True),
        )
    ]
