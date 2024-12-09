"""Model admin for the Hours app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from hours import forms, models


@admin.register(models.ClockTime)
class ClockTimeAdmin(admin.ModelAdmin):
    """Model admin for the ClockTime model."""

    form = forms.ClockTimeForm

    exclude = ()
    list_filter = [("user", admin.RelatedOnlyFieldListFilter)]
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)


@admin.register(models.HoursSettings)
class HoursSettingsAdmin(SingletonModelAdmin):
    """Admin for the HoursSettings model."""

    exclude = ()


@admin.register(models.HoursExport)
class HoursExportAdmin(admin.ModelAdmin):
    """Admin for the HoursExport model."""

    exclude = ()
