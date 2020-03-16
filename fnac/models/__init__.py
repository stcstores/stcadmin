"""Models for the fnac app."""

from .category import Category
from .fnac_product import FnacProduct
from .fnac_range import FnacRange
from .inventory_update import update_inventory
from .size import Size
from .translation import Translation

__all__ = [
    "Category",
    "FnacProduct",
    "FnacRange",
    "update_inventory",
    "Size",
    "Translation",
]
