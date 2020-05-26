# Generated by Django 3.0.6 on 2020-05-27 10:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0003_auto_20200218_1150"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShippingPrice",
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
                    "price_type",
                    models.CharField(
                        choices=[
                            ("fixed", "Fixed"),
                            ("weight", "Weight"),
                            ("weight_band", "Weight Band"),
                        ],
                        max_length=50,
                    ),
                ),
                ("item_price", models.IntegerField(default=0)),
                ("price_per_kg", models.IntegerField(default=0)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.Country",
                    ),
                ),
            ],
            options={
                "verbose_name": "Shipping Price",
                "verbose_name_plural": "Shipping Prices",
            },
        ),
        migrations.CreateModel(
            name="ShippingService",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Shipping Service",
                "verbose_name_plural": "Shipping Services",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="WeightBand",
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
                ("min_weight", models.IntegerField()),
                ("max_weight", models.IntegerField()),
                ("price", models.IntegerField()),
                (
                    "shipping_price",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.ShippingPrice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Weight Band",
                "verbose_name_plural": "Weight Bands",
                "ordering": ("min_weight",),
            },
        ),
        migrations.AddField(
            model_name="shippingprice",
            name="shipping_service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="shipping.ShippingService",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="shippingprice", unique_together={("shipping_service", "country")},
        ),
    ]
