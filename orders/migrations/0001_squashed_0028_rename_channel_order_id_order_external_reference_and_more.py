# Generated by Django 4.2.4 on 2023-08-15 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("shipping", "0001_squashed_0021_region_flag_if_not_delivered_by_days"),
        ("home", "0002_cloudcommerceuser"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("inventory", "0001_initial_squashed_0009_delete_productimage"),
        ("inventory", "0003_productimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="Channel",
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
                ("name", models.CharField(db_index=True, max_length=255, unique=True)),
                ("channel_fee", models.FloatField(default=15.5)),
                ("include_vat", models.BooleanField(default=True)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Channel",
                "verbose_name_plural": "Channels",
            },
        ),
        migrations.CreateModel(
            name="Order",
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
                (
                    "order_id",
                    models.CharField(db_index=True, max_length=12, unique=True),
                ),
                ("recieved_at", models.DateTimeField()),
                ("dispatched_at", models.DateTimeField(blank=True, null=True)),
                ("cancelled", models.BooleanField(default=False)),
                (
                    "external_reference",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "tracking_number",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"active": True},
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="orders.channel",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.country",
                    ),
                ),
                ("ignored", models.BooleanField(default=False)),
                ("priority", models.BooleanField(default=False)),
                ("total_paid", models.PositiveIntegerField(blank=True, null=True)),
                ("total_paid_GBP", models.PositiveIntegerField(blank=True, null=True)),
                ("postage_price", models.PositiveIntegerField(blank=True, null=True)),
                ("postage_price_success", models.BooleanField(blank=True, null=True)),
                (
                    "shipping_service",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"active": True},
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.shippingservice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Order",
                "verbose_name_plural": "Orders",
            },
        ),
        migrations.CreateModel(
            name="OrderUpdate",
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
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Complete", "Complete"),
                            ("In Progress", "In Progress"),
                            ("Error", "Error"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="In Progress",
                        max_length=25,
                    ),
                ),
            ],
            options={
                "verbose_name": "Order Update",
                "verbose_name_plural": "Order Updates",
            },
        ),
        migrations.CreateModel(
            name="PackingRecord",
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
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="orders.order"
                    ),
                ),
                (
                    "packed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="home.cloudcommerceuser",
                    ),
                ),
            ],
            options={
                "verbose_name": "Packing Record",
                "verbose_name_plural": "Packing Records",
            },
        ),
        migrations.CreateModel(
            name="Breakage",
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
                ("product_sku", models.CharField(max_length=20)),
                ("order_id", models.CharField(max_length=10)),
                ("note", models.TextField(blank=True, null=True)),
                ("timestamp", models.DateTimeField()),
                (
                    "packer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="home.cloudcommerceuser",
                    ),
                ),
            ],
            options={
                "verbose_name": "Breakage",
                "verbose_name_plural": "Breakages",
                "ordering": ("timestamp",),
            },
        ),
        migrations.CreateModel(
            name="OrderDetailsUpdate",
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
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Complete", "Complete"),
                            ("In Progress", "In Progress"),
                            ("Error", "Error"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="In Progress",
                        max_length=25,
                    ),
                ),
            ],
            options={
                "verbose_name": "Order Details Update",
                "verbose_name_plural": "Order Details Updates",
            },
        ),
        migrations.CreateModel(
            name="ProductSale",
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
                ("quantity", models.PositiveSmallIntegerField()),
                ("price", models.PositiveIntegerField()),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="orders.order"
                    ),
                ),
                ("name", models.TextField(null=True)),
                ("sku", models.CharField(max_length=25, null=True)),
                ("weight", models.PositiveIntegerField(null=True)),
                ("purchase_price", models.PositiveIntegerField(blank=True, null=True)),
                ("vat", models.PositiveSmallIntegerField(blank=True, null=True)),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.supplier",
                    ),
                ),
                ("channel_sku", models.CharField(max_length=25, null=True)),
            ],
            options={
                "verbose_name": "Product Sale",
                "verbose_name_plural": "Product Sales",
                "unique_together": {("order", "sku")},
            },
        ),
        migrations.CreateModel(
            name="OrderDetailsUpdateError",
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
                ("text", models.TextField()),
            ],
            options={
                "verbose_name": "Order Details Update Error",
                "verbose_name_plural": "Order Details Update Errors",
            },
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
                ("contact_contacted", models.BooleanField(default=False)),
                ("refund_accepted", models.BooleanField(blank=True, null=True)),
                ("refund_amount", models.PositiveIntegerField(blank=True, null=True)),
                ("closed", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
        ),
        migrations.CreateModel(
            name="RefundIn",
            fields=[],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("orders.refund",),
        ),
        migrations.CreateModel(
            name="RefundOut",
            fields=[],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        upload_to="",
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
            ],
        ),
        migrations.DeleteModel(
            name="Refund",
        ),
        migrations.DeleteModel(
            name="RefundImage",
        ),
        migrations.DeleteModel(
            name="RefundIn",
        ),
        migrations.DeleteModel(
            name="RefundOut",
        ),
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
                        to="orders.productsale",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Refund",
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
                ("notes", models.TextField(blank=True)),
                ("closed", models.BooleanField(default=False)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="orders.order"
                    ),
                ),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_partial", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        to="orders.refund",
                    ),
                ),
                ("contact_contacted", models.BooleanField(default=False)),
                ("refund_accepted", models.BooleanField(blank=True, null=True)),
                ("refund_amount", models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        to="orders.refund",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        to="orders.refund",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("orders.refund",),
        ),
        migrations.CreateModel(
            name="RefundImage",
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
                (
                    "image",
                    models.ImageField(
                        height_field="image_height",
                        upload_to="",
                        width_field="image_width",
                    ),
                ),
                ("image_height", models.PositiveIntegerField()),
                ("image_width", models.PositiveIntegerField()),
                (
                    "product_refund",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="orders.productrefund",
                    ),
                ),
                (
                    "refund",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="orders.refund"
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
                to="orders.refund",
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
                        to="orders.contactrefund",
                    ),
                ),
                (
                    "courier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.provider",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        to="orders.contactrefund",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="inventory.supplier",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        to="orders.supplierrefund",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        to="orders.supplierrefund",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
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
                        to="orders.courierrefund",
                    ),
                ),
                ("returned", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("orders.courierrefund",),
        ),
        migrations.DeleteModel(
            name="Breakage",
        ),
        migrations.AlterField(
            model_name="productrefund",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.DeleteModel(
            name="OrderUpdate",
        ),
        migrations.DeleteModel(
            name="OrderDetailsUpdate",
        ),
        migrations.DeleteModel(
            name="OrderDetailsUpdateError",
        ),
    ]
