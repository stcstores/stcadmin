# Generated by Django 4.1.1 on 2022-10-05 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0024_alter_exchangerate_unique_together"),
        ("linnworks", "0013_linnworksconfig_image_import_file_path"),
    ]

    operations = [
        migrations.CreateModel(
            name="LinnworksShippingService",
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
                ("name", models.CharField(max_length=255)),
                (
                    "shipping_service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="linnworks_shipping_services",
                        to="shipping.shippingservice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Linnworks Shipping Service",
                "verbose_name_plural": "Linnworks Shipping Services",
            },
        ),
    ]
