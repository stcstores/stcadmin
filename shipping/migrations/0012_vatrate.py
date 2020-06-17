# Generated by Django 3.0.7 on 2020-06-16 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0011_auto_20200611_1557"),
    ]

    operations = [
        migrations.CreateModel(
            name="VATRate",
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
    ]
