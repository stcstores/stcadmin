# Generated by Django 4.0.5 on 2022-06-16 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0031_order_packed_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='packed_by',
        ),
    ]
