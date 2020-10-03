# Generated by Django 3.0.7 on 2020-06-11 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0010_shippingrule_shipping_service"),
    ]

    operations = [
        migrations.AddField(
            model_name="country",
            name="vat_required",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="region",
            name="vat_required",
            field=models.BooleanField(default=False),
        ),
    ]