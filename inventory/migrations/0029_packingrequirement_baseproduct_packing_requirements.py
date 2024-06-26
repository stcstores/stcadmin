# Generated by Django 5.0.6 on 2024-05-15 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0028_endoflinereason_baseproduct_end_of_line_reason"),
    ]

    operations = [
        migrations.CreateModel(
            name="PackingRequirement",
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
                ("ordering", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Packing Requirement",
                "verbose_name_plural": "Packing Requirements",
                "ordering": ["ordering"],
            },
        ),
        migrations.AddField(
            model_name="baseproduct",
            name="packing_requirements",
            field=models.ManyToManyField(
                related_name="products", to="inventory.packingrequirement"
            ),
        ),
    ]
