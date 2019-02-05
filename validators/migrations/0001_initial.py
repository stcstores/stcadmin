# Generated by Django 2.1.5 on 2019-02-05 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ModelValidationLog",
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
                ("app", models.CharField(max_length=255)),
                ("model", models.CharField(max_length=255)),
                ("error_level", models.PositiveIntegerField()),
                ("object_validator", models.CharField(max_length=255)),
                ("validation_check", models.CharField(max_length=255)),
                ("error_message", models.TextField()),
                ("last_seen", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Model Validation Log",
                "verbose_name_plural": "Model Validation Log",
                "ordering": (
                    "app",
                    "model",
                    "object_validator",
                    "-error_level",
                    "validation_check",
                ),
            },
        )
    ]
