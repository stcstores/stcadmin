# Generated by Django 3.0.6 on 2020-06-02 10:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0008_auto_20200527_1504"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="shipping.Region"
            ),
        ),
    ]
