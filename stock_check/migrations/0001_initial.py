# Generated by Django 2.0 on 2018-01-04 10:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bay",
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
                    "bay_id",
                    models.PositiveIntegerField(
                        db_index=True, unique=True, verbose_name="Bay ID"
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
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
                    "range_id",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Range ID"
                    ),
                ),
                (
                    "product_id",
                    models.PositiveIntegerField(
                        blank=True,
                        db_index=True,
                        null=True,
                        unique=True,
                        verbose_name="Product ID",
                    ),
                ),
                ("sku", models.CharField(db_index=True, max_length=50, unique=True)),
                ("bays", models.ManyToManyField(to="stock_check.Bay")),
            ],
        ),
        migrations.CreateModel(
            name="Warehouse",
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
                    "warehouse_id",
                    models.PositiveIntegerField(
                        db_index=True, unique=True, verbose_name="Warehouse ID"
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name="bay",
            name="warehouse",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stock_check.Warehouse"
            ),
        ),
    ]
