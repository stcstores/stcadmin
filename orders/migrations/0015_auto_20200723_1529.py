# Generated by Django 3.0.8 on 2020-07-23 14:29

import django.db.models.deletion
from django.db import migrations, models

import orders.models.refund


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("shipping", "0014_vatrate"),
        ("inventory", "0005_delete_stcadminimage"),
        ("orders", "0014_auto_20200723_1216"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductRefund",
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
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="orders.ProductSale",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Refund",
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
                ("notes", models.TextField(blank=True)),
                ("closed", models.BooleanField(default=False)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="orders.Order"
                    ),
                ),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_orders.refund_set+",
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
        ),
        migrations.CreateModel(
            name="ContactRefund",
            fields=[
                (
                    "refund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.Refund",
                    ),
                ),
                ("contact_contacted", models.BooleanField(default=False)),
                ("refund_accepted", models.BooleanField(blank=True, null=True)),
                ("refund_amount", models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.refund",),
        ),
        migrations.CreateModel(
            name="LinkingMistakeRefund",
            fields=[
                (
                    "refund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.Refund",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.refund",),
        ),
        migrations.CreateModel(
            name="PackingMistakeRefund",
            fields=[
                (
                    "refund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.Refund",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.refund",),
        ),
        migrations.CreateModel(
            name="RefundImage",
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
                    "image",
                    models.ImageField(
                        height_field="image_height",
                        upload_to=orders.models.refund.image_path,
                        width_field="image_width",
                    ),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        height_field="thumb_height",
                        upload_to="",
                        width_field="thumb_width",
                    ),
                ),
                ("image_height", models.PositiveIntegerField()),
                ("image_width", models.PositiveIntegerField()),
                ("thumb_height", models.PositiveIntegerField()),
                ("thumb_width", models.PositiveIntegerField()),
                (
                    "product_refund",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="orders.ProductRefund",
                    ),
                ),
                (
                    "refund",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="orders.Refund"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="productrefund",
            name="refund",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="orders.Refund",
            ),
        ),
        migrations.CreateModel(
            name="CourierRefund",
            fields=[
                (
                    "contactrefund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.ContactRefund",
                    ),
                ),
                (
                    "courier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.Provider",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.contactrefund",),
        ),
        migrations.CreateModel(
            name="SupplierRefund",
            fields=[
                (
                    "contactrefund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.ContactRefund",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.Supplier",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.contactrefund",),
        ),
        migrations.CreateModel(
            name="BreakageRefund",
            fields=[
                (
                    "supplierrefund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.SupplierRefund",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.supplierrefund",),
        ),
        migrations.CreateModel(
            name="DemicRefund",
            fields=[
                (
                    "supplierrefund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.SupplierRefund",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.supplierrefund",),
        ),
        migrations.CreateModel(
            name="LostInPostRefund",
            fields=[
                (
                    "courierrefund_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="orders.CourierRefund",
                    ),
                ),
            ],
            options={"abstract": False, "base_manager_name": "objects"},
            bases=("orders.courierrefund",),
        ),
    ]
