# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-28 14:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('print_audit', '0006_auto_20170829_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
