"""Create, download and save a Cloud Commerce Pro product export."""

import datetime
import tempfile
import time
from pathlib import Path

import pytz
from ccapi import CCAPI
from django.core.files import File
from django.db import models
from tabler import Table


def export_file_path(instance, filename):
    """Return the path at which to save product export files."""
    timestamp = instance.timestamp
    filename = instance.name + ".xlsx"
    return Path("product_exports").joinpath(
        timestamp.strftime("%Y"),
        timestamp.strftime("%m"),
        timestamp.strftime("%d"),
        timestamp.strftime("%H_%M"),
        filename,
    )


class ProductExport(models.Model):
    """Model for Cloud Commerce product export files."""

    name = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField()
    export_file = models.FileField(upload_to=export_file_path)

    class Meta:
        """Meta class for ProductExport."""

        verbose_name = "Product Export"
        verbose_name_plural = "Product Exports"
        ordering = ("-timestamp",)

    def __str__(self):
        return f"Product Export {self.timestamp.strftime('%Y-%m-%d %H-%M')}"

    def as_table(self):
        """Return the export file as a tabler.Table instance."""
        return Table(self.export_file.path)

    @classmethod
    def save_new_export(cls, path=None):
        """Create, download and save a Cloud Commerce Pro product export.

        Args:
            path (pathlib.Path): The path to save the export. If it is a directory the
                export name will be used as a file name.
        """
        export_info = cls._new_export()
        cls._save_export_file(export_info, path)
        return export_info

    @classmethod
    def add_new_export_to_database(cls):
        """Create a new export and add it to the database."""
        directory = tempfile.TemporaryDirectory()
        export_path = Path(directory.name)
        export_info = cls.save_new_export(export_path)
        export_file = export_path / (export_info.file_name + ".xlsx")
        cls._save_to_database(export_file, export_info)
        directory.cleanup()

    @classmethod
    def _save_to_database(cls, path_to_file, export_info):
        """Add an export to the database."""
        tz = pytz.timezone("Europe/London")
        with open(path_to_file, "rb") as f:
            export = cls(
                name=export_info.file_name,
                timestamp=export_info.date_started.replace(tzinfo=tz),
                export_file=f,
            )
            export.export_file = File(f)
            export.save()

    @staticmethod
    def _get_existing_export_IDs():
        """Return the IDs of all existing product exports."""
        existing_exports = CCAPI.get_product_exports().product_exports
        return [export.export_ID for export in existing_exports]

    @staticmethod
    def _sanitise_path(path, default_file_name="Product_Export.xlsx"):
        """Return a corrected path file path for saving the export.

        If the path is None, replace it with the current working directory.
        If the path is a directory append a file name based on the product name.
        """
        if path is None:
            path = Path.cwd()
        if path.is_dir():
            path = path / default_file_name
        return path

    @staticmethod
    def _get_new_export_ID(product_exports, existing_export_IDs):
        """Return the ID of the export whos ID is not in existing_export_IDs."""
        new_export_ID = [
            export
            for export in product_exports
            if export.export_ID not in existing_export_IDs
        ][0].export_ID
        return new_export_ID

    @classmethod
    def _new_export(cls):
        """Return the export info for a newly created product export."""
        existing_export_IDs = cls._get_existing_export_IDs()
        CCAPI.export_products()
        time.sleep(5)
        product_exports = CCAPI.get_product_exports().product_exports
        export_ID = cls._get_new_export_ID(product_exports, existing_export_IDs)
        export_info = cls._get_export_info(export_ID)
        return export_info

    @classmethod
    def _save_export_file(cls, export_info, path):
        """Save a product export file."""
        filename = export_info.file_name + ".xlsx"
        path = cls._sanitise_path(path, default_file_name=filename)
        CCAPI.save_product_export_file(export_info.file_name, path)

    @staticmethod
    def _get_export_info(export_ID):
        """Return information about the new export once available."""
        for _ in range(1000):
            export = CCAPI.get_product_exports().product_exports.get_by_ID(export_ID)
            if export.failed:
                raise Exception("Failed product export.")
            if export.complete:
                break
            time.sleep(10)
        else:
            raise Exception("Exceeded maximum attempts to retrive product export.")
        return export

    def export_data(self):
        """Return an instance of ProductExportData containing the data from this export."""
        return ProductExportData(self)


class ProductExportData:
    """Wrapper for Product Export data."""

    RANGE_SKU = "range_SKU"
    RANGE_NAME = "range_name"
    PRODUCT_TYPE = "product_type"
    SKU = "SKU"
    NAME = "name"
    DESCRIPTION = "description"
    BARCODE = "barcode"
    STOCK_LEVEL = "stock_level"
    PRICE = "price"
    VAT_RATE = "VAT_rate"
    FACTORY = "factory"
    WEIGHT = "weight"
    CC_LENGTH = "cc_length"
    CC_HEIGHT = "cc_height"
    CC_WIDTH = "cc_width"
    LARGE_LETTER_COMPATIBLE = "large_letter_compatible"
    HANDLING_TIME = "handling_time"
    IMAGES = "images"
    BAYS = "bays"
    WOO_CATEGORY_1 = "woo_category_1"
    WOO_CATEGORY_2 = "woo_category_2"
    WOO_CATEGORY_3 = "woo_category_3"
    DESIGN_OPTION = "design_option"
    COLOUR_OPTION = "colour_option"
    SIZE_OPTION = "size_option"
    QUANTITY_OPTION = "quantity_option"
    WEIGHT_OPTION = "weight_option"
    SHAPE_OPTION = "shape_option"
    STRENGTH_OPTION = "strength_option"
    CALIBRE_OPTION = "calibre_option"
    SCENT_OPTION = "scent_option"
    NAME_OPTION = "name_option"
    EXTRAS_OPTION = "extras_option"
    FINISH_OPTION = "finish_option"
    WORD_OPTION = "word_option"
    MODEL_OPTION = "model_option"
    MANUFACTURER = "manufacturer"
    DEPARTMENT = "department"
    BRAND = "brand"
    SUPPLIER_SKU = "supplier_SKU"
    SUPPLIER = "supplier"
    PURCHASE_PRICE = "purchase_price"
    MATERITAL_OPTION = "material_option"
    INTERNTATIONAL_SHIPPING = "international_shipping"
    DISCONTINUED = "discontinued"
    DATE_CREATED = "date_created"
    AMAZON_BULLETS = "amazon_bullets"
    PACKAGE_TYPE = "package_type"
    AMAZON_SEARCH_TERMS = "search_terms"
    GENDER = "gender"
    INCOMPLETE = "incomplete"
    RETAIL_PRICE = "retail_price"
    HEIGHT = "height"
    LENGTH = "length"
    WIDTH = "width"

    attribute_mapping = {
        RANGE_SKU: "RNG_SKU",
        RANGE_NAME: "RNG_Name",
        PRODUCT_TYPE: "VAR_ProductType",
        SKU: "VAR_SKU",
        NAME: "VAR_Name",
        DESCRIPTION: "VAR_Description",
        BARCODE: "VAR_Barcode",
        STOCK_LEVEL: "VAR_Stock",
        PRICE: "VAR_Price_Net",
        VAT_RATE: "VAR_VATRate",
        FACTORY: "VAR_Supplier",
        WEIGHT: "VAR_Weight",
        CC_LENGTH: "VAR_Length",
        CC_HEIGHT: "VAR_Height",
        CC_WIDTH: "VAR_Width",
        LARGE_LETTER_COMPATIBLE: "VAR_LargeLetterCompatible",
        HANDLING_TIME: "VAR_HandlingTime",
        IMAGES: "VAR_IMG",
        BAYS: "VAR_Bays",
        WOO_CATEGORY_1: "OPT_WooCategory1",
        WOO_CATEGORY_2: "OPT_WooCategory2",
        WOO_CATEGORY_3: "OPT_WooCategory3",
        DESIGN_OPTION: "OPT_Design_DRD",
        COLOUR_OPTION: "OPT_Colour_DRD",
        SIZE_OPTION: "OPT_Size_DRD",
        QUANTITY_OPTION: "OPT_Quantity_DRD",
        WEIGHT_OPTION: "OPT_Weight_DRD",
        SHAPE_OPTION: "OPT_Shape_DRD",
        STRENGTH_OPTION: "OPT_Strength_DRD",
        CALIBRE_OPTION: "OPT_Calibre_DRD",
        SCENT_OPTION: "OPT_Scent_DRD",
        NAME_OPTION: "OPT_Name_DRD",
        EXTRAS_OPTION: "OPT_Extras_DRD",
        FINISH_OPTION: "OPT_Finish_DRD",
        WORD_OPTION: "OPT_Word_DRD",
        MODEL_OPTION: "OPT_Model_DRD",
        MANUFACTURER: "OPT_Manufacturer",
        DEPARTMENT: "OPT_Department_MST",
        BRAND: "OPT_Brand",
        SUPPLIER_SKU: "OPT_Supplier SKU",
        SUPPLIER: "OPT_Supplier",
        PURCHASE_PRICE: "OPT_Purchase Price",
        MATERITAL_OPTION: "OPT_Material_DRD",
        INTERNTATIONAL_SHIPPING: "OPT_International Shipping",
        DISCONTINUED: "OPT_Discontinued",
        DATE_CREATED: "OPT_Date Created",
        AMAZON_BULLETS: "OPT_Amazon Bullets",
        PACKAGE_TYPE: "OPT_Package Type",
        AMAZON_SEARCH_TERMS: "OPT_Amazon Search Terms",
        GENDER: "OPT_Gender",
        INCOMPLETE: "OPT_Incomplete",
        RETAIL_PRICE: "OPT_Retail Price",
        HEIGHT: "OPT_Height MM",
        LENGTH: "OPT_Length MM",
        WIDTH: "OPT_Width MM",
    }

    def __init__(self, export):
        """Load data from a Product Export.

        Args:
            export (ProductExport): The ProductExport object from which to load data.

        Attrs:
            export: The ProductExport object from which data is loaded.
            table: A tabler.Table object loaded from the export.
            ranges: A list of ProductExportProductRange objects loaded from the export.
            products: A list of ProductExportProduct objects loaded from the export.
        """
        self.export = export
        self.table = export.as_table()
        self.ranges = self._get_ranges()
        self.products = sum(
            [product_range.products for product_range in self.ranges], []
        )

    def _get_ranges(self):
        ranges = {}
        for row in self.table:
            range_SKU = row[self.attribute_mapping["range_SKU"]]
            if range_SKU not in ranges:
                ranges[range_SKU] = []
            ranges[range_SKU].append(row)
        return [ProductExportProductRange(SKU, rows) for SKU, rows in ranges.items()]

    @staticmethod
    def parse_bays(value):
        """Return a list of bay names parsed from the VAR_Bay field of a Product Export."""
        if value is None:
            return []
        return value.split(";")

    @staticmethod
    def parse_date(value):
        """Return a datetime.datetime object for the Date Created field of a Product Export."""
        if value is None:
            return None
        year, month, day = value.split("-")
        return datetime.date(year=int(year), month=int(month), day=int(day))

    @staticmethod
    def parse_bool(value):
        """Return a boolean version of a string 1 or 0."""
        return bool(int(value))

    @staticmethod
    def parse_barcode(value):
        """Return the primary barcode of the product."""
        if value is None:
            return ""
        return value.split(",")[0]

    @staticmethod
    def parse_currency(value):
        """Return a price value as a string."""
        if value is None:
            return ""
        return str(value)

    parsers = {
        BAYS: parse_bays.__get__(object),
        DATE_CREATED: parse_date.__get__(object),
        LARGE_LETTER_COMPATIBLE: parse_bool.__get__(object),
        BARCODE: parse_barcode.__get__(object),
        PRICE: parse_currency.__get__(object),
        PURCHASE_PRICE: parse_currency.__get__(object),
        RETAIL_PRICE: parse_currency.__get__(object),
        HANDLING_TIME: int,
    }


class ProductExportProductRange:
    """Wrapper for Product Ranges from a Product Export."""

    def __init__(self, SKU, rows):
        """Add products from rows."""
        self.SKU = SKU
        self.rows = rows
        self.products = [ProductExportProduct(row) for row in self.rows]


class ProductExportProduct:
    """Wrapper for Product from a Product Export."""

    def __init__(self, row):
        """Add attributes from an export row according to ProductExportData.attribute_mapping."""
        self.row = row
        for attr, header in ProductExportData.attribute_mapping.items():
            if header in self.row.header:
                value = row[header]
            else:
                value = None
            setattr(self, f"_{attr}", value)

    def __getattribute__(self, name):
        attribute_mapping = ProductExportData.attribute_mapping
        parsers = ProductExportData.parsers
        if name in attribute_mapping:
            value = getattr(self, f"_{name}")
            if name in parsers:
                return parsers[name](value)
            else:
                return value
        else:
            return object.__getattribute__(self, name)

    @property
    def multipack(self):
        """Return True if the product is a mulitpack item, otherwise return False.

        Raises:
            ValueError if the value in the product type field is not recognised.

        """
        product_type = getattr(self, ProductExportData.PRODUCT_TYPE)
        if product_type == "Single":
            return False
        elif product_type == "SimplePack":
            return True
        else:
            raise ValueError(f'Unrecognized product type: "{product_type}".')
