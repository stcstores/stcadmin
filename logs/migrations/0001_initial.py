# Generated by Django 5.1.6 on 2025-02-13 12:15

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("home", "0012_staff_can_clock_in"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkLog",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("date", models.DateField()),
                ("work", models.TextField()),
                (
                    "staff_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="work_logs",
                        to="home.staff",
                    ),
                ),
            ],
            options={
                "verbose_name": "Work Log",
                "verbose_name_plural": "Work Logs",
            },
        ),
    ]
