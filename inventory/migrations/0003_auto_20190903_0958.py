# Generated by Django 2.2.5 on 2019-09-03 09:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("inventory", "0002_auto_20190812_1405")]

    operations = [
        migrations.AlterField(
            model_name="productedit",
            name="product_range",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory.ProductRange",
            ),
        )
    ]
