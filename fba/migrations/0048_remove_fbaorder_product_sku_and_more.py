# Generated by Django 4.2.5 on 2023-09-20 13:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("fba", "0047_fbaorder_product"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fbaorder",
            name="product_SKU",
        ),
        migrations.RemoveField(
            model_name="fbaorder",
            name="product_barcode",
        ),
        migrations.RemoveField(
            model_name="fbaorder",
            name="product_image_url",
        ),
        migrations.RemoveField(
            model_name="fbaorder",
            name="product_name",
        ),
        migrations.RemoveField(
            model_name="fbaorder",
            name="product_supplier",
        ),
    ]
