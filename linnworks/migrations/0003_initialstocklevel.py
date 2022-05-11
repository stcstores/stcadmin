# Generated by Django 4.0.4 on 2022-05-11 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linnworks', '0002_linnworksconfig_channel_items_export_file_path_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='InitialStockLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(db_index=True, max_length=255, unique=True)),
                ('stock_level', models.PositiveIntegerField()),
            ],
        ),
    ]
