# Generated by Django 4.2 on 2023-04-17 13:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fba", "0040_alter_fbaorder_product_asin"),
    ]

    operations = [
        migrations.AddField(
            model_name="fbaregion",
            name="expiry_date_required",
            field=models.BooleanField(default=False),
        ),
    ]
