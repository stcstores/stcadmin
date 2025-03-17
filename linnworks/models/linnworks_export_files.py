"""Models for managing exports from Linnworks."""

import csv
import datetime as dt
from pathlib import Path

import pytz

from .config import LinnworksConfig


class BaseExportFile:
    """Base class for Linnworks export files."""

    filename_date = False

    def __init__(self, file_path=None):
        """Open a .csv file and load headers and rows."""
        self.file_path = file_path or self.get_file_path()
        if self.filename_date:
            self.export_date = self.parse_filename_date(self.file_path)
        self.header, self.rows = self.read_file(self.file_path)

    @staticmethod
    def parse_filename_date(filepath):
        """Return a date from an export filepath."""
        date_string = filepath.stem.split("_")[-1]
        year = int(date_string[:4])
        month = int(date_string[4:6])
        day = int(date_string[6:8])
        hour = int(date_string[8:10])
        minute = int(date_string[10:12])
        second = int(date_string[12:14])
        return dt.datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            tzinfo=pytz.UTC,
        )

    def get_file_path(self):
        """Override this method to return the path of the export file."""
        raise NotImplementedError

    def read_file(self, file_path):
        """
        Return the file header and row data.

        Returns:
            list[str]: The header row from the csv file.
            list[dict[str: Any]]: A list of dicts where each item is a row in the csv
                file as a dict of column headers and values.
        """
        rows = []
        with open(file_path, "r", encoding="utf8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == 0:
                    header = row
                else:
                    row_dict = {
                        key: value for key, value in zip(header, row, strict=True)
                    }
                    rows.append(row_dict)
        return header, rows


class ChannelItemsExport(BaseExportFile):
    """Model for reading Linnworks channel item exports."""

    filename_date = True

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


class InventoryExport(BaseExportFile):
    """Model for reading Linnworks inventory exports."""

    filename_date = True

    SKU = "SKU"
    ITEM_TITLE = "Item Title"
    SHORT_DESCRIPTION = "Short Description"
    RETAIL_PRICE = "Retail Price"
    PURCHASE_PRICE = "Purchase Price"
    CATEGORY = "Category"
    WEIGHT = "Weight"
    HEIGHT = "Height"
    DIM_WIDTH = "Dim Width"
    DEPTH = "Depth"
    TAX_RATE = "Tax Rate"
    DEFAULT_POSTAL_SERVICE = "Default Postal Service"
    DEFAULT_PACKAGING_GROUP = "Default Packaging Group"
    IS_VARIATION_PARENT = "Is Variation Parent"
    IS_ARCHIVED = "Is Archived"
    BARCODE_NUMBER = "Barcode Number"
    STOCK_LOCATION = "Stock Location"
    STOCK_AVAILABLE_LEVEL_AT_LOCATION = "Stock available level at location"
    STOCK_IN_ORDER_BOOK_AT_LOCATION = "Stock in order book at location"
    STOCK_LEVEL_AT_LOCATION = "Stock level at location"
    STOCK_VALUE_AT_LOCATION = "Stock value at location"
    STOCK_MINIMUM_LEVEL_AT_LOCATION = "Stock minimum level at location"
    STOCK_DUE_AT_LOCATION = "Stock due at location"
    BIN_RACK = "Bin Rack"
    BRAND = "Brand"
    DATE_CREATED = "Date Created"
    HS_CODE = "HS Code"
    INTERNATIONAL_SHIPPING = "International Shipping"
    MANUFACTURER = "Manufacturer"
    COLOUR = "Colour"
    AMAZON_BULLETS = "Amazon Bullets"
    AMAZON_SEARCH_TERMS = "Amazon Search Terms"
    CALIBRE = "Calibre"
    COMMODITYCODE = "CommodityCode"
    COUNTRY_OF_ORIGIN = "Country of Origin"
    COUNTRYOFORIGIN = "CountryOfOrigin"
    DATE_CREATED = "Date Created"
    DESIGN = "Design"
    EXTRAS = "Extras"
    FINISH = "Finish"
    HS_CODE = "HS Code"
    INTERNATIONAL_SHIPPING = "International Shipping"
    ITEM_WEIGHT = "Item Weight"
    MATERIAL = "Material"
    MODEL = "Model"
    NAME = "Name"
    QUANTITY = "Quantity"
    SCENT = "Scent"
    SHAPE = "Shape"
    SIZE = "Size"
    STRENGTH = "Strength"
    WORD = "Word"

    def get_file_path(self):
        """Return the path to the latest inventory export."""
        config = LinnworksConfig.get_solo()
        inventory_export_file_dir = config.inventory_export_file_path
        exports = sorted(list(Path(inventory_export_file_dir).iterdir()))
        return exports[-1]


class StockLevelExport(BaseExportFile):
    """Model for reading Linnworks stock level exports."""

    filename_date = True

    SKU = "SKU"
    TITLE = "Title"
    LOCATION = "Location"
    QUANTITY = "Quantity"
    BINRACK = "BinRack"
    STOCK_VALUE = "Stock Value"
    IN_ORDER_BOOK = "In Order Book"
    IS_COMPOSITE_PARENT = "Is Composite Parent"

    TRUE = "True"
    FALSE = "False"

    def get_file_path(self):
        """Return the path to the latest inventory export."""
        config = LinnworksConfig.get_solo()
        stock_level_export_file_dir = config.stock_level_export_file_path
        exports = sorted(list(Path(stock_level_export_file_dir).iterdir()))
        return exports[-1]
