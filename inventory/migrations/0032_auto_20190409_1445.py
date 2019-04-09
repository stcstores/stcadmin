# Generated by Django 2.2 on 2019-04-09 14:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("inventory", "0031_auto_20190409_1435")]

    operations = [
        migrations.RemoveField(model_name="product", name="product_options"),
        migrations.CreateModel(
            name="ProductOptionValueLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventory.Product",
                    ),
                ),
                (
                    "product_option_value",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventory.ProductOptionValue",
                    ),
                ),
            ],
            options={
                "verbose_name": "ProductRangeVariableOption",
                "verbose_name_plural": "ProductRangeVariableOptions",
                "ordering": ("product_option_value__product_option__ordering",),
                "unique_together": {("product", "product_option_value")},
            },
        ),
    ]
