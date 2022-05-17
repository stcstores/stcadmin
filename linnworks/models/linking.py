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

    prime_identifers = ["_PRIME", "_PRIME2"]

    header = (SOURCE, SUBSOURCE, LINKED_SKU_CUSTOM_LABEL, SKU)

    @classmethod
    def create(cls):
        """Create a Linnworks Product Import file."""
        channels = LinnworksChannel.objects.all().order_by("source", "sub_source")
        product_skus = cls.product_skus()
        channel_items_file = ChannelItemsExport()
        linked_skus = cls.linked_skus(channel_items_file)
        prime_rows = cls.prime_rows(channel_items_file)
        return cls.create_file(
            channels=channels,
            product_skus=product_skus,
            linked_skus=linked_skus,
            prime_rows=prime_rows,
        )

    @classmethod
    def product_skus(cls):
        """Return a set of all SKUs on Linnworks."""
        skus = BaseProduct.objects.variations().active().values_list("sku", flat=True)
        return set(skus)

    @classmethod
    def linked_skus(cls, channel_items_file):
        """Return a dict of linnworks.models.LinnworksChannel to a list of linked SKUs."""
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
    def prime_rows(cls, channel_items_file):
        """Return a list of prime SKUs to link."""
        prime_channels = LinnworksChannel.objects.filter(link_prime=True)
        prime_rows = []
        for channel in prime_channels:
            linked_skus = []
            unlinked_skus = {}
            for row in channel_items_file.rows:
                if (
                    row[channel_items_file.SOURCE] != channel.source
                    or row[channel_items_file.SUBSOURCE] != channel.sub_source
                ):
                    continue
                channel_sku = row[channel_items_file.LINKED_SKU_CUSTOM_LABEL]
                if cls.prime_identifers[0] in channel_sku:
                    linked_skus.append(channel_sku)
                else:
                    unlinked_skus[channel_sku] = row[channel_items_file.SKU]
            linked_skus = set(linked_skus)
            for channel_sku, linnworks_sku in unlinked_skus.items():
                for identifer in cls.prime_identifers:
                    link_sku = f"{channel_sku}{identifer}"
                    if link_sku not in linked_skus:
                        prime_rows.append(
                            {
                                cls.SOURCE: channel.source,
                                cls.SUBSOURCE: channel.sub_source,
                                cls.LINKED_SKU_CUSTOM_LABEL: link_sku,
                                cls.SKU: linnworks_sku,
                            }
                        )
        return prime_rows

    @classmethod
    def get_row_data(cls, channels, product_skus, linked_skus, prime_rows):
        """Return a list of channel item dicts."""
        rows = list(prime_rows)
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
