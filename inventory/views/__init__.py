"""Views for inventory app."""
from .api import (
    GetNewRangeSKUView,
    GetNewSKUView,
    NewBrand,
    NewManufacturer,
    NewSupplier,
)
from .descriptions import DescriptionsView
from .images import ImageFormView
from .locations import BaySearch, LocationFormView
from .product import ProductView
from .product_editor import (
    CompleteNewProduct,
    Continue,
    CreateInitialVariation,
    DiscardNewRange,
    EditAllVariations,
    EditNewProduct,
    EditNewVariation,
    EditRangeDetails,
    ResumeEditingProduct,
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
    "NewBrand",
    "NewManufacturer",
    "NewSupplier",
    "SetImageOrderView",
    "DescriptionsView",
    "ImageFormView",
    "LocationFormView",
    "ProductView",
    "Continue",
    "CreateInitialVariation",
    "DiscardNewRange",
    "EditAllVariations",
    "EditRangeDetails",
    "EditNewVariation",
    "EditNewProduct",
    "ResumeEditingProduct",
    "CompleteNewProduct",
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
    "BaySearch",
    "restock",
]
