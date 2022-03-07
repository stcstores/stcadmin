# Generated by Django 2.2.7 on 2019-11-13 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("labelmaker", "0001_initial_squashed_0003_auto_20180514_0933"),
        ("inventory", "0004_auto_20220301_1107"),
    ]

    operations = [
        migrations.AddField(
            model_name="sizechart",
            name="supplier",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory.Supplier",
            ),
        ),
        migrations.AlterField(
            model_name="sizechartsize",
            name="size_chart",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="labelmaker.SizeChart",
            ),
        ),
    ]
