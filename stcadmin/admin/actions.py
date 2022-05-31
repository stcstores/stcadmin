"""General actions for use in model admin."""

from django.contrib import admin


@admin.action(description="Set Inactive")
def set_inactive(modeladmin, request, queryset):
    """Set inactive action."""
    queryset.update(active=False)


@admin.action(description="Set Active")
def set_active(modeladmin, request, queryset):
    """Set active action."""
    queryset.update(active=True)
