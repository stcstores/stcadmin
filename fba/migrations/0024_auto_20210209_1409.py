# Generated by Django 3.1.6 on 2021-02-09 14:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0023_auto_20201217_0958"),
    ]

    operations = [
        migrations.CreateModel(
            name="FulfillmentCenter",
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
                ("address_1", models.CharField(max_length=255)),
                ("address_2", models.CharField(blank=True, max_length=255)),
                ("address_3", models.CharField(blank=True, max_length=255)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="fba.fbaregion"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="fbaorder",
            name="fulfillment_center",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="fba.fulfillmentcenter",
            ),
        ),
    ]
