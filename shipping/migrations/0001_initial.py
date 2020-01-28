# Generated by Django 3.0.2 on 2020-01-28 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Currency",
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
                ("code", models.CharField(max_length=5, unique=True)),
                ("exchange_rate", models.DecimalField(decimal_places=3, max_digits=6)),
                ("symbol", models.CharField(default="$", max_length=5)),
            ],
            options={"verbose_name": "Currency", "verbose_name_plural": "Currencies"},
        ),
        migrations.CreateModel(
            name="Provider",
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
            options={"verbose_name": "Provider", "verbose_name_plural": "Providers"},
        ),
        migrations.CreateModel(
            name="Service",
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
                ("name", models.CharField(max_length=255)),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.Provider",
                    ),
                ),
            ],
            options={
                "verbose_name": "Service",
                "verbose_name_plural": "Services",
                "unique_together": {("name", "provider")},
            },
        ),
        migrations.CreateModel(
            name="ShippingRule",
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
                ("rule_ID", models.CharField(max_length=10, unique=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("priority", models.BooleanField(default=False)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.Service",
                    ),
                ),
            ],
            options={
                "verbose_name": "Shipping Rule",
                "verbose_name_plural": "Shipping Rules",
            },
        ),
        migrations.CreateModel(
            name="Country",
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
                ("country_ID", models.CharField(max_length=10, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("ISO_code", models.CharField(blank=True, max_length=2, null=True)),
                (
                    "region",
                    models.CharField(
                        choices=[
                            ("EU", "Europe"),
                            ("UK", "UK"),
                            ("ROW", "Rest of World"),
                        ],
                        max_length=3,
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="shipping.Currency",
                    ),
                ),
            ],
            options={
                "verbose_name": "Country",
                "verbose_name_plural": "Countries",
                "ordering": ("country_ID",),
            },
        ),
    ]
