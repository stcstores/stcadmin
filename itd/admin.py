"""Model admin for the ITD app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from itd import models

admin.site.register(models.ITDConfig, SingletonModelAdmin)


@admin.register(models.ITDManifest)
class ITDManifestAdmin(admin.ModelAdmin):
    """Model admin for the ITDManifest model."""

    fields = ("status", "manifest_file")
    list_display = ("created_at", "last_generated_at", "status", "manifest_file")
