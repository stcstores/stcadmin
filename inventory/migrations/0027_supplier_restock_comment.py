# Generated by Django 5.0.1 on 2024-01-25 10:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0026_product_is_flammable"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplier",
            name="restock_comment",
            field=models.TextField(blank=True),
        ),
    ]
