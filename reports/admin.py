"""Admin for the reports app."""

from django.contrib import admin

from reports import models


@admin.register(models.ReorderReportDownload)
class ReorderReportDownloadAdmin(admin.ModelAdmin):
    """Model admin for the ReorderReportDownload model."""

    exclude = ()
    list_display = ""
    list_display = (
        "status",
        "user",
        "supplier",
        "date_from",
        "date_to",
        "created_at",
        "completed_at",
        "error_message",
        "row_count",
        "download_file",
    )
    date_hierarchy = "created_at"
