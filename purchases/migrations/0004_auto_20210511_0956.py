# Generated by Django 3.1.8 on 2021-05-11 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0003_stockpurchase_discount_percentage"),
    ]

    operations = [
        migrations.RenameField(
            model_name="stockpurchase",
            old_name="product_purchase_price",
            new_name="full_price",
        ),
    ]
