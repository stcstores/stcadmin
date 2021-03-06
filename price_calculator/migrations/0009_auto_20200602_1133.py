# Generated by Django 3.0.6 on 2020-06-02 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("price_calculator", "0008_auto_20200602_1109"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="vatrate",
            options={
                "ordering": ("ordering",),
                "verbose_name": "VAT Rate",
                "verbose_name_plural": "VAT Rates",
            },
        ),
        migrations.AddField(
            model_name="vatrate",
            name="ordering",
            field=models.PositiveSmallIntegerField(default=100),
        ),
    ]
