"""Model Admin for the logs app."""

from django.contrib import admin

from logs import models


@admin.register(models.FBALogUsers)
class FBALogUsersAdmin(admin.ModelAdmin):
    """Model admin for the FBALogUsers model."""

    exclude_fields = ("created_at", "modified_at")


@admin.register(models.WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    """Model admin for the WorkLog model."""

    exclude_fields = ("created_at", "modified_at")
