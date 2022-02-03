# Generated by Django 4.0.2 on 2022-02-03 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("channels", "0004_auto_20210809_1217"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopifyConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("channel_id", models.CharField(max_length=20)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
