"""Models for creating Linnworks import files."""

import csv
import io
from collections import defaultdict

from inventory.models import CombinationProductLink, MultipackProduct, Product
from inventory.models.product import CombinationProduct
from linnworks.models.stock_manager import InitialStockLevel


class CSVFile:
    """Provides methods for handling CSV files."""

    def __init__(self, rows, header=None, dialect="excel"):
        """
        Create a CSVFile.

        Kwargs:
            rows (list[list[Any]]): The rows of the csv file as a list of rows, each
                row being a list of values.
            header (tuple[str] | None): The csv file header as a tuple of row headers
                or None if the file has no header row.
            dialect: The dialect kwarg passed to csv.writer when writing files.
        """
        self.header = header
        self.rows = rows
        self.dialect = dialect

    def write(self, fileobj):
        """Stream the CSV file to file-like object."""
        writer = csv.writer(
            fileobj,
            delimiter=",",
            lineterminator="\n",
            quoting=csv.QUOTE_NONNUMERIC,
        )
        if self.header is not None:
            writer.writerow(self.header)
        writer.writerows(self.rows)

    def to_string_io(self):
        """Return the CSV file as io.StringIO."""
        f = io.StringIO()
        self.write(f)
        return f

    def to_string(self):
        """Return the CSV file as a string."""
        return self.to_string_io().getvalue()


class BaseImportFile:
    """Base class for Linnworks import files."""

    header = tuple()

    @classmethod
    def get_row_data(cls, *args, **kwargs):
        """
        Override this method to return a list rows in the form [{header: value}].

        Raises:
            NotImplementedError: This method must be overriden by subclasses.
        """
        raise NotImplementedError()

    @classmethod
    def post_creation(cls, *args, **kwargs):
        """Override this method to add operations after file creation."""
        pass

    @classmethod
    def create_file(cls, *args, **kwargs):
        """Return a list of lists of row values."""
        row_data = cls.get_row_data(*args, **kwargs)
        rows = [[row.get(h, "") for h in cls.header] for row in row_data]
        csv_file = CSVFile(rows=rows, header=cls.header)
        cls.post_creation(*args, **kwargs)
        return csv_file


class LinnworksProductImportFile(BaseImportFile):
    """Create Linnworks product import files."""

    SKU = "SKU"
    TITLE = "Title"
    SHORT_DESCRIPTION = "Short Description"
    BARCODE_NUMBER = "Barcode number"
    TAX_RATE = "Tax Rate"
    WEIGHT = "Weight"
    HEIGHT = "Height"
    WIDTH = "Width"
    DEPTH = "Depth"
    PACKAGING_GROUP = "Packaging Group"
    PURCHASE_PRICE = "Purchase Price"
    RETAIL_PRICE = "Retail Price"
    LOCATION = "Location"
    STOCK_LEVEL = "Stock Level"
    DEFAULT_SUPPLIER = "Default Supplier"
    SUPPLIER_BARCODE = "Supplier Barcode"
    SUPPLIER_CODE = "Supplier Code"
    SUPPLIER_NAME = "Supplier Name"
    SUPPLIER_PURCHASE_PRICE = "Supplier Purchase Price"
    BATCH_TYPE = "Batch Type"
    BIN_RACK = "Bin Rack"
    ARCHIVED = "Archived"
    IS_VARIATION_GROUP = "Is Variation Group"
    VARIATION_SKU = "Variation SKU"
    VARIATION_GROUP_NAME = "Variation Group Name"
    HS_CODE = "HS Code"
    COUNTRY_OF_ORIGIN = "CountryOfOrigin"
    MANUFACTURER = "Manufacturer"
    BRAND = "Brand"
    MATERIAL = "Material"
    INTERNATIONAL_SHIPPING = "International Shipping"
    DATE_CREATED = "Date Created"
    AMAZON_BULLETS = "Amazon Bullets"
    AMAZON_SEARCH_TERMS = "Amazon Search Terms"
    CREATED_BY = "Created By"
    COLOUR = "Colour"
    SIZE = "Size"
    DESIGN = "Design"
    QUANTITY = "Quantity"
    SHAPE = "Shape"
    ITEM_WEIGHT = "Item Weight"
    STRENGTH = "Strength"
    SCENT = "Scent"
    NAME = "Name"
    EXTRAS = "Extras"
    FINISH = "Finish"
    WORD = "Word"
    MODEL = "Model"
    CALIBRE = "Calibre"

    header = (
        SKU,
        TITLE,
        SHORT_DESCRIPTION,
        BARCODE_NUMBER,
        TAX_RATE,
        WEIGHT,
        HEIGHT,
        WIDTH,
        DEPTH,
        PACKAGING_GROUP,
        PURCHASE_PRICE,
        RETAIL_PRICE,
        LOCATION,
        STOCK_LEVEL,
        DEFAULT_SUPPLIER,
        SUPPLIER_BARCODE,
        SUPPLIER_CODE,
        SUPPLIER_NAME,
        SUPPLIER_PURCHASE_PRICE,
        BATCH_TYPE,
        BIN_RACK,
        ARCHIVED,
        IS_VARIATION_GROUP,
        VARIATION_SKU,
        VARIATION_GROUP_NAME,
        HS_CODE,
        COUNTRY_OF_ORIGIN,
        MANUFACTURER,
        INTERNATIONAL_SHIPPING,
        DATE_CREATED,
        AMAZON_BULLETS,
        AMAZON_SEARCH_TERMS,
        CREATED_BY,
        BRAND,
        COLOUR,
        SIZE,
        DESIGN,
        QUANTITY,
        SHAPE,
        ITEM_WEIGHT,
        STRENGTH,
        SCENT,
        NAME,
        EXTRAS,
        FINISH,
        WORD,
        MODEL,
        MATERIAL,
        CALIBRE,
    )

    EMPTY_BAY_STRING = "NO BAY"

    @classmethod
    def create(cls):
        """Create a Linnworks Product Import file."""
        return cls.create_file(product_ranges=cls.get_product_ranges())

    @classmethod
    def post_creation(cls, product_ranges):
        """Clear updated SKUs from the initial stock level table."""
        skus = []
        for range_products in product_ranges.values():
            for product in range_products:
                skus.append(product.sku)
        InitialStockLevel.objects.filter(sku__in=set(skus)).delete()

    @classmethod
    def get_product_ranges(cls):
        """Return a dict of productrange: list(products)."""
        product_ranges = defaultdict(list)
        products = list(
            Product.objects.variations()
            .active()
            .complete()
            .select_related(
                "product_range",
                "supplier",
                "brand",
                "manufacturer",
                "package_type",
                "vat_rate",
            )
            .prefetch_related(
                "product_bay_links",
                "product_bay_links__bay",
                "variation_option_values",
                "variation_option_values__variation_option",
                "listing_attribute_values",
                "listing_attribute_values__listing_attribute",
            )
        )
        products.extend(
            MultipackProduct.objects.variations()
            .active()
            .select_related(
                "product_range",
                "supplier",
                "package_type",
                "base_product",
                "base_product__brand",
                "base_product__manufacturer",
                "base_product__vat_rate",
            )
            .prefetch_related(
                "variation_option_values",
                "variation_option_values__variation_option",
                "listing_attribute_values",
                "listing_attribute_values__listing_attribute",
            )
        )
        products.extend(
            CombinationProduct.objects.variations()
            .active()
            .select_related(
                "product_range",
                "supplier",
                "package_type",
            )
            .prefetch_related(
                "variation_option_values",
                "variation_option_values__variation_option",
                "listing_attribute_values",
                "listing_attribute_values__listing_attribute",
                "combination_product_links",
                "combination_product_links__product",
            )
        )
        for product in products:
            product_ranges[product.product_range].append(product)
        return product_ranges

    @classmethod
    def _get_default_row(cls):
        return {cls.INTERNATIONAL_SHIPPING: "Standard", cls.COUNTRY_OF_ORIGIN: "CHN"}

    @classmethod
    def _get_product_range_row(cls, product_range):
        row = cls._get_default_row()
        row[cls.SKU] = product_range.sku
        row[cls.TITLE] = product_range.name
        row[cls.SHORT_DESCRIPTION] = product_range.description
        row[cls.IS_VARIATION_GROUP] = "YES"
        row[cls.VARIATION_SKU] = product_range.sku
        row[cls.VARIATION_GROUP_NAME] = product_range.name
        row[cls.ARCHIVED] = "YES" if product_range.is_end_of_line else "NO"
        row[cls.AMAZON_BULLETS] = "|".join(product_range.bullet_points)
        row[cls.AMAZON_SEARCH_TERMS] = "|".join(product_range.search_terms)
        row[cls.DATE_CREATED] = product_range.created_at.isoformat()
        return row

    @classmethod
    def _get_bin_rack(cls, product):
        """Return the product's bays as a comma separated list."""
        bay_links = product.product_bay_links.all()
        bays = [link.bay.name for link in bay_links]
        bay_text = ", ".join(bays) or cls.EMPTY_BAY_STRING
        return bay_text

    @classmethod
    def convert_dimension(self, distance_mm):
        """Convert dimensions in mm to cm."""
        if distance_mm is None:
            return 1
        cm = int(distance_mm / 10)
        if cm < 1:
            return 1
        return cm

    @classmethod
    def _get_product_row(cls, product):
        row = cls._get_default_row()
        try:
            initial_stock_level = InitialStockLevel.objects.get(
                sku=product.sku
            ).stock_level
        except InitialStockLevel.DoesNotExist:
            initial_stock_level = None
        row[cls.SKU] = product.sku
        row[cls.TITLE] = product.full_name
        row[cls.SHORT_DESCRIPTION] = product.product_range.description
        row[cls.BARCODE_NUMBER] = product.barcode
        row[cls.TAX_RATE] = int(product.vat_rate.percentage * 100)
        row[cls.WEIGHT] = product.weight_grams
        row[cls.HEIGHT] = cls.convert_dimension(product.height_mm)
        row[cls.WIDTH] = cls.convert_dimension(product.width_mm)
        row[cls.DEPTH] = cls.convert_dimension(product.length_mm)
        row[cls.PACKAGING_GROUP] = product.package_type.name
        row[cls.PURCHASE_PRICE] = product.purchase_price
        row[cls.RETAIL_PRICE] = product.retail_price
        row[cls.DEFAULT_SUPPLIER] = "YES"
        row[cls.SUPPLIER_BARCODE] = product.supplier_barcode
        row[cls.SUPPLIER_CODE] = product.supplier_sku
        row[cls.SUPPLIER_NAME] = product.supplier.name
        row[cls.SUPPLIER_PURCHASE_PRICE] = product.purchase_price
        row[cls.BIN_RACK] = cls._get_bin_rack(product)
        row[cls.ARCHIVED] = "YES" if product.is_end_of_line else "NO"
        row[cls.IS_VARIATION_GROUP] = "NO"
        row[cls.VARIATION_SKU] = product.product_range.sku
        row[cls.HS_CODE] = product.hs_code
        row[cls.MANUFACTURER] = product.manufacturer.name
        row[cls.BRAND] = product.brand.name
        row[cls.DATE_CREATED] = product.created_at.isoformat()
        row[cls.AMAZON_BULLETS] = "|".join(product.product_range.bullet_points)
        row[cls.AMAZON_SEARCH_TERMS] = "|".join(product.product_range.search_terms)
        product_attributes = product.attributes()
        if missing_attributes := set(product_attributes.keys()) - set(cls.header):
            raise ValueError(
                f'Product attributes "{list(missing_attributes)}" not recognised.'
            )
        for attribute, value in product_attributes.items():
            row[attribute] = value
        if initial_stock_level is not None and initial_stock_level != 0:
            row[cls.STOCK_LEVEL] = initial_stock_level
        return row

    @classmethod
    def get_row_data(cls, product_ranges):
        """
        Return a list of product row dicts.

        Args:
            product_ranges (dict[models.ProductRange, list[models.BaseProduct]]): A
                dict with product ranges as the key and a list of it's products to
                be exported as values.

        Returns:
            list[dict[str,Any]]: A list of dicts of column headers and values.
        """
        rows = []
        for product_range, products in product_ranges.items():
            rows.append(cls._get_product_range_row(product_range=product_range))
            for product in products:
                rows.append(cls._get_product_row(product))
        return rows


class LinnworksCompostitionImportFile(BaseImportFile):
    """Create Linnworks composition product import files."""

    PARENT_SKU = "Parent SKU"
    CHILD_SKU = "Child SKU"
    QUANTITY = "Quantity"

    header = (PARENT_SKU, CHILD_SKU, QUANTITY)

    @classmethod
    def create(cls):
        """Create a Linnworks Composition Import File."""
        combination_product_links = CombinationProductLink.objects.all().select_related(
            "product", "combination_product"
        )
        multipack_products = (
            MultipackProduct.objects.active().complete().select_related("base_product")
        )
        return cls.create_file(
            combination_product_links=combination_product_links,
            multipack_products=multipack_products,
        )

    @classmethod
    def _get_combination_product_row(cls, combination_product_link):
        return {
            cls.PARENT_SKU: combination_product_link.combination_product.sku,
            cls.CHILD_SKU: combination_product_link.product.sku,
            cls.QUANTITY: combination_product_link.quantity,
        }

    @classmethod
    def _get_multipack_product_row(cls, multipack_product):
        return {
            cls.CHILD_SKU: multipack_product.base_product.sku,
            cls.PARENT_SKU: multipack_product.sku,
            cls.QUANTITY: multipack_product.quantity,
        }

    @classmethod
    def get_row_data(cls, combination_product_links, multipack_products):
        """
        Return a list of product row dicts.

        Args:
            product_ranges (dict[models.ProductRange, list[models.BaseProduct]]): A
                dict with product ranges as the key and a list of it's products to
                be exported as values.

        Returns:
            list[dict[str,Any]]: A list of dicts of column headers and values.
        """
        rows = []
        for combination_product_link in combination_product_links:
            rows.append(cls._get_combination_product_row(combination_product_link))
        for multipack_product in multipack_products:
            rows.append(cls._get_multipack_product_row(multipack_product))
        return rows
