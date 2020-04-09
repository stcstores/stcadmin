"""Views for inventory app."""

from .api import (
    DeleteImage,
    GetNewRangeSKUView,
    GetNewSKUView,
    GetStockForProductView,
    SetImageOrderView,
    UpdateStockLevelView,
)
from .descriptions import DescriptionsView
from .images import ImageFormView
from .locations import LocationFormView
from .print_barcodes import BarcodePDF, PrintBarcodeLabels
from .product import ProductView
from .productrange import ProductRangeView
from .productsearch import AdvancedSearch, InventorySearch
from .suppliers import (
    CreateSupplier,
    CreateSupplierContact,
    DeleteSupplierContact,
    Supplier,
    Suppliers,
    ToggleSupplierActive,
    UpdateSupplierContact,
)
from .views import CreateBayView, Index, InventoryUserMixin, SKUGeneratorView

__all__ = [
    "DeleteImage",
    "GetNewRangeSKUView",
    "GetNewSKUView",
    "GetStockForProductView",
    "SetImageOrderView",
    "UpdateStockLevelView",
    "DescriptionsView",
    "ImageFormView",
    "LocationFormView",
    "BarcodePDF",
    "PrintBarcodeLabels",
    "ProductView",
    "ProductRangeView",
    "AdvancedSearch",
    "InventorySearch",
    "CreateSupplier",
    "CreateSupplierContact",
    "DeleteSupplierContact",
    "Supplier",
    "Suppliers",
    "ToggleSupplierActive",
    "UpdateSupplierContact",
    "CreateBayView",
    "Index",
    "InventoryUserMixin",
    "SKUGeneratorView",
]
