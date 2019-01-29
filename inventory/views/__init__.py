"""Views for inventory app."""

from .views import *  # NOQA
from .api import *  # NOQA
from .descriptions import DescriptionsView  # NOQA
from .images import ImageFormView, DeleteSTCAdminImage  # NOQA
from .locations import LocationFormView  # NOQA
from .print_barcodes import PrintBarcodeLabels, BarcodePDF  # NOQA
from .product import ProductView  # NOQA
from .productrange import ProductRangeView  # NOQA
from .productsearch import ProductSearchView  # NOQA
from .suppliers import (  # NOQA
    Suppliers,
    Supplier,
    CreateSupplier,
    ToggleSupplierActive,
    UpdateSupplierContact,
    CreateSupplierContact,
    DeleteSupplierContact,
)
