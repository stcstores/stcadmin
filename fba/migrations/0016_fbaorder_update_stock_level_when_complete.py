# Generated by Django 3.1.3 on 2020-11-19 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0015_fbaorder_product_supplier"),
    ]

    operations = [
        migrations.AddField(
            model_name="fbaorder",
            name="update_stock_level_when_complete",
            field=models.BooleanField(default=True),
        ),
    ]