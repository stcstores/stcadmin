# Generated by Django 4.2.6 on 2023-10-18 10:02

from django.db import migrations, models
import django.utils.timezone
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):
    dependencies = [
        ("restock", "0003_reorder_closed_at_reorder_created_at_and_more"),
    ]

    operations = [
        TrigramExtension(),
        migrations.CreateModel(
            name="BlacklistedBrand",
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
                ("comment", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Blacklisted Brand",
                "verbose_name_plural": "Blacklisted Brands",
                "ordering": ("name",),
            },
        ),
    ]