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
from .images import DeleteSTCAdminImage, ImageFormView
from .locations import LocationFormView
from .print_barcodes import BarcodePDF, PrintBarcodeLabels
from .product import ProductView
from .productrange import ProductRangeView
from .productsearch import ProductSearchView
from .suppliers import (
    CreateSupplier,
    CreateSupplierContact,
    DeleteSupplierContact,
    Supplier,
    Suppliers,
    ToggleSupplierActive,
    UpdateSupplierContact,
)
from .views import CreateBayView, InventoryUserMixin, SKUGeneratorView

__all__ = [
    "DeleteImage",
    "GetNewRangeSKUView",
    "GetNewSKUView",
    "GetStockForProductView",
    "SetImageOrderView",
    "UpdateStockLevelView",
    "DescriptionsView",
    "DeleteSTCAdminImage",
    "ImageFormView",
    "LocationFormView",
    "BarcodePDF",
    "PrintBarcodeLabels",
    "ProductView",
    "ProductRangeView",
    "ProductSearchView",
    "CreateSupplier",
    "CreateSupplierContact",
    "DeleteSupplierContact",
    "Supplier",
    "Suppliers",
    "ToggleSupplierActive",
    "UpdateSupplierContact",
    "CreateBayView",
    "InventoryUserMixin",
    "SKUGeneratorView",
]
