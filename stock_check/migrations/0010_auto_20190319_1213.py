# Generated by Django 2.1.7 on 2019-03-19 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0023_vatrate"),
        ("stock_check", "0009_auto_20190226_1206"),
    ]

    operations = [
        migrations.RenameModel(old_name="Product", new_name="StockCheckProduct"),
        migrations.AlterModelOptions(
            name="stockcheckproduct",
            options={
                "verbose_name": "StockCheckProduct",
                "verbose_name_plural": "StockCheckProducts",
            },
        ),
    ]
