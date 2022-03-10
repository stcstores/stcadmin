"""Models for the inventory app."""

from .barcodes import Barcode
from .location import Bay, ProductBayHistory, ProductBayLink
from .product import (
    Brand,
    CombinationProduct,
    Gender,
    ListingAttribute,
    ListingAttributeValue,
    Manufacturer,
    MultipackProduct,
    PackageType,
    Product,
    ProductRange,
    SingleProduct,
    VariationOption,
    VariationOptionValue,
    VariationProduct,
    VATRate,
    new_product_sku,
    new_range_sku,
)
from .product_exports import ProductExport
from .product_image import ProductImage
from .stock_change import StockChange
from .suppliers import Supplier, SupplierContact

__all__ = [
    "Barcode",
    "ProductImage",
    "Bay",
    "ProductBayHistory",
    "ProductBayLink",
    "ProductExport",
    "ProductImage",
    "Brand",
    "CombinationProduct",
    "Manufacturer",
    "MultipackProduct",
    "Gender",
    "ListingAttribute",
    "ListingAttributeValue",
    "VariationOption",
    "VariationOptionValue",
    "VariationProduct",
    "VATRate",
    "new_product_sku",
    "new_range_sku",
    "PackageType",
    "Product",
    "ProductRange",
    "SingleProduct",
    "StockChange",
    "Supplier",
    "SupplierContact",
]
