"""Model for configuring the Linnworks app."""

from django.db import models
from solo.models import SingletonModel


class LinnworksConfig(SingletonModel):
    """Model for configuring the Linnworks app."""

    inventory_import_file_path = models.CharField(max_length=250)
    composition_import_file_path = models.CharField(max_length=250)
    inventory_export_file_path = models.CharField(max_length=250)
    composition_export_file_path = models.CharField(max_length=250)
    image_export_file_path = models.CharField(max_length=250)

    class Meta:
        """Meta class for the LinnworksConfig model."""

        verbose_name = "Linnworks Config"
