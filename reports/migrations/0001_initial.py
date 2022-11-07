# Generated by Django 4.1.1 on 2022-10-11 12:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("inventory", "0019_productrange_images"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ReorderReportDownload",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("in_progress", "In Progress"),
                            ("complete", "Complete"),
                            ("errored", "Errored"),
                        ],
                        default="in_progress",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True)),
                (
                    "download_file",
                    models.FileField(
                        blank=True, null=True, upload_to="reports/reorder_reports"
                    ),
                ),
                ("row_count", models.PositiveIntegerField(blank=True, null=True)),
                ("date_from", models.DateField()),
                ("date_to", models.DateField()),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reorder_reports",
                        to="inventory.supplier",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Reorder Report Download",
                "verbose_name_plural": "Reorder Report Downlaods",
                "ordering": ("-created_at",),
                "get_latest_by": "created_at",
            },
        ),
    ]