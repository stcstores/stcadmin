# Generated by Django 3.1.4 on 2020-12-17 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0022_fbaorder_is_combinable"),
    ]

    operations = [
        migrations.AddField(
            model_name="fbaorder",
            name="product_purchase_price",
            field=models.CharField(default="", max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="fbaorder",
            name="selling_price",
            field=models.PositiveIntegerField(blank=True),
        ),
    ]
