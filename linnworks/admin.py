"""Model Admin for the Linnworks app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from linnworks import models


@admin.register(models.LinnworksConfig)
class LinnworksConfigAdmin(SingletonModelAdmin):
    """Model admin for the LinnworksConfig model."""

    exclude_fields = ()
