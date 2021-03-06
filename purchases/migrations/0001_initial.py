# Generated by Django 3.1.7 on 2021-03-18 11:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("shipping", "0015_country_flag"),
    ]

    operations = [
        migrations.CreateModel(
            name="Purchase",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("to_pay", models.IntegerField()),
                ("paid", models.BooleanField(default=False)),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_purchases.purchase_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
        ),
        migrations.CreateModel(
            name="StockPurchase",
            fields=[
                (
                    "purchase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="purchases.purchase",
                    ),
                ),
                ("product_id", models.CharField(max_length=20)),
                ("product_sku", models.CharField(max_length=20)),
                ("product_name", models.CharField(max_length=255)),
                ("product_purchase_price", models.IntegerField()),
                ("quantity", models.IntegerField()),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("purchases.purchase",),
        ),
        migrations.CreateModel(
            name="ShippingPurchase",
            fields=[
                (
                    "purchase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="purchases.purchase",
                    ),
                ),
                (
                    "shipping_price",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.shippingprice",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("purchases.purchase",),
        ),
    ]
