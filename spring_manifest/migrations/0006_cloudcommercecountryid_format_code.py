# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-10 16:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spring_manifest', '0005_manifestedorder_manifest_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloudcommercecountryid',
            name='format_code',
            field=models.CharField(blank=True, default=None, max_length=1, null=True),
        ),
    ]
