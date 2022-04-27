"""Models for managing exports from Linnworks."""

import csv
from pathlib import Path

from .config import LinnworksConfig


class BaseExportFile:
    """Base class for Linnworks export files."""

    def __init__(self):
        """Open a .csv file and load headers and rows."""
        self.header, self.rows = self.read_file()

    def get_file_path(self):
        """Override this method to return the path of the export file."""
        raise NotImplementedError

    def read_file(self):
        """
        Return the file header and row data.

        Returns:
            list[str]: The header row from the csv file.
            list[dict[str: Any]]: A list of dicts where each item is a row in the csv
                file as a dict of column headers and values.
        """
        rows = []
        with open(self.get_file_path(), "r", encoding="utf8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    header = row
                else:
                    row_dict = {key: value for key, value in zip(header, row)}
                    rows.append(row_dict)
        return header, rows


class ChannelItemsExport(BaseExportFile):
    """Model for reading Linnworks channel item exports."""

    CHANNEL_REFERENCE_ID = "Channel Reference Id"
    SOURCE = "Source"
    SUBSOURCE = "Subsource"
    LINKED_SKU_CUSTOM_LABEL = "Linked SKU Custom Label"  # Channel SKU
    CHANNEL_TITLE = "Channel Title"
    SKU = "SKU"  # Linnworks SKU
    LINNWORKS_TITLE = "Linnworks Title"
    STOCK_PERCENTAGE = "Stock Percentage"
    MAX_LISTED_QUANTITY = "Max Listed Quantity"
    END_WHEN_STOCK = "End When Stock"
    IGNORE_SYNC = "Ignore Sync"

    def get_file_path(self):
        """Return the path to the latest channels items export file."""
        config = LinnworksConfig.get_solo()
        channel_items_export_dir = config.channel_items_export_file_path
        exports = sorted(list(Path(channel_items_export_dir).iterdir()))
        return exports[-1]
