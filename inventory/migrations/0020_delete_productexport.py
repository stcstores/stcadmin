# Generated by Django 4.1.2 on 2022-10-24 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0019_productrange_images"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ProductExport",
        ),
    ]
