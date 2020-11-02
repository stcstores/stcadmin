# Generated by Django 3.1.2 on 2020-10-26 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0008_fbaregion_flag"),
    ]

    operations = [
        migrations.CreateModel(
            name="FBAShippingPrice",
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
                ("added", models.DateTimeField(auto_now_add=True)),
                ("product_SKU", models.CharField(max_length=20, unique=True)),
                ("price_per_item", models.PositiveIntegerField()),
            ],
            options={
                "verbose_name": "FBA Shipping Price",
                "verbose_name_plural": "FBA Shipping Prices",
            },
        ),
    ]
