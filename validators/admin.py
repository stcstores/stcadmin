"""ModelAdmin classes for the validator app."""

from django.contrib import admin

from validators import models


@admin.register(models.ModelValidationLog)
class ModelValidationLogAdmin(admin.ModelAdmin):
    """Model admin for the ModelValidationLog model."""

    fields = (
        "app",
        "model",
        "object_validator",
        "error_level",
        "validation_check",
        "error_message",
    )
    list_display = (
        "__str__",
        "app",
        "model",
        "object_validator",
        "level",
        "validation_check",
        "error_message",
        "last_seen",
    )
    list_display_links = ("__str__",)
    list_filter = ("app", "model", "object_validator", "validation_check")
