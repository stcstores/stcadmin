# Generated by Django 3.1.4 on 2020-12-02 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fba", "0019_fbawarehouse"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="fbawarehouse",
            options={
                "ordering": ("name",),
                "verbose_name": "FBA Warehouse",
                "verbose_name_plural": "FBA Warehouses",
            },
        ),
    ]
