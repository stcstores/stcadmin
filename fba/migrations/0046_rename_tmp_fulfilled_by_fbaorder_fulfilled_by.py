# Generated by Django 4.2.5 on 2023-09-11 10:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("fba", "0045_remove_fbaorder_fulfilled_by"),
    ]

    operations = [
        migrations.RenameField(
            model_name="fbaorder",
            old_name="tmp_fulfilled_by",
            new_name="fulfilled_by",
        ),
    ]