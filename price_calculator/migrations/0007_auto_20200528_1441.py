# Generated by Django 3.0.6 on 2020-05-28 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0008_auto_20200527_1504"),
        ("inventory", "0005_delete_stcadminimage"),
        ("price_calculator", "0006_auto_20200128_0952"),
    ]

    operations = [
        migrations.CreateModel(
            name="CountryChannelFee",
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
                ("min_channel_fee", models.PositiveIntegerField()),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.Country",
                    ),
                ),
            ],
            options={
                "verbose_name": "Country Channel Fee",
                "verbose_name_plural": "Country Channel Fees",
            },
        ),
        migrations.CreateModel(
            name="ProductType",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("package_types", models.ManyToManyField(to="inventory.PackageType")),
            ],
            options={
                "verbose_name": "Product Type",
                "verbose_name_plural": "Product Types",
            },
        ),
        migrations.CreateModel(
            name="ShippingMethod",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("min_weight", models.PositiveIntegerField(default=0)),
                ("max_weight", models.PositiveIntegerField(blank=True, null=True)),
                ("min_price", models.PositiveIntegerField(default=0)),
                ("max_price", models.PositiveIntegerField(blank=True, null=True)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.Country",
                    ),
                ),
                (
                    "product_type",
                    models.ManyToManyField(to="price_calculator.ProductType"),
                ),
                (
                    "shipping_service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.ShippingService",
                    ),
                ),
                (
                    "vat_rates",
                    models.ManyToManyField(blank=True, to="price_calculator.VATRate"),
                ),
            ],
            options={
                "verbose_name": "Shipping Method",
                "verbose_name_plural": "Shippng Method",
            },
        ),
        migrations.RemoveField(model_name="shippingprice", name="country",),
        migrations.RemoveField(model_name="shippingprice", name="package_type",),
        migrations.RemoveField(model_name="shippingprice", name="vat_rates",),
        migrations.DeleteModel(name="DestinationCountry",),
        migrations.DeleteModel(name="PackageType",),
        migrations.DeleteModel(name="ShippingPrice",),
    ]
