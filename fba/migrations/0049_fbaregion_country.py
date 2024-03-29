# Generated by Django 4.2.5 on 2023-09-27 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("shipping", "0024_alter_exchangerate_unique_together"),
        ("fba", "0048_remove_fbaorder_product_sku_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="fbaregion",
            name="country",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="shipping.country",
            ),
        ),
    ]
