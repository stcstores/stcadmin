"""Models for the inventory app."""

from .barcode import Barcode
from .location import Bay, ProductBayHistory, ProductBayLink
from .product import (
    BaseProduct,
    CombinationProduct,
    CombinationProductLink,
    MultipackProduct,
    Product,
    ProductRange,
    SingleProduct,
    VariationProduct,
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
from .stock_change import StockChange
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
    "MultipackProduct",
    "PackageType",
    "Product",
    "ProductBayHistory",
    "ProductBayLink",
    "ProductExport",
    "ProductImage",
    "ProductImage",
    "ProductImageLink",
    "ProductRange",
    "ProductRangeImageLink",
    "SingleProduct",
    "StockChange",
    "Supplier",
    "SupplierContact",
    "VATRate",
    "VariationOption",
    "VariationOptionValue",
    "VariationProduct",
    "new_product_sku",
    "new_range_sku",
]
