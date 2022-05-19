# Generated by Django 4.0.4 on 2022-05-19 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_calculator', '0014_channelfee_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingmethod',
            name='inactive',
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
