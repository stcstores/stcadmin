# Generated by Django 2.0 on 2018-01-04 11:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("stock_check", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="ProductBayStock",
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
                    "stock_level",
                    models.PositiveIntegerField(blank=True, default=None, null=True),
                ),
            ],
        ),
        migrations.AlterModelOptions(name="bay", options={"ordering": ("name",)}),
        migrations.AlterModelOptions(name="warehouse", options={"ordering": ("name",)}),
        migrations.AddField(
            model_name="productbaystock",
            name="bay",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stock_check.Bay"
            ),
        ),
        migrations.AddField(
            model_name="productbaystock",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stock_check.Product"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="productbaystock", unique_together={("product", "bay")}
        ),
    ]
