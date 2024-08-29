"""Model Admin for the Home app."""

from django.contrib import admin

from home import models


@admin.register(models.Staff)
class StaffAdmin(admin.ModelAdmin):
    """Model admin for Staff model."""

    exclude = ()
    list_display = (
        "full_name",
        "first_name",
        "second_name",
        "stcadmin_user",
        "email_address",
        "fba_packer",
        "hidden",
        "can_clock_in",
    )
    list_display_links = ("full_name",)
    list_editable = (
        "stcadmin_user",
        "email_address",
        "fba_packer",
        "hidden",
        "can_clock_in",
    )
    search_fields = (
        "stcadmin_user__username" "first_name",
        "second_name",
        "email_address",
    )
    list_select_related = ("stcadmin_user",)
    list_filter = ("hidden",)
    autocomplete_fields = ("stcadmin_user",)


@admin.register(models.ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    """Model admin for the ExternalLink model."""

    exclude = ()
    list_display = ("__str__", "name", "url", "ordering")
    list_editable = ("name", "url", "ordering")
