# Generated by Django 5.0.3 on 2024-04-08 11:40

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0061_fbaregion_placement_fee"),
        ("inventory", "0027_supplier_restock_comment"),
    ]

    operations = [
        migrations.CreateModel(
            name="FBAProfitFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("import_date", models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                "verbose_name": "FBA Profit File",
                "verbose_name_plural": "FBA Profit Files",
                "ordering": ("import_date",),
                "get_latest_by": "import_date",
            },
        ),
        migrations.CreateModel(
            name="FBAProfit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("exchange_rate", models.FloatField()),
                ("channel_sku", models.CharField(max_length=255)),
                ("asin", models.CharField(max_length=10)),
                ("listing_name", models.TextField()),
                ("sale_price", models.PositiveIntegerField()),
                ("referral_fee", models.PositiveIntegerField()),
                ("closing_fee", models.PositiveIntegerField()),
                ("handling_fee", models.PositiveIntegerField()),
                ("placement_fee", models.PositiveIntegerField()),
                ("purchase_price", models.PositiveIntegerField()),
                ("shipping_price", models.PositiveIntegerField()),
                ("profit", models.IntegerField()),
                (
                    "last_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fba_profit",
                        to="fba.fbaorder",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fba_profit",
                        to="inventory.baseproduct",
                    ),
                ),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fba_profit",
                        to="fba.fbaregion",
                    ),
                ),
                (
                    "import_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_profit",
                        to="fba.fbaprofitfile",
                    ),
                ),
            ],
            options={
                "verbose_name": "FBA Profit",
                "verbose_name_plural": "FBA Profit",
            },
        ),
    ]
