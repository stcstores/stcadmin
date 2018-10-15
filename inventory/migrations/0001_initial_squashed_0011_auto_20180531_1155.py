# Generated by Django 2.0.7 on 2018-07-31 12:42

import django.db.models.deletion
import inventory.models.stcadmin_image
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("inventory", "0001_initial"),
        ("inventory", "0002_barcode"),
        ("inventory", "0003_auto_20171220_1402"),
        ("inventory", "0004_auto_20171221_1143"),
        ("inventory", "0005_auto_20171221_1346"),
        ("inventory", "0006_auto_20180104_1053"),
        ("inventory", "0007_auto_20180227_1604"),
        ("inventory", "0008_auto_20180227_1626"),
        ("inventory", "0009_warehouse_abriviation"),
        ("inventory", "0010_auto_20180514_0933"),
        ("inventory", "0011_auto_20180531_1155"),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="STCAdminImage",
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
                ("range_id", models.CharField(max_length=10)),
                (
                    "image",
                    models.ImageField(
                        upload_to=inventory.models.stcadmin_image.get_product_image_upload_to
                    ),
                ),
            ],
            options={
                "verbose_name": "STC Admin Image",
                "verbose_name_plural": "STC Admin Images",
            },
        ),
        migrations.CreateModel(
            name="Barcode",
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
                ("barcode", models.CharField(max_length=13, unique=True)),
                ("used", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "Barcode", "verbose_name_plural": "Barcodes"},
        ),
        migrations.CreateModel(
            name="Bay",
            fields=[
                (
                    "bay_id",
                    models.PositiveIntegerField(primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Warehouse",
            fields=[
                (
                    "warehouse_id",
                    models.PositiveIntegerField(primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("abriviation", models.CharField(blank=True, max_length=4, null=True)),
            ],
            options={
                "verbose_name": "Warehouse",
                "verbose_name_plural": "Warehouses",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="bay",
            name="warehouse",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="inventory.Warehouse"
            ),
        ),
        migrations.AlterField(
            model_name="bay",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterModelOptions(
            name="bay", options={"verbose_name": "Bay", "verbose_name_plural": "Bays"}
        ),
    ]
