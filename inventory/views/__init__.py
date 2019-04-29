"""Views for inventory app."""

from .api import *  # NOQA
from .descriptions import DescriptionsView  # NOQA
from .images import DeleteSTCAdminImage, ImageFormView  # NOQA
from .locations import LocationFormView  # NOQA
from .print_barcodes import BarcodePDF, PrintBarcodeLabels  # NOQA
from .product import ProductView  # NOQA
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
from .views import *  # NOQA
