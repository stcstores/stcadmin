# Generated by Django 2.0.5 on 2018-05-14 09:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_warehouse_abriviation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='barcode',
            options={'verbose_name': 'Barcode', 'verbose_name_plural': 'Barcodes'},
        ),
        migrations.AlterModelOptions(
            name='bay',
            options={'verbose_name': 'Bay', 'verbose_name_plural': 'Bays'},
        ),
        migrations.AlterModelOptions(
            name='stcadminimage',
            options={'verbose_name': 'STC Admin Image', 'verbose_name_plural': 'STC Admin Images'},
        ),
        migrations.AlterModelOptions(
            name='warehouse',
            options={'verbose_name': 'Warehouse', 'verbose_name_plural': 'Warehouses'},
        ),
    ]
