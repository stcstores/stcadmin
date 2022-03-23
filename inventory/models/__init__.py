"""Models for the inventory app."""

from .barcode import Barcode
from .location import Bay, ProductBayHistory, ProductBayLink
from .product import (
    BaseProduct,
    CombinationProduct,
    CombinationProductLink,
    InitialVariation,
    MultipackProduct,
    Product,
    new_product_sku,
    new_range_sku,
)
from .product_attribute import (
    Brand,
    Gender,
    ListingAttribute,
    ListingAttributeValue,
    Manufacturer,
    PackageType,
    VariationOption,
    VariationOptionValue,
    VATRate,
)
from .product_export import ProductExport
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
    "Gender",
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
    "ProductRange",
    "ProductRangeImageLink",
    "StockLevelHistory",
    "Supplier",
    "SupplierContact",
    "VATRate",
    "VariationOption",
    "VariationOptionValue",
    "new_product_sku",
    "new_range_sku",
]
