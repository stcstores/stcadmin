"""Model Admin for the Home app."""
from django.contrib import admin

from home import models


@admin.register(models.CloudCommerceUser)
class CloudCommerceUserAdmin(admin.ModelAdmin):
    """Model admin for CloudCommerceUser model."""

    fields = [
        "full_name",
        "user_id",
        "stcadmin_user",
        "first_name",
        "second_name",
        "hidden",
    ]
    list_display = ("full_name", "user_id", "first_name", "second_name", "hidden")
    list_display_links = ("full_name",)
    list_editable = ("user_id", "hidden")
    readonly_fields = ("full_name",)


@admin.register(models.ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    """Model admin for the ExternalLink model."""

    fields = ("name", "url", "ordering")
    list_display = ("__str__", "name", "url", "ordering")
    list_editable = ("name", "url", "ordering")
