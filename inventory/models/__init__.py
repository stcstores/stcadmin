"""Models for inventory app."""

from . barcodes import Barcode, get_barcode  # NOQA
from . stcadmin_image import STCAdminImage, get_product_image_upload_to  # NOQA
from . locations import Warehouse, Bay, check_location_integrity  # NOQA
