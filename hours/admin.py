"""Model admin for the Hours app."""

from django.contrib import admin

from hours import models


@admin.register(models.ClockTime)
class ClockTimeAdmin(admin.ModelAdmin):
    """Model admin for the ClockTime model."""

    exclude = ()
