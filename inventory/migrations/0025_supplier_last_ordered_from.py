# Generated by Django 4.2.6 on 2023-10-23 10:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0024_supplier_blacklisted"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplier",
            name="last_ordered_from",
            field=models.DateField(blank=True, null=True),
        ),
    ]
