# Generated by Django 5.0.2 on 2024-02-28 12:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0058_fbaorder_priority_temp"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fbaorder",
            options={
                "ordering": ["-priority_temp"],
                "verbose_name": "FBA Order",
                "verbose_name_plural": "FBA Orders",
            },
        ),
        migrations.RemoveField(
            model_name="fbaorder",
            name="priority",
        ),
    ]