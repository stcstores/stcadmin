# Generated by Django 2.1.5 on 2019-02-12 16:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("price_calculator", "0003_auto_20190212_1548")]

    operations = [
        migrations.CreateModel(
            name="ShippingRegion",
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
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name": "Shipping Region",
                "verbose_name_plural": "Shipping Regions",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="destinationcountry",
            name="shipping_region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="price_calculator.ShippingRegion",
            ),
        ),
    ]
