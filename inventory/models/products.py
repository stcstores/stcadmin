"""Models for products."""

import random
import string

from ccapi import CCAPI
from django.db import models

from .product_options import Department

UNIQUE_SKU_ATTEMPTS = 100


def generate_SKU():
    """Return a Product SKU."""
    pass

    def get_character_block():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return "_".join((get_character_block() for _ in range(3)))


def unique_SKU(existing_SKUs, SKU_function):
    """Generate a unique SKU."""
    remaining_attempts = UNIQUE_SKU_ATTEMPTS
    while True:
        SKU = SKU_function()
        if SKU not in existing_SKUs:
            return SKU
        if remaining_attempts == 0:
            raise Exception(
                f"Did not generate a unique SKU in {UNIQUE_SKU_ATTEMPTS} attemtps."
            )


class ProductRange(models.Model):
    """Model for Product Ranges."""

    range_ID = models.CharField(max_length=50, db_index=True, unique=True)
    SKU = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    end_of_line = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    class Meta:
        """Meta class for Warehouse."""

        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"

    def __str__(self):
        return f"{self.SKU} - {self.name}"

    @classmethod
    def get_new_SKU(cls):
        """Return an unused Range SKU."""
        existing_SKUs = cls._base_manager.values_list("SKU", flat=True)
        return unique_SKU(existing_SKUs, cls.generate_SKU)

    @staticmethod
    def generate_SKU():
        """Return a Product Range SKU."""
        return f"RNG_{generate_SKU()}"

    def clean(self, *args, **kwargs):
        """Save the model instance."""
        if not self.SKU:
            self.SKU = self.get_new_SKU()
        if not self.range_ID:
            self.range_ID = self.create_CC_range()
        super().clean(*args, **kwargs)

    def create_CC_range(self):
        """Create a new Product Range in Cloud Commerce."""
        return CCAPI.create_range(self.name, sku=self.SKU)
