# Generated by Django 3.0.7 on 2020-06-17 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0013_auto_20200617_1255"),
    ]

    operations = [
        migrations.CreateModel(
            name="VATRate",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("cc_id", models.PositiveSmallIntegerField()),
                ("percentage", models.PositiveSmallIntegerField()),
                ("ordering", models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                "verbose_name": "VAT Rate",
                "verbose_name_plural": "VAT Rates",
                "ordering": ("ordering",),
            },
        ),
    ]