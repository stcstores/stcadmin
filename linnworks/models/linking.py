"""Models for managing Linnworks channel linking."""

from django.db import models

from inventory.models import BaseProduct

from .config import LinnworksChannel
from .linnworks_export_files import ChannelItemsExport
from .linnworks_import_files import BaseImportFile


class LinkingIgnoredSKU(models.Model):
    """Model for SKUs to be ignored when updating channel linking."""

    sku = models.CharField(max_length=255)
    channel = models.ForeignKey(
        LinnworksChannel, on_delete=models.CASCADE, related_name="ignored_linking_skus"
    )

    class Meta:
        """Meta class for the LinkingIgnoredSKU model."""

        verbose_name = "Linking Ignored SKU"
        verbose_name_plural = "Linking Ignored SKUs"


class LinnworksChannelMappingImportFile(BaseImportFile):
    """Create a Linnworks channel linking import."""

    SOURCE = "Source"
    SUBSOURCE = "Subsource"
    LINKED_SKU_CUSTOM_LABEL = "Linked SKU Custom Label"  # Channel SKU
    SKU = "SKU"  # Linnworks SKU

    header = (SOURCE, SUBSOURCE, LINKED_SKU_CUSTOM_LABEL, SKU)

    @classmethod
    def create(cls):
        """Create a Linnworks Product Import file."""
        channels = LinnworksChannel.objects.all().order_by("source", "sub_source")
        product_skus = cls.product_skus()
        linked_skus = cls.linked_skus()
        return cls.create_file(
            channels=channels, product_skus=product_skus, linked_skus=linked_skus
        )

    @classmethod
    def product_skus(cls):
        """Return a set of all SKUs on Linnworks."""
        skus = BaseProduct.objects.variations().active().values_list("sku", flat=True)
        return set(skus)

    @classmethod
    def linked_skus(cls):
        """Return a dict of linnworks.models.LinnworksChannel to a list of linked SKUs."""
        channel_items_file = ChannelItemsExport()
        channels = LinnworksChannel.objects.all()
        linked_skus = {channel: [] for channel in channels}
        for row in channel_items_file.rows:
            for channel in channels:
                if (
                    row[channel_items_file.SOURCE] == channel.source
                    and row[channel_items_file.SUBSOURCE] == channel.sub_source
                ):
                    linked_skus[channel].append(row[channel_items_file.SKU])
        return linked_skus

    @classmethod
    def get_row_data(cls, channels, product_skus, linked_skus):
        """Return a list of channel item dicts."""
        rows = []
        for channel in channels:
            channel_linked_skus = set(linked_skus[channel])
            ignored_skus = set(
                LinkingIgnoredSKU.objects.filter(channel=channel).values_list(
                    "sku", flat=True
                )
            )
            channel_skus = product_skus - ignored_skus - channel_linked_skus
            for sku in channel_skus:
                rows.append(
                    {
                        cls.SOURCE: channel.source,
                        cls.SUBSOURCE: channel.sub_source,
                        cls.LINKED_SKU_CUSTOM_LABEL: sku,
                        cls.SKU: sku,
                    }
                )
        return rows
