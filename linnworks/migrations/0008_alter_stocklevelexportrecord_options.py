# Generated by Django 4.0.5 on 2022-06-13 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linnworks', '0007_stocklevelexportupdate_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stocklevelexportrecord',
            options={'get_latest_by': 'stock_level_update__export_time', 'verbose_name': 'Stock Level Export Record', 'verbose_name_plural': 'Stock Levels Export Records'},
        ),
    ]
