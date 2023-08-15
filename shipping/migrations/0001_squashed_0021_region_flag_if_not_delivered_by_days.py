# Generated by Django 4.2.4 on 2023-08-15 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    replaces = [
        ("shipping", "0001_initial"),
        ("shipping", "0002_auto_20200213_1259"),
        ("shipping", "0003_auto_20200218_1150"),
        ("shipping", "0004_auto_20200527_1129"),
        ("shipping", "0005_auto_20200527_1417"),
        ("shipping", "0006_country_region"),
        ("shipping", "0007_remove_country_old_region"),
        ("shipping", "0008_auto_20200527_1504"),
        ("shipping", "0009_auto_20200602_1109"),
        ("shipping", "0010_shippingrule_shipping_service"),
        ("shipping", "0011_auto_20200611_1557"),
        ("shipping", "0012_remove_shippingprice_price_type"),
        ("shipping", "0013_auto_20200617_1255"),
        ("shipping", "0014_vatrate"),
        ("shipping", "0015_country_flag"),
        ("shipping", "0016_auto_20210426_1006"),
        ("shipping", "0017_auto_20210601_1017"),
        ("shipping", "0018_auto_20210818_1110"),
        ("shipping", "0019_alter_country_vat_required"),
        ("shipping", "0020_auto_20210818_1133"),
        ("shipping", "0021_region_flag_if_not_delivered_by_days"),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Currency",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("code", models.CharField(max_length=5, unique=True)),
                ("exchange_rate", models.DecimalField(decimal_places=3, max_digits=6)),
                ("symbol", models.CharField(default="$", max_length=5)),
            ],
            options={
                "verbose_name": "Currency",
                "verbose_name_plural": "Currencies",
            },
        ),
        migrations.CreateModel(
            name="Provider",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("inactive", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Provider",
                "verbose_name_plural": "Providers",
            },
        ),
        migrations.CreateModel(
            name="Country",
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
                ("country_ID", models.CharField(max_length=10, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("ISO_code", models.CharField(blank=True, max_length=2, null=True)),
                (
                    "old_region",
                    models.CharField(
                        choices=[
                            ("EU", "Europe"),
                            ("UK", "UK"),
                            ("ROW", "Rest of World"),
                        ],
                        max_length=3,
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="shipping.currency",
                    ),
                ),
            ],
            options={
                "verbose_name": "Country",
                "verbose_name_plural": "Countries",
                "ordering": ("country_ID",),
            },
        ),
        migrations.CreateModel(
            name="Courier",
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
                    "courier_ID",
                    models.CharField(db_index=True, max_length=12, unique=True),
                ),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("inactive", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Courier",
                "verbose_name_plural": "Couriers",
            },
        ),
        migrations.CreateModel(
            name="CourierService",
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
                    "courier_service_ID",
                    models.CharField(db_index=True, max_length=12, unique=True),
                ),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "courier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.courier",
                    ),
                ),
            ],
            options={
                "verbose_name": "Courier Service",
                "verbose_name_plural": "Couriers Services",
            },
        ),
        migrations.CreateModel(
            name="CourierType",
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
                    "courier_type_ID",
                    models.CharField(db_index=True, max_length=12, unique=True),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "provider",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.provider",
                    ),
                ),
            ],
            options={
                "verbose_name": "Courier Type",
                "verbose_name_plural": "Courier Types",
            },
        ),
        migrations.AddField(
            model_name="courier",
            name="courier_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="shipping.couriertype",
            ),
        ),
        migrations.CreateModel(
            name="ShippingRule",
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
                    "rule_ID",
                    models.CharField(db_index=True, max_length=10, unique=True),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("priority", models.BooleanField(default=False)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "courier_service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="shipping.courierservice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Shipping Rule",
                "verbose_name_plural": "Shipping Rules",
                "ordering": ("inactive", "name"),
            },
        ),
        migrations.CreateModel(
            name="ShippingPrice",
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
                    "price_type",
                    models.CharField(
                        choices=[
                            ("fixed", "Fixed"),
                            ("weight", "Weight"),
                            ("weight_band", "Weight Band"),
                        ],
                        max_length=50,
                    ),
                ),
                ("item_price", models.IntegerField(default=0)),
                ("price_per_kg", models.IntegerField(default=0)),
                ("inactive", models.BooleanField(default=False)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.country",
                    ),
                ),
            ],
            options={
                "verbose_name": "Shipping Price",
                "verbose_name_plural": "Shipping Prices",
            },
        ),
        migrations.CreateModel(
            name="ShippingService",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Shipping Service",
                "verbose_name_plural": "Shipping Services",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="WeightBand",
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
                ("min_weight", models.IntegerField()),
                ("max_weight", models.IntegerField()),
                ("price", models.IntegerField()),
                (
                    "shipping_price",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipping.shippingprice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Weight Band",
                "verbose_name_plural": "Weight Bands",
                "ordering": ("min_weight",),
            },
        ),
        migrations.AddField(
            model_name="shippingprice",
            name="shipping_service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="shipping.shippingservice",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="shippingprice",
            unique_together={("shipping_service", "country")},
        ),
        migrations.CreateModel(
            name="Region",
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
                ("abriviation", models.CharField(blank=True, max_length=10, null=True)),
            ],
            options={
                "verbose_name": "Region",
                "verbose_name_plural": "Regions",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="country",
            name="region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="shipping.region",
            ),
        ),
        migrations.RemoveField(
            model_name="country",
            name="old_region",
        ),
        migrations.AddField(
            model_name="shippingprice",
            name="region",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="shipping.region",
            ),
        ),
        migrations.AlterField(
            model_name="shippingprice",
            name="country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="shipping.country",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="shippingprice",
            unique_together={
                ("shipping_service", "country"),
                ("shipping_service", "region"),
            },
        ),
        migrations.AddConstraint(
            model_name="shippingprice",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("country__isnull", False), ("region__isnull", True)),
                    models.Q(("country__isnull", True), ("region__isnull", False)),
                    _connector="OR",
                ),
                name="shipping_price_has_country_or_region",
            ),
        ),
        migrations.AlterField(
            model_name="country",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="shipping.region"
            ),
        ),
        migrations.AddField(
            model_name="shippingrule",
            name="shipping_service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="shipping.shippingservice",
            ),
        ),
        migrations.RemoveField(
            model_name="shippingprice",
            name="price_type",
        ),
        migrations.AddField(
            model_name="shippingprice",
            name="price_per_g",
            field=models.DecimalField(decimal_places=3, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name="shippingprice",
            name="item_price",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="shippingprice",
            name="price_per_kg",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="country",
            name="flag",
            field=models.ImageField(blank=True, null=True, upload_to="flags"),
        ),
        migrations.AddField(
            model_name="shippingprice",
            name="covid_surcharge",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="shippingprice",
            name="fuel_surcharge",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="shippingprice",
            name="item_surcharge",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="country",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="courier",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="courierservice",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="couriertype",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="currency",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="provider",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="region",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="shippingprice",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="shippingrule",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="shippingservice",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
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
                ("name", models.CharField(max_length=50)),
                ("cc_id", models.PositiveSmallIntegerField()),
                ("percentage", models.PositiveSmallIntegerField()),
                ("ordering", models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                "verbose_name": "VAT Rate",
                "verbose_name_plural": "VAT Rates",
                "ordering": ("ordering",),
            },
        ),
        migrations.AlterField(
            model_name="weightband",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddField(
            model_name="region",
            name="vat_required",
            field=models.CharField(
                choices=[
                    ("Always", "Always"),
                    ("Never", "Never"),
                    ("Variable", "Variable"),
                ],
                default="Variable",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="country",
            name="vat_required",
            field=models.CharField(
                choices=[
                    ("Always", "Always"),
                    ("Never", "Never"),
                    ("Variable", "Variable"),
                    ("As Region", "As Region"),
                ],
                default="As Region",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="country",
            name="default_vat_rate",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="region",
            name="default_vat_rate",
            field=models.FloatField(default=20),
        ),
        migrations.AddField(
            model_name="region",
            name="flag_if_not_delivered_by_days",
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]