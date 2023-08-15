# Generated by Django 4.2.4 on 2023-08-15 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("inventory", "0001_initial_squashed_0009_delete_productimage"),
        ("shipping", "0001_squashed_0021_region_flag_if_not_delivered_by_days"),
    ]

    operations = [
        migrations.CreateModel(
            name="VATRate",
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
                ("name", models.CharField(max_length=50)),
                ("cc_id", models.PositiveSmallIntegerField()),
                ("percentage", models.PositiveSmallIntegerField()),
                ("ordering", models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                "verbose_name": "VAT Rate",
                "verbose_name_plural": "VAT Rates",
                "ordering": ("ordering",),
            },
        ),
        migrations.CreateModel(
            name="ChannelFee",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("fee_percentage", models.FloatField()),
                ("ordering", models.PositiveSmallIntegerField(default=100)),
                (
                    "country",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="channel_fees",
                        to="shipping.country",
                    ),
                ),
            ],
            options={
                "verbose_name": "Channel Fee",
                "verbose_name_plural": "Channel Fees",
                "ordering": ("ordering",),
            },
        ),
        migrations.CreateModel(
            name="ProductType",
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
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "package_types",
                    models.ManyToManyField(blank=True, to="inventory.packagetype"),
                ),
            ],
            options={
                "verbose_name": "Product Type",
                "verbose_name_plural": "Product Types",
            },
        ),
        migrations.CreateModel(
            name="Channel",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("ordering", models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                "verbose_name": "Channel",
                "verbose_name_plural": "Channel",
                "ordering": ("ordering",),
            },
        ),
        migrations.CreateModel(
            name="CountryChannelFee",
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
                ("min_channel_fee", models.PositiveIntegerField()),
                (
                    "country",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.country",
                    ),
                ),
            ],
            options={
                "verbose_name": "Country Channel Fee",
                "verbose_name_plural": "Country Channel Fees",
            },
        ),
        migrations.CreateModel(
            name="ShippingMethod",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("min_weight", models.PositiveIntegerField(default=0)),
                ("max_weight", models.PositiveIntegerField(blank=True, null=True)),
                ("min_price", models.PositiveIntegerField(default=0)),
                ("max_price", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.country",
                    ),
                ),
                (
                    "product_type",
                    models.ManyToManyField(to="price_calculator.producttype"),
                ),
                (
                    "shipping_service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.shippingservice",
                    ),
                ),
                (
                    "vat_rates",
                    models.ManyToManyField(blank=True, to="price_calculator.vatrate"),
                ),
                (
                    "channel",
                    models.ManyToManyField(blank=True, to="price_calculator.channel"),
                ),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Shipping Method",
                "verbose_name_plural": "Shippng Method",
            },
        ),
    ]
