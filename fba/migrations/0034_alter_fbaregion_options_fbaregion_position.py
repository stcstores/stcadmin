# Generated by Django 4.1.2 on 2022-10-13 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0033_fbaregion_min_shipping_cost_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fbaregion",
            options={
                "ordering": ("position",),
                "verbose_name": "FBA Region",
                "verbose_name_plural": "FBA Regions",
            },
        ),
        migrations.AddField(
            model_name="fbaregion",
            name="position",
            field=models.PositiveSmallIntegerField(default=9999),
        ),
    ]
