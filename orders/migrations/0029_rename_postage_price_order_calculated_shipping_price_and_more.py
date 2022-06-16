# Generated by Django 4.0.4 on 2022-05-24 11:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0022_remove_courier_courier_type_and_more"),
        ("orders", "0028_rename_channel_order_id_order_external_reference_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="postage_price",
            new_name="calculated_shipping_price",
        ),
        migrations.RenameField(
            model_name="productsale",
            old_name="vat",
            new_name="item_total_before_tax",
        ),
        migrations.RemoveField(
            model_name="order",
            name="postage_price_success",
        ),
        migrations.RemoveField(
            model_name="productsale",
            name="price",
        ),
        migrations.AddField(
            model_name="order",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_currencies",
                to="shipping.currency",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="displayed_shipping_price",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="tax",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="productsale",
            name="item_price",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="productsale",
            name="tax",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="productsale",
            name="unit_price",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="productsale",
            name="purchase_price",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]