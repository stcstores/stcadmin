# Generated by Django 5.0.6 on 2024-05-15 10:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0063_fbashipmentorder_at_risk_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fbaorder",
            name="is_fragile",
        ),
    ]