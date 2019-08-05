"""Views for inventory app."""

from .api import *  # NOQA
from .descriptions import DescriptionsView  # NOQA
from .images import ImageFormView  # NOQA
from .locations import LocationFormView  # NOQA
from .print_barcodes import BarcodePDF, PrintBarcodeLabels  # NOQA
from .product import ProductView  # NOQA
from .product_editor import (  # NOQA
    AddDropdown,
    AddDropdownValues,
    AddProductOptionValues,
    Continue,
    CreateVariation,
    DeleteVariation,
    DiscardChanges,
    EditAllVariations,
    EditProduct,
    EditRangeDetails,
    EditVariation,
    EditVariations,
    RemoveProductOptionValue,
    StartEditingProduct,
)
from .product_order import ProductOrderView  # NOQA
from .productrange import ProductRangeView  # NOQA
from .productsearch import ProductSearchView  # NOQA
from .suppliers import (  # NOQA
    CreateSupplier,
    CreateSupplierContact,
    DeleteSupplierContact,
    Supplier,
    Suppliers,
    ToggleSupplierActive,
    UpdateSupplierContact,
)
from .variations import VariationsView  # NOQA
from .views import *  # NOQA
