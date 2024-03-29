# Generated by Django 4.0.3 on 2022-03-30 11:21

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import stcadmin.settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
        ("inventory", "0003_productimage"),
        (
            "orders",
            "0001_squashed_0028_rename_channel_order_id_order_external_reference_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="BaseProduct",
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
                ("sku", models.CharField(db_index=True, max_length=255, unique=True)),
                (
                    "retail_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=8, null=True
                    ),
                ),
                (
                    "supplier_sku",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("barcode", models.CharField(max_length=20)),
                (
                    "supplier_barcode",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("length_mm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("height_mm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("width_mm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("is_end_of_line", models.BooleanField(default=False)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("range_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Base Product",
                "verbose_name_plural": "Base Products",
                "ordering": ("product_range", "range_order"),
                "base_manager_name": "objects",
            },
        ),
        migrations.CreateModel(
            name="Brand",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Brand",
                "verbose_name_plural": "Brands",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="CombinationProductLink",
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
                ("quantity", models.PositiveIntegerField()),
            ],
            options={
                "verbose_name": "Combination Product Link",
                "verbose_name_plural": "Combination Product Links",
            },
        ),
        migrations.CreateModel(
            name="ListingAttribute",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Listing Attribute",
                "verbose_name_plural": "Listing Attributes",
                "ordering": ("ordering",),
            },
        ),
        migrations.CreateModel(
            name="ListingAttributeValue",
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
                ("value", models.CharField(max_length=255)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Listing Attribute Value",
                "verbose_name_plural": "Listing Attribute Values",
                "ordering": ("value",),
            },
        ),
        migrations.CreateModel(
            name="Manufacturer",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("active", models.BooleanField(default=True)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Manufacturer",
                "verbose_name_plural": "Manufacturers",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="ProductBayHistory",
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
                ("timestamp", models.DateTimeField(auto_now=True)),
                (
                    "change",
                    models.CharField(
                        choices=[("removed", "Removed"), ("added", "Added")],
                        max_length=255,
                    ),
                ),
            ],
            options={
                "verbose_name": "Product Bay History",
                "verbose_name_plural": "Product Bay History",
            },
        ),
        migrations.CreateModel(
            name="ProductBayLink",
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
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Product Bay Link",
                "verbose_name_plural": "Product Bay Links",
            },
        ),
        migrations.CreateModel(
            name="ProductRange",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("complete", "Complete"),
                            ("creating", "Creating"),
                            ("error", "Error"),
                        ],
                        default="creating",
                        max_length=20,
                    ),
                ),
                ("sku", models.CharField(db_index=True, max_length=255, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "search_terms",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        null=True,
                        size=5,
                    ),
                ),
                (
                    "bullet_points",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        null=True,
                        size=5,
                    ),
                ),
                ("is_end_of_line", models.BooleanField(default=False)),
                ("hidden", models.BooleanField(default=False)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Product Range",
                "verbose_name_plural": "Product Ranges",
            },
        ),
        migrations.CreateModel(
            name="ProductRangeImage",
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
                ("ordering", models.PositiveIntegerField()),
                (
                    "image_file",
                    models.ImageField(
                        storage=stcadmin.settings.ProductImageStorage, upload_to=""
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Product Range Image",
                "verbose_name_plural": "Product Range Images",
                "ordering": ("ordering",),
            },
        ),
        migrations.CreateModel(
            name="StockLevelHistory",
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
                    "source",
                    models.CharField(
                        choices=[("U", "User"), ("I", "Import"), ("A", "API")],
                        max_length=1,
                    ),
                ),
                ("stock_level", models.PositiveIntegerField()),
                ("timestamp", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Stock Level History",
                "verbose_name_plural": "Stock Level History",
                "ordering": ("timestamp",),
            },
        ),
        migrations.CreateModel(
            name="VariationOption",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Variation Option",
                "verbose_name_plural": "Variation Options",
                "ordering": ("ordering",),
            },
        ),
        migrations.CreateModel(
            name="VariationOptionValue",
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
                ("value", models.CharField(max_length=255)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Variation Option Value",
                "verbose_name_plural": "Variation Option Values",
                "ordering": ("variation_option", "value"),
            },
        ),
        migrations.CreateModel(
            name="VATRate",
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
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "percentage",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1),
                        ]
                    ),
                ),
                ("ordering", models.PositiveIntegerField(default=0)),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "VAT Rate",
                "verbose_name_plural": "VAT Rates",
                "ordering": ["ordering"],
            },
        ),
        migrations.DeleteModel(
            name="Department",
        ),
        migrations.DeleteModel(
            name="InternationalShipping",
        ),
        migrations.RemoveField(
            model_name="stockchange",
            name="user",
        ),
        migrations.AlterModelOptions(
            name="bay",
            options={
                "ordering": ("name",),
                "verbose_name": "Bay",
                "verbose_name_plural": "Bays",
            },
        ),
        migrations.AlterModelOptions(
            name="packagetype",
            options={
                "ordering": ("ordering",),
                "verbose_name": "Package Type",
                "verbose_name_plural": "Package Types",
            },
        ),
        migrations.AlterModelOptions(
            name="productimage",
            options={
                "ordering": ("ordering",),
                "verbose_name": "Product Image",
                "verbose_name_plural": "Product Images",
            },
        ),
        migrations.AlterModelOptions(
            name="supplier",
            options={
                "ordering": ("name",),
                "verbose_name": "Supplier",
                "verbose_name_plural": "Suppliers",
            },
        ),
        migrations.RemoveConstraint(
            model_name="bay",
            name="single_default_bay_per_warehouse",
        ),
        migrations.RenameField(
            model_name="productimage",
            old_name="position",
            new_name="ordering",
        ),
        migrations.RemoveField(
            model_name="bay",
            name="bay_ID",
        ),
        migrations.RemoveField(
            model_name="bay",
            name="is_default",
        ),
        migrations.RemoveField(
            model_name="bay",
            name="warehouse",
        ),
        migrations.RemoveField(
            model_name="packagetype",
            name="description",
        ),
        migrations.RemoveField(
            model_name="packagetype",
            name="inactive",
        ),
        migrations.RemoveField(
            model_name="packagetype",
            name="product_option_value_ID",
        ),
        migrations.RemoveField(
            model_name="productimage",
            name="cloud_commerce_name",
        ),
        migrations.RemoveField(
            model_name="productimage",
            name="product_id",
        ),
        migrations.RemoveField(
            model_name="productimage",
            name="range_sku",
        ),
        migrations.RemoveField(
            model_name="productimage",
            name="sku",
        ),
        migrations.RemoveField(
            model_name="supplier",
            name="factory_ID",
        ),
        migrations.RemoveField(
            model_name="supplier",
            name="inactive",
        ),
        migrations.RemoveField(
            model_name="supplier",
            name="product_option_value_ID",
        ),
        migrations.AddField(
            model_name="bay",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="bay",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="bay",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="packagetype",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="packagetype",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="packagetype",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="productimage",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="productimage",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="supplier",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="supplier",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="supplier",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="suppliercontact",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="suppliercontact",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image_file",
            field=models.ImageField(
                storage=stcadmin.settings.ProductImageStorage, upload_to=""
            ),
        ),
        migrations.AlterField(
            model_name="supplier",
            name="name",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="suppliercontact",
            name="supplier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="supplier_contacts",
                to="inventory.supplier",
            ),
        ),
        migrations.CreateModel(
            name="CombinationProduct",
            fields=[
                (
                    "baseproduct_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="inventory.baseproduct",
                    ),
                ),
            ],
            options={
                "verbose_name": "Combination Product",
                "verbose_name_plural": "Combination Products",
            },
            bases=("inventory.baseproduct",),
        ),
        migrations.CreateModel(
            name="MultipackProduct",
            fields=[
                (
                    "baseproduct_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="inventory.baseproduct",
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("inventory.baseproduct",),
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "baseproduct_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="inventory.baseproduct",
                    ),
                ),
                ("purchase_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("weight_grams", models.PositiveSmallIntegerField()),
                ("hs_code", models.CharField(max_length=50)),
                (
                    "brand",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="inventory.brand",
                    ),
                ),
                (
                    "manufacturer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="inventory.manufacturer",
                    ),
                ),
                (
                    "vat_rate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="inventory.vatrate",
                    ),
                ),
            ],
            options={
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
            bases=("inventory.baseproduct",),
        ),
        migrations.DeleteModel(
            name="StockChange",
        ),
        migrations.DeleteModel(
            name="Warehouse",
        ),
        migrations.AddField(
            model_name="variationoptionvalue",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variation_option_values",
                to="inventory.baseproduct",
            ),
        ),
        migrations.AddField(
            model_name="variationoptionvalue",
            name="variation_option",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="variation_option_values",
                to="inventory.variationoption",
            ),
        ),
        migrations.AddField(
            model_name="stocklevelhistory",
            name="previous_change",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory.stocklevelhistory",
            ),
        ),
        migrations.AddField(
            model_name="stocklevelhistory",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stock_level_history",
                to="inventory.baseproduct",
            ),
        ),
        migrations.AddField(
            model_name="stocklevelhistory",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="stock_change_history",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="productrangeimage",
            name="product_range",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="images",
                to="inventory.productrange",
            ),
        ),
        migrations.AddField(
            model_name="productrange",
            name="managed_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_ranges",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="productbaylink",
            name="bay",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_bay_links",
                to="inventory.bay",
            ),
        ),
        migrations.AddField(
            model_name="productbayhistory",
            name="bay",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_bay_changes",
                to="inventory.bay",
            ),
        ),
        migrations.AddField(
            model_name="productbayhistory",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_bay_changes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="listingattributevalue",
            name="listing_attribute",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="listing_attribute_values",
                to="inventory.listingattribute",
            ),
        ),
        migrations.AddField(
            model_name="listingattributevalue",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="listing_attribute_values",
                to="inventory.baseproduct",
            ),
        ),
        migrations.AddField(
            model_name="baseproduct",
            name="latest_stock_change",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory.stocklevelhistory",
            ),
        ),
        migrations.AddField(
            model_name="baseproduct",
            name="package_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.packagetype",
            ),
        ),
        migrations.AddField(
            model_name="baseproduct",
            name="polymorphic_ctype",
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="polymorphic_%(app_label)s.%(class)s_set+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="baseproduct",
            name="product_range",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.productrange",
            ),
        ),
        migrations.AddField(
            model_name="baseproduct",
            name="supplier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.supplier",
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="images",
                to="inventory.baseproduct",
            ),
        ),
        migrations.CreateModel(
            name="InitialVariation",
            fields=[
                (
                    "product_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="inventory.product",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("inventory.product",),
        ),
        migrations.AlterUniqueTogether(
            name="variationoptionvalue",
            unique_together={("product", "variation_option")},
        ),
        migrations.AddField(
            model_name="productbaylink",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_bay_links",
                to="inventory.product",
            ),
        ),
        migrations.AddField(
            model_name="productbayhistory",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_bay_changes",
                to="inventory.product",
            ),
        ),
        migrations.AddField(
            model_name="multipackproduct",
            name="base_product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="multipacks",
                to="inventory.product",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="listingattributevalue",
            unique_together={("product", "listing_attribute")},
        ),
        migrations.AddField(
            model_name="combinationproductlink",
            name="combination_product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="combination_product_links",
                to="inventory.combinationproduct",
            ),
        ),
        migrations.AddField(
            model_name="combinationproductlink",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="combination_product_links",
                to="inventory.product",
            ),
        ),
        migrations.AddField(
            model_name="combinationproduct",
            name="products",
            field=models.ManyToManyField(
                related_name="combination_products",
                through="inventory.CombinationProductLink",
                to="inventory.product",
            ),
        ),
        migrations.AddIndex(
            model_name="baseproduct",
            index=models.Index(fields=["sku"], name="inventory_b_sku_ce29d4_idx"),
        ),
        migrations.AddIndex(
            model_name="baseproduct",
            index=models.Index(
                fields=["supplier_sku"], name="inventory_b_supplie_3b5e51_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="baseproduct",
            index=models.Index(
                fields=["barcode"], name="inventory_b_barcode_798f9e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="baseproduct",
            index=models.Index(
                fields=["supplier_barcode"], name="inventory_b_supplie_07990b_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="productbaylink",
            unique_together={("product", "bay")},
        ),
        migrations.AlterUniqueTogether(
            name="combinationproductlink",
            unique_together={("product", "combination_product")},
        ),
    ]
