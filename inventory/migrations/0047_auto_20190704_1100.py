# Generated by Django 2.2.3 on 2019-07-04 11:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("inventory", "0046_auto_20190704_1056")]

    operations = [
        migrations.AlterField(
            model_name="partialproduct",
            name="product_range",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory.PartialProductRange",
            ),
        )
    ]
