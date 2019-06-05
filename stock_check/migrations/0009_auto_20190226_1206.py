# Generated by Django 2.1.7 on 2019-02-26 12:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0012_re_add_bay_FK"),
        ("stock_check", "0008_auto_20190226_1200"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="bays",
            field=models.ManyToManyField(
                through="stock_check.ProductBay", to="inventory.Bay"
            ),
        ),
        migrations.AddField(
            model_name="productbay",
            name="bay",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="inventory.Bay"
            ),
            preserve_default=False,
        ),
    ]