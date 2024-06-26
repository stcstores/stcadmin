# Generated by Django 5.0.6 on 2024-05-13 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0027_supplier_restock_comment"),
    ]

    operations = [
        migrations.CreateModel(
            name="EndOfLineReason",
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
                ("short_name", models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                "verbose_name": "End of Line Reason",
                "verbose_name_plural": "End of Line Reasons",
            },
        ),
        migrations.AddField(
            model_name="baseproduct",
            name="end_of_line_reason",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="inventory.endoflinereason",
            ),
        ),
    ]
