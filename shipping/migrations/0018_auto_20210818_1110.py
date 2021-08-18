# Generated by Django 3.2.6 on 2021-08-18 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0017_auto_20210601_1017"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="vat_required",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Always", "Always"),
                    ("Never", "Never"),
                    ("Variable", "Variable"),
                    ("As Region", "As Region"),
                ],
                default="As Region",
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="region",
            name="vat_required",
            field=models.CharField(
                choices=[
                    ("Always", "Always"),
                    ("Never", "Never"),
                    ("Variable", "Variable"),
                ],
                default="Variable",
                max_length=10,
            ),
        ),
    ]
