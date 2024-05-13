"""Models for the inventory app."""

from .barcode import Barcode
from .location import Bay, ProductBayHistory, ProductBayLink
from .product import (
    BaseProduct,
    CombinationProduct,
    CombinationProductLink,
    EndOfLineReason,
    InitialVariation,
    MultipackProduct,
    Product,
    new_product_sku,
    new_range_sku,
)
from .product_attribute import (
    Brand,
    ListingAttribute,
    ListingAttributeValue,
    Manufacturer,
    PackageType,
    VariationOption,
    VariationOptionValue,
    VATRate,
)
from .product_image import ProductImage, ProductImageLink, ProductRangeImageLink
from .product_range import ProductRange
from .stock_change import StockLevelHistory
from .supplier import Supplier, SupplierContact

__all__ = [
    "Barcode",
    "BaseProduct",
    "Bay",
    "Brand",
    "CombinationProduct",
    "CombinationProductLink",
    "EndOfLineReason",
    "ListingAttribute",
    "ListingAttributeValue",
    "Manufacturer",
    "InitialVariation",
    "MultipackProduct",
    "PackageType",
    "Product",
    "ProductBayHistory",
    "ProductBayLink",
    "ProductExport",
    "ProductImage",
    "ProductImageLink",
    "ProductRangeImageLink",
    "ProductRange",
    "StockLevelHistory",
    "Supplier",
    "SupplierContact",
    "VATRate",
    "VariationOption",
    "VariationOptionValue",
    "new_product_sku",
    "new_range_sku",
]
