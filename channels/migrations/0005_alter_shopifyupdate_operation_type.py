# Generated by Django 5.0.1 on 2024-01-03 12:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("channels", "0004_alter_shopifyupdate_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shopifyupdate",
            name="operation_type",
            field=models.CharField(
                choices=[
                    ("Create Product", "Create Product"),
                    ("Update Product", "Update Product"),
                ],
                max_length=20,
            ),
        ),
    ]
