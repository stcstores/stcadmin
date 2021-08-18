# Generated by Django 3.2.6 on 2021-08-18 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0019_alter_country_vat_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="country",
            name="default_vat_rate",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="region",
            name="default_vat_rate",
            field=models.FloatField(default=20),
        ),
    ]