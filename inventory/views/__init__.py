"""Views for inventory app."""

from .api import (
    DeleteImage,
    GetNewRangeSKUView,
    GetNewSKUView,
    GetStockLevelView,
    SetImageOrderView,
    UpdateStockLevelView,
)
from .descriptions import DescriptionsView
from .images import ImageFormView
from .locations import LocationFormView
from .print_barcodes import BarcodePDF, PrintBarcodeLabels
from .product import ProductView
from .product_editor import (
    AddDropdown,
    AddListingOption,
    AddProductOptionValues,
    CompleteNewProduct,
    Continue,
    CreateInitialVariation,
    CreateVariation,
    DeleteVariation,
    DiscardNewRange,
    EditAllVariations,
    EditNewProduct,
    EditProduct,
    EditRangeDetails,
    EditVariation,
    EditVariations,
    RemoveDropdown,
    RemoveProductOptionValue,
    ResumeEditingProduct,
    SetProductOptionValues,
    SetupVariations,
    StartNewProduct,
)
from .product_order import ProductOrderView
from .productrange import ProductRangeView
from .suppliers import (
    CreateSupplier,
    CreateSupplierContact,
    DeleteSupplierContact,
    Supplier,
    Suppliers,
    ToggleSupplierActive,
    UpdateSupplierContact,
)
from .views import InventoryUserMixin, ProductSearchView, SKUGeneratorView

__all__ = [
    "DeleteImage",
    "GetNewRangeSKUView",
    "GetNewSKUView",
    "GetStockLevelView",
    "SetImageOrderView",
    "UpdateStockLevelView",
    "DescriptionsView",
    "ImageFormView",
    "LocationFormView",
    "BarcodePDF",
    "PrintBarcodeLabels",
    "ProductView",
    "AddDropdown",
    "AddListingOption",
    "AddProductOptionValues",
    "Continue",
    "CreateInitialVariation",
    "CreateVariation",
    "DeleteVariation",
    "DiscardNewRange",
    "EditAllVariations",
    "EditProduct",
    "EditRangeDetails",
    "EditVariation",
    "EditVariations",
    "EditNewProduct",
    "RemoveDropdown",
    "RemoveProductOptionValue",
    "ResumeEditingProduct",
    "CompleteNewProduct",
    "SetProductOptionValues",
    "SetupVariations",
    "StartNewProduct",
    "ProductOrderView",
    "ProductRangeView",
    "CreateSupplier",
    "CreateSupplierContact",
    "DeleteSupplierContact",
    "Supplier",
    "Suppliers",
    "ToggleSupplierActive",
    "UpdateSupplierContact",
    "InventoryUserMixin",
    "ProductSearchView",
    "SKUGeneratorView",
]
