# Generated by Django 2.0.1 on 2018-02-19 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_calculator', '0003_destinationcountry_currency_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='destinationcountry',
            name='min_channel_fee',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
