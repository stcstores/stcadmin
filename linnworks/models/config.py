"""Model for configuring the Linnworks app."""

from django.db import models
from solo.models import SingletonModel


class LinnworksConfig(SingletonModel):
    """Model for configuring the Linnworks app."""

    inventory_import_file_path = models.CharField(max_length=250, blank=True, null=True)
    composition_import_file_path = models.CharField(
        max_length=250, blank=True, null=True
    )
    channel_items_import_file_path = models.CharField(
        max_length=250, blank=True, null=True
    )
    inventory_export_file_path = models.CharField(max_length=250, blank=True, null=True)
    composition_export_file_path = models.CharField(
        max_length=250, blank=True, null=True
    )
    channel_items_export_file_path = models.CharField(
        max_length=250, blank=True, null=True
    )
    image_export_file_path = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        """Meta class for the LinnworksConfig model."""

        verbose_name = "Linnworks Config"


class LinnworksChannel(models.Model):
    """Model for Linnworks integrated selling channels."""

    source = models.CharField(max_length=255)
    sub_source = models.CharField(max_length=255)

    class Meta:
        """Meta class for the LinnworksChannel model."""

        verbose_name = "Linnworks Channel"
        verbose_name_plural = "Linnworks Channels"
        unique_together = ["source", "sub_source"]
        ordering = ["source", "sub_source"]

    def __str__(self):
        return f"{self.source} - {self.sub_source}"
