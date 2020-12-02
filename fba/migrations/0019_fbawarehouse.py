# Generated by Django 3.1.4 on 2020-12-02 15:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0018_remove_fbaregion_delivery_unit"),
    ]

    operations = [
        migrations.CreateModel(
            name="FBAWarehouse",
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
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="fba.fbaregion"
                    ),
                ),
            ],
            options={
                "verbose_name": "FBA Warehouse",
                "verbose_name_plural": "FBA Warehouses",
            },
        ),
    ]
