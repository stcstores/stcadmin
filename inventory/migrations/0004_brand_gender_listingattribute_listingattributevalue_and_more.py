# Generated by Django 4.0.3 on 2022-03-10 10:14

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inventory", "0003_productimage"),
        ("orders", "0026_remove_productsale_department"),
    ]

    operations = [
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
            ],
            options={
                "verbose_name": "Brand",
                "verbose_name_plural": "Brands",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Gender",
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
                ("name", models.CharField(max_length=50)),
                ("ordering", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Gender",
                "verbose_name_plural": "Genders",
                "ordering": ("ordering",),
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
            ],
            options={
                "verbose_name": "Manufacturer",
                "verbose_name_plural": "Manufacturers",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Product",
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
                    "supplier_sku",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("barcode", models.CharField(max_length=20)),
                (
                    "supplier_barcode",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("purchase_price", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "retail_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=8, null=True
                    ),
                ),
                ("weight_grams", models.PositiveSmallIntegerField()),
                ("length_mm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("height_mm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("width_mm", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("end_of_line", models.BooleanField(default=False)),
                ("date_created", models.DateField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("hs_code", models.CharField(max_length=50)),
                ("range_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
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
                "verbose_name": "Product Bay Change",
                "verbose_name_plural": "Product Bay Changes",
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
                ("amazon_search_terms", models.TextField(blank=True, default="")),
                ("amazon_bullet_points", models.TextField(blank=True, default="")),
                ("end_of_line", models.BooleanField(default=False)),
                ("hidden", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Product Range",
                "verbose_name_plural": "Product Ranges",
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
            model_name="stockchange",
            name="product_id",
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
            model_name="packagetype",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="supplier",
            name="active",
            field=models.BooleanField(default=True),
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
        migrations.DeleteModel(
            name="Warehouse",
        ),
        migrations.AddField(
            model_name="variationoptionvalue",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variation_option_values",
                to="inventory.product",
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
            name="bay",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_bay_changes",
                to="inventory.bay",
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
            model_name="productbayhistory",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="product_bay_changes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.brand",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="gender",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="products",
                to="inventory.gender",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="manufacturer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.manufacturer",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="package_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.packagetype",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="product_range",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.productrange",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="supplier",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.supplier",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="vat_rate",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.vatrate",
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
                to="inventory.product",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="productbaylink",
            unique_together={("product", "bay")},
        ),
    ]
