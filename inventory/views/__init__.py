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
    Continue,
    CreateInitialVariation,
    CreateVariation,
    DeleteVariation,
    DiscardChanges,
    EditAllVariations,
    EditProduct,
    EditRangeDetails,
    EditVariation,
    EditVariations,
    RemoveDropdown,
    RemoveProductOptionValue,
    SaveChanges,
    SetProductOptionValues,
    SetupVariations,
    StartEditingProduct,
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
from .variations import VariationsView
from .views import (
    CreateBayView,
    InventoryUserMixin,
    ProductSearchView,
    SKUGeneratorView,
)

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
    "DiscardChanges",
    "EditAllVariations",
    "EditProduct",
    "EditRangeDetails",
    "EditVariation",
    "EditVariations",
    "RemoveDropdown",
    "RemoveProductOptionValue",
    "SaveChanges",
    "SetProductOptionValues",
    "SetupVariations",
    "StartEditingProduct",
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
    "VariationsView",
    "CreateBayView",
    "InventoryUserMixin",
    "ProductSearchView",
    "SKUGeneratorView",
]
