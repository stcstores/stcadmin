# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-20 15:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_auto_20171120_1251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingprice',
            name='country',
        ),
        migrations.RemoveField(
            model_name='shippingprice',
            name='package_type',
        ),
        migrations.RemoveField(
            model_name='shippingprice',
            name='vat_rates',
        ),
        migrations.DeleteModel(
            name='DestinationCountry',
        ),
        migrations.DeleteModel(
            name='PackageType',
        ),
        migrations.DeleteModel(
            name='ShippingPrice',
        ),
        migrations.DeleteModel(
            name='VATRate',
        ),
    ]
