"""Model for configuring the Linnworks app."""

from django.db import models
from solo.models import SingletonModel

from orders.models.channel import Channel


class LinnworksConfig(SingletonModel):
    """Model for configuring the Linnworks app."""

    inventory_import_file_path = models.CharField(max_length=250, blank=True, null=True)
    composition_import_file_path = models.CharField(
        max_length=250, blank=True, null=True
    )
    channel_items_import_file_path = models.CharField(
        max_length=250, blank=True, null=True
    )
    processed_orders_import_path = models.CharField(
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
    image_import_file_path = models.CharField(max_length=250, blank=True, null=True)
    stock_level_export_file_path = models.CharField(
        max_length=250, blank=True, null=True
    )
    last_image_update = models.DateTimeField()

    class Meta:
        """Meta class for the LinnworksConfig model."""

        verbose_name = "Linnworks Config"


class LinnworksChannel(models.Model):
    """Model for Linnworks integrated selling channels."""

    source = models.CharField(max_length=255)
    sub_source = models.CharField(max_length=255)
    readable_name = models.CharField(max_length=255, blank=True)
    item_link_format = models.CharField(max_length=255, blank=True)
    link_prime = models.BooleanField(default=False)
    channel = models.ForeignKey(
        Channel,
        on_delete=models.PROTECT,
        related_name="linnworks_channel",
        null=True,
        blank=True,
    )

    class Meta:
        """Meta class for the LinnworksChannel model."""

        verbose_name = "Linnworks Channel"
        verbose_name_plural = "Linnworks Channels"
        unique_together = ["source", "sub_source"]
        ordering = ["source", "sub_source"]

    def __str__(self):
        return f"{self.source} - {self.sub_source}"

    def name(self):
        """Return the name of the channel."""
        if self.readable_name:
            return self.readable_name
        else:
            return self.sub_source

    def item_link(self, item_channel_id):
        """Return a link to an item on the channel."""
        if item_channel_id and self.item_link_format:
            return self.item_link_format.format(item_channel_id)
        return None
