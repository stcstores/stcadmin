# Generated by Django 3.0.7 on 2020-06-09 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("price_calculator", "0009_auto_20200602_1133"),
    ]

    operations = [
        migrations.CreateModel(
            name="Channel",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("ordering", models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                "verbose_name": "Channel",
                "verbose_name_plural": "Channel",
                "ordering": ("ordering",),
            },
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="channel",
            field=models.ManyToManyField(to="price_calculator.Channel"),
        ),
    ]